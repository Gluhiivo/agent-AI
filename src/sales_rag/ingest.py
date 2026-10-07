import hashlib
from pathlib import Path


def documents(config):
    root = config.input_dir.resolve()
    if not root.is_dir():
        raise ValueError("Input directory does not exist")
    paths = sorted(root.rglob("*"))
    for path in paths:
        if path.is_symlink() or any(p.is_symlink() for p in path.parents if p != root):
            raise ValueError("Symbolic links are forbidden")
        if not path.is_file():
            continue
        if not path.resolve().is_relative_to(root):
            raise ValueError("File outside input directory")
        if path.suffix.lower() not in (".md", ".txt", ".pdf"):
            raise ValueError("Unsupported input format")
        if path.stat().st_size > config.max_file_bytes:
            raise ValueError("Input file exceeds size limit")
        with path.open("rb") as handle:
            raw = handle.read(config.max_file_bytes + 1)
        if len(raw) > config.max_file_bytes:
            raise ValueError("Input file exceeds size limit")
        digest = hashlib.sha256(raw).hexdigest()
        name = path.relative_to(root).as_posix()
        if path.suffix.lower() == ".pdf":
            from io import BytesIO
            try:
                from pypdf import PdfReader
            except ImportError as exc:
                raise ValueError("Install the pdf extra to read PDF files") from exc
            reader = PdfReader(BytesIO(raw))
            if reader.is_encrypted:
                raise ValueError("Encrypted PDF is unsupported")
            sections = [(f"page {i + 1}", page.extract_text() or "")
                        for i, page in enumerate(reader.pages)]
            if not sections or any(not text.strip() for _, text in sections):
                raise ValueError("PDF has an empty text page; OCR/manual review required")
        else:
            sections = [("text", raw.decode("utf-8"))]
        for location, text in sections:
            for offset in range(0, len(text), config.chunk_size - config.overlap):
                chunk = text[offset:offset + config.chunk_size].strip()
                if chunk:
                    yield {"source": name, "digest": digest,
                           "location": f"{location}, chars {offset}-{min(offset + config.chunk_size, len(text))}",
                           "text": chunk}
