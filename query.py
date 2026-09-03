import os

import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq

DB_DIR = "chroma_db"
COLLECTION_NAME = "howard_cs_guide"
MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 5

FALLBACK = "I don't have enough information in the Howard CS knowledge base to answer that."

SYSTEM_PROMPT = """You are a grounded assistant for The Unofficial Howard CS Guide.
Answer ONLY from the retrieved context below. If the context does not support the answer, say exactly:
I don't have enough information in the Howard CS knowledge base to answer that.
Do not use outside knowledge to fill gaps. Keep answers concise. Do not invent facts, names, dates, or URLs.
When answering, include a short Sources section listing the source file(s) used.

RETRIEVED CONTEXT:
{context}
"""


def retrieve(question: str, k: int = TOP_K):
    model = SentenceTransformer(MODEL_NAME)
    client = chromadb.PersistentClient(path=DB_DIR)
    collection = client.get_collection(COLLECTION_NAME)
    embedding = model.encode([question], normalize_embeddings=True).tolist()
    result = collection.query(query_embeddings=embedding, n_results=k, include=["documents", "metadatas", "distances"])
    docs = result["documents"][0]
    metas = result["metadatas"][0]
    distances = result["distances"][0]
    return list(zip(docs, metas, distances))


def answer(question: str):
    if not question.strip():
        return "Please enter a question.", []
    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError("Set GROQ_API_KEY before asking questions.")

    results = retrieve(question)
    context_parts = []
    for i, (doc, meta, distance) in enumerate(results, 1):
        context_parts.append(
            f"[Chunk {i} | {meta['source_file']} | URL: {meta.get('source_url', '')} | distance={distance:.4f}]\n{doc}"
        )
    context = "\n\n".join(context_parts)

    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    response = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.format(context=context)},
            {"role": "user", "content": question},
        ],
        temperature=0,
    )
    return response.choices[0].message.content, results


if __name__ == "__main__":
    question = input("Ask the Howard CS Guide: ")
    response, results = answer(question)
    print("\n" + response)
    print("\nRetrieved sources:")
    for _, meta, distance in results:
        print(f"- {meta['source_file']} | {meta.get('source_url', '')} | distance {distance:.4f}")
