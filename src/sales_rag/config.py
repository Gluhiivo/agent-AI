from dataclasses import dataclass
from pathlib import Path
import tomllib
from urllib.parse import urlsplit


def validate_endpoint(endpoint):
    url = urlsplit(endpoint)
    if (url.scheme != "http" or url.hostname != "127.0.0.1"
            or url.username or url.password or url.path not in ("", "/")
            or url.query or url.fragment or not url.port):
        raise ValueError("Endpoint must be http://127.0.0.1:<port>")
    return endpoint.rstrip("/")


@dataclass(frozen=True)
class Config:
    input_dir: Path
    database: Path
    endpoint: str = "http://127.0.0.1:11434"
    embedding_model: str = "bge-m3:latest"
    generation_model: str = "qwen3:4b"
    chunk_size: int = 1200
    overlap: int = 150
    top_k: int = 5
    min_score: float = 0.55
    max_file_bytes: int = 10485760

    def __post_init__(self):
        validate_endpoint(self.endpoint)
        if not 0 <= self.overlap < self.chunk_size <= 10000:
            raise ValueError("Invalid chunk size/overlap")
        if not 1 <= self.top_k <= 20 or not 0 <= self.min_score <= 1:
            raise ValueError("Invalid retrieval settings")
        if not 1 <= self.max_file_bytes <= 104857600:
            raise ValueError("Invalid file limit")
        root = self.input_dir.resolve()
        if self.database.resolve().is_relative_to(root):
            raise ValueError("Database must be outside input_dir")


def load(path):
    path = Path(path).resolve()
    with path.open("rb") as handle:
        values = tomllib.load(handle)
    for key in ("input_dir", "database"):
        values[key] = (path.parent / values[key]).resolve()
    return Config(**values)
