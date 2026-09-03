# The Unofficial Howard CS Guide

A Retrieval-Augmented Generation (RAG) project that makes curated Howard University Computer Science information searchable through natural-language questions.

## What It Does

1. Loads source documents from `data/`.
2. Cleans and chunks the documents with overlap.
3. Embeds each chunk with `all-MiniLM-L6-v2`.
4. Stores embeddings in ChromaDB.
5. Retrieves the 5 most relevant chunks for a question.
6. Uses a Groq-hosted LLM to answer only from retrieved context.
7. Shows source files and retrieval distances with every answer.

## Domain

The knowledge base focuses on Howard CS academics, courses, advising, research, career resources, internships, and student opportunities.

## Data

There are currently 12 curated `.txt` source documents in `data/`. Each includes its source URL. The sources are primarily official Howard University pages plus a Howard University Magazine article.

## Chunking Strategy

The pipeline uses approximately 700-character chunks with 120-character overlap. Paragraph boundaries are preferred. The overlap preserves context across boundaries while keeping retrieval units small enough to be focused.

## Embedding + Vector Store

Embedding model: `sentence-transformers/all-MiniLM-L6-v2`.

ChromaDB is used as the local persistent vector database. The model is lightweight and fast for a student project. A production system could compare larger embedding models for semantic recall while measuring latency, memory use, cost, and index size.

## Setup

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file or export `GROQ_API_KEY` in your shell. Do not commit the key.

## Build the Index

```bash
python ingest.py
```

This prints the number of indexed chunks and five sample chunks for inspection.

## Run the CLI

```bash
python query.py
```

## Run the Gradio Interface

```bash
python app.py
```

## Evaluation Questions

| Question | Expected answer |
|---|---|
| What credit-hour requirement does Howard's BS in Computer Science have? | At least 120 credit hours. |
| What topics are covered in CSCI 354? | Advanced data structures, algorithms, efficiency, trees, graphs, indexing, and search. |
| Who advises CS students for last names A-K and L-Z? | Ladan Johnson for A-K; Bobbi Harewood for L-Z. |
| What internship resources are available? | Handshake opportunities, externships, and micro-internships. |
| What are some EECS research areas? | AI/ML, cybersecurity, HCI, networking, software engineering, databases/data visualization, distributed systems, gaming, and more. |

## Out-of-Scope Behavior

For questions not supported by the knowledge base, the assistant is instructed to refuse rather than invent an answer. Example: `What is the weather in Washington, DC tomorrow?`

## Failure Analysis

A likely failure mode is retrieval of a related but insufficient chunk. For example, a broad question about every Computer Science elective could retrieve only a subset of course descriptions. The system should not treat that subset as a complete catalog. This is why evaluation includes checking the retrieved chunks and source distances instead of judging only the generated text.

## Spec Reflection

### What worked

The RAG pipeline separates ingestion, retrieval, and generation. Source metadata makes it possible to show where an answer came from.

### What could improve

The current system uses dense semantic search only. Hybrid keyword + semantic retrieval, metadata filters, and a comparison of chunk sizes would be useful next steps.

### Stretch Goals

- Hybrid search
- Compare multiple chunking strategies
- Metadata filtering by topic/source
- Conversational memory

## AI Usage

AI assistance was used to help implement and debug the RAG pipeline, prompt design, interface scaffolding, and documentation. Source selection, factual review, evaluation judgments, and final submission should be reviewed by the student.

## Architecture

```text
Document Ingestion → Cleaning/Chunking → Embedding + ChromaDB → Retrieval → Grounded Generation + Sources
```
