import json
import math
import sqlite3
from .ingest import documents


def connect(config):
    config.database.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(config.database)
    db.row_factory = sqlite3.Row
    db.execute("CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS chunks (id INTEGER PRIMARY KEY, source TEXT, digest TEXT, location TEXT, text TEXT, vector TEXT)")
    return db


def ingest(config, client):
    digest = client.model_digest(config.embedding_model)
    rows = []
    for chunk in documents(config):
        vector = client.embed(config.embedding_model, chunk["text"])
        if rows and len(vector) != len(json.loads(rows[0][-1])):
            raise ValueError("Embedding dimension changed")
        rows.append((chunk["source"], chunk["digest"], chunk["location"],
                     chunk["text"], json.dumps(vector)))
    if not rows:
        raise ValueError("No indexable text; existing index preserved")
    if client.model_digest(config.embedding_model) != digest:
        raise ValueError("Embedding model changed during ingestion")
    db = connect(config)
    try:
        with db:
            db.execute("DELETE FROM chunks")
            db.executemany("INSERT INTO chunks(source,digest,location,text,vector) VALUES(?,?,?,?,?)", rows)
            db.execute("DELETE FROM metadata")
            db.executemany("INSERT INTO metadata VALUES(?,?)", [
                ("embedding_model", config.embedding_model), ("embedding_digest", digest),
                ("dimension", str(len(json.loads(rows[0][-1])))),
                ("chunk_size", str(config.chunk_size)), ("overlap", str(config.overlap))])
    finally:
        db.close()
    return len(rows)


def cosine(a, b):
    if len(a) != len(b):
        raise ValueError("Embedding dimensions differ; rebuild index")
    denominator = math.sqrt(sum(x*x for x in a) * sum(x*x for x in b))
    return sum(x*y for x, y in zip(a, b)) / denominator if denominator else 0


def retrieve(config, client, question):
    if not config.database.exists():
        raise ValueError("Index missing; run ingest")
    db = connect(config)
    try:
        metadata = dict(db.execute("SELECT key,value FROM metadata").fetchall())
        if (metadata.get("embedding_model") != config.embedding_model
                or metadata.get("embedding_digest") != client.model_digest(config.embedding_model)):
            raise ValueError("Embedding model changed; rebuild index")
        vector = client.embed(config.embedding_model, question)
        ranked = []
        for row in db.execute("SELECT * FROM chunks"):
            chunk = dict(row)
            chunk["score"] = cosine(vector, json.loads(chunk.pop("vector")))
            if chunk["score"] >= config.min_score:
                ranked.append(chunk)
        return sorted(ranked, key=lambda c: (-c["score"], c["id"]))[:config.top_k]
    finally:
        db.close()


def reset(config):
    if not config.database.exists():
        return
    db = connect(config)
    try:
        db.execute("PRAGMA secure_delete=ON")
        with db:
            db.execute("DELETE FROM chunks")
            db.execute("DELETE FROM metadata")
        db.execute("VACUUM")
    finally:
        db.close()
