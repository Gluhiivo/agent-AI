# Architecture decision record 001

Status: proposed implementation for M1; real model acceptance pending.

Use a Python CLI and SQLite with JSON vectors instead of LanceDB. For ~5 documents,
brute-force cosine ranking simplifies installation, transactions and inspection.
This is not intended for large corpora. Reconsider at measured scale/performance limits.

Ollama is the only runtime network adapter. It uses /api/tags to check local model
availability and embedding digest, /api/embed for embeddings, /api/generate for JSON
answers. No pulling, tools, proxy, redirects or cloud fallback. Client errors fail closed.
The external Ollama service requires independent network controls.

Ingestion: supported files -> page/text offsets -> SHA-256 source hash -> overlapping
character chunks -> embeddings -> atomic full index replacement. Characters are not
tokens; Ollama truncation is disabled to surface oversized embedding inputs.
Model digest changes require rebuilding the index. Context limits still depend on model
and local Ollama configuration. Adjust chunk_size/top_k after measuring.

Answers: retrieved IDs only; each claim requires valid citations. Structural validation
is deterministic, semantic entailment is not. Human review and empirical abstention
evaluation are required. No reranker, hybrid search, ACL, OCR or fine-tuning in M1.
