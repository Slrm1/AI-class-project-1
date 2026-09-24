"""Load, clean, chunk, embed, and index the unofficial Howard CS corpus."""

from pathlib import Path
import html
import re

DATA_DIR = Path("data")
DB_DIR = "chroma_db"
COLLECTION_NAME = "howard_cs_guide"
MODEL_NAME = "all-MiniLM-L6-v2"
# One review or comment per chunk, up to this size. See planning.md.
CHUNK_SIZE = 720
OVERLAP = 100


def clean_text(text: str) -> str:
    text = html.unescape(text)
    text = text.replace("\u200b", "").replace("\xa0", " ")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _split_sentences(paragraph: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", paragraph.strip())
    return [p.strip() for p in parts if p.strip()]


def _overlap_start(text: str, end: int, overlap: int) -> int:
    """Start the overlap on a word boundary so chunks do not begin mid-word."""
    start = max(end - overlap, 0)
    if start == 0:
        return 0
    space = text.find(" ", start, end)
    if space != -1 and space + 1 < end:
        return space + 1
    return start


def _window(text: str, size: int, overlap: int) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(text):
            break
        nxt = _overlap_start(text, end, overlap)
        start = nxt if nxt > start else start + 1
    return chunks


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> list[str]:
    """One chunk per paragraph when the paragraph fits in `size`.

    A review or a student comment is the unit retrieval needs. Packing the
    page header onto the first review pushed "exams follow the homework" into
    the next chunk, and that chunk then lost the search. Paragraphs longer
    than `size` are split on sentences with a word-aligned overlap.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    for paragraph in paragraphs:
        if len(paragraph) <= size:
            if len(paragraph) < 80 and chunks:
                chunks[-1] = f"{chunks[-1]}\n\n{paragraph}"
            else:
                chunks.append(paragraph)
            continue

        sentence_buf = ""
        parts: list[str] = []
        for sentence in _split_sentences(paragraph):
            if len(sentence) > size:
                if sentence_buf:
                    parts.append(sentence_buf.strip())
                    sentence_buf = ""
                parts.extend(_window(sentence, size, overlap))
                continue
            candidate = f"{sentence_buf} {sentence}".strip() if sentence_buf else sentence
            if len(candidate) <= size:
                sentence_buf = candidate
            else:
                parts.append(sentence_buf.strip())
                tail_at = _overlap_start(sentence_buf, len(sentence_buf), overlap)
                tail = sentence_buf[tail_at:].strip()
                sentence_buf = f"{tail} {sentence}".strip() if tail else sentence
        if sentence_buf:
            parts.append(sentence_buf.strip())
        chunks.extend(parts)

    return [c for c in chunks if len(c) > 40]


def _header_value(text: str, label: str) -> str:
    prefix = f"{label}:"
    for line in text.splitlines():
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip()
    return ""


def body_text(text: str) -> str:
    """Drop the source header. URL and type are stored as chunk metadata."""
    kept = []
    for line in text.splitlines():
        if line.startswith(("Source:", "URL:", "Type:")):
            continue
        kept.append(line)
    return "\n".join(kept).strip()


def representative_chunks(records: list[dict], n: int = 5) -> list[dict]:
    """First full chunk from several files, skipping overlap fragments."""
    by_file: dict[str, list[dict]] = {}
    for record in records:
        by_file.setdefault(record["source_file"], []).append(record)
    picked = []
    for records_for_file in by_file.values():
        ordered = sorted(records_for_file, key=lambda r: r["chunk"])
        choice = ordered[0]
        for record in ordered:
            text = record["text"].lstrip()
            if text[:1].isupper() and len(text) >= 200:
                choice = record
                break
        picked.append(choice)
        if len(picked) == n:
            break
    return picked


def main():
    import chromadb
    from sentence_transformers import SentenceTransformer

    files = sorted(DATA_DIR.glob("*.txt"))
    if not files:
        raise SystemExit("No .txt files found in data/")

    model = SentenceTransformer(MODEL_NAME)
    client = chromadb.PersistentClient(path=DB_DIR)
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.get_or_create_collection(
        COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    documents, metadatas, ids = [], [], []
    records = []
    for path in files:
        text = clean_text(path.read_text(encoding="utf-8"))
        source_url = _header_value(text, "URL")
        source_type = _header_value(text, "Type") or "unknown"
        for i, chunk in enumerate(chunk_text(body_text(text))):
            documents.append(chunk)
            meta = {
                "source_file": path.name,
                "source_url": source_url,
                "source_type": source_type,
                "chunk": i,
            }
            metadatas.append(meta)
            ids.append(f"{path.stem}-{i}")
            records.append({"text": chunk, **meta})

    embeddings = model.encode(documents, normalize_embeddings=True).tolist()
    collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)

    print(f"Indexed {len(files)} documents into {len(documents)} chunks.")
    print(f"Chunk size {CHUNK_SIZE}, overlap {OVERLAP}.")
    samples = representative_chunks(records)
    print("\nSample chunks:")
    for i, sample in enumerate(samples, 1):
        print(f"\n--- Chunk {i} | {sample['source_file']} ---\n{sample['text']}")


if __name__ == "__main__":
    main()
