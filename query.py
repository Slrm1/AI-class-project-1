"""Retrieve chunks and generate an answer grounded only in those chunks."""

import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

load_dotenv(Path(__file__).resolve().parent / ".env")

DB_DIR = "chroma_db"
COLLECTION_NAME = "howard_cs_guide"
MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 4
# Cosine distance. On-topic hits in this corpus land around 0.20–0.45.
# Weather and other off-topic queries land above 0.75. Refuse before the LLM
# sees a context set whose best match is that weak.
MAX_DISTANCE = 0.65
REFUSAL = "I don't have enough information in the collected Howard CS student documents to answer that."

SYSTEM_PROMPT = """You answer questions for The Unofficial Howard CS Guide.
You must use ONLY the retrieved context below. Do not use outside knowledge, even if you think you know the answer.
If the context does not contain enough information to answer, reply with exactly this sentence and nothing else:
I don't have enough information in the collected Howard CS student documents to answer that.
Do not invent professor names, course facts, ratings, or dates that are not written in the context.
If reviews disagree, say that they disagree and name the course each review is about.
Do not declare a single winner when the context only mentions more than one person.
Keep the answer to a short paragraph. Mention the source file name for each fact you use.

RETRIEVED CONTEXT:
{context}
"""

_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def get_collection():
    client = chromadb.PersistentClient(path=DB_DIR)
    return client.get_collection(COLLECTION_NAME)


def retrieve(question: str, k: int = TOP_K, source_type: str | None = None):
    model = get_model()
    collection = get_collection()
    embedding = model.encode([question], normalize_embeddings=True).tolist()
    kwargs = {
        "query_embeddings": embedding,
        "n_results": k,
        "include": ["documents", "metadatas", "distances"],
    }
    if source_type in {"reddit", "rmp"}:
        kwargs["where"] = {"source_type": source_type}
    result = collection.query(**kwargs)
    docs = result["documents"][0] if result["documents"] else []
    metas = result["metadatas"][0] if result["metadatas"] else []
    distances = result["distances"][0] if result["distances"] else []
    return list(zip(docs, metas, distances))


def _format_context(results) -> str:
    parts = []
    for i, (doc, meta, distance) in enumerate(results, 1):
        parts.append(
            f"[Chunk {i} | file: {meta['source_file']} | type: {meta.get('source_type', '')} "
            f"| distance: {distance:.4f}]\n{doc}"
        )
    return "\n\n".join(parts)


def source_names(results) -> list[str]:
    seen = []
    for _, meta, _ in results:
        name = meta["source_file"]
        if name not in seen:
            seen.append(name)
    return seen


def answer(question: str, source_type: str | None = None):
    if not question or not question.strip():
        return {"answer": "Please enter a question.", "sources": [], "results": []}

    results = retrieve(question, source_type=source_type)
    if not results or results[0][2] > MAX_DISTANCE:
        return {"answer": REFUSAL, "sources": [], "results": results}

    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError("Set GROQ_API_KEY in .env before asking questions.")

    context = _format_context(results)
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    response = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.format(context=context)},
            {"role": "user", "content": question.strip()},
        ],
        temperature=0,
    )
    text = (response.choices[0].message.content or "").strip()
    sources = source_names(results)
    # Attribution is attached in code so a citation survives even if the model omits one.
    cited = "\n".join(f"- {name}" for name in sources)
    if "Sources:" not in text:
        text = f"{text}\n\nSources:\n{cited}"
    return {"answer": text, "sources": sources, "results": results}


if __name__ == "__main__":
    question = input("Ask the Unofficial Howard CS Guide: ")
    result = answer(question)
    print("\n" + result["answer"])
    print("\nRetrieved chunks:")
    for doc, meta, distance in result["results"]:
        preview = doc.replace("\n", " ")[:180]
        print(f"- {meta['source_file']} | {distance:.4f} | {preview}")
