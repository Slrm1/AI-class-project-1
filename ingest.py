from pathlib import Path
import re

import chromadb
from sentence_transformers import SentenceTransformer

DATA_DIR = Path("data")
DB_DIR = "chroma_db"
COLLECTION_NAME = "howard_cs_guide"
MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_SIZE = 700
OVERLAP = 120


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = OVERLAP):
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""

    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}" if current else paragraph
        if len(candidate) <= size:
            current = candidate
            continue

        if current:
            chunks.append(current.strip())
            tail = current[-overlap:]
            current = f"{tail}\n\n{paragraph}" if len(tail) else paragraph
        else:
            start = 0
            while start < len(paragraph):
                end = min(start + size, len(paragraph))
                chunks.append(paragraph[start:end].strip())
                if end >= len(paragraph):
                    break
                start = max(end - overlap, start + 1)
            current = ""

    if current:
        chunks.append(current.strip())
    return [c for c in chunks if c]


def main():
    files = sorted(DATA_DIR.glob("*.txt"))
    if not files:
        raise SystemExit("No .txt files found in data/")

    model = SentenceTransformer(MODEL_NAME)
    client = chromadb.PersistentClient(path=DB_DIR)
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.get_or_create_collection(COLLECTION_NAME)

    documents, metadatas, ids = [], [], []
    for path in files:
        text = clean_text(path.read_text(encoding="utf-8"))
        source = ""
        for line in text.splitlines():
            if line.startswith("URL:"):
                source = line.replace("URL:", "", 1).strip()
                break
        for i, chunk in enumerate(chunk_text(text)):
            documents.append(chunk)
            metadatas.append({"source_file": path.name, "source_url": source, "chunk": i})
            ids.append(f"{path.stem}-{i}")

    embeddings = model.encode(documents, normalize_embeddings=True).tolist()
    collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)

    print(f"Indexed {len(files)} documents into {len(documents)} chunks.")
    print("Sample chunks:")
    for i, chunk in enumerate(documents[:5], 1):
        print(f"\n--- Sample {i} ---\n{chunk}")


if __name__ == "__main__":
    main()
