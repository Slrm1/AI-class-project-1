# The Unofficial Howard CS Guide

A Retrieval-Augmented Generation (RAG) application for asking natural-language questions about a curated Howard University Computer Science knowledge base.

> **Submission note:** The repository contains the working pipeline and curated source corpus. Before submitting, review the sources and add any required student-generated material specified by the instructor. The evaluation table should contain the actual results from your run, not assumed results.

## Project Goal

Students often have to search across multiple pages to find information about courses, advising, research, internships, and student opportunities. This project combines document retrieval with an LLM so users can ask questions in plain language and receive answers grounded in the retrieved documents.

## Features

- Ingests multiple `.txt` source documents.
- Cleans and normalizes source text.
- Chunks documents using a deliberate size/overlap strategy.
- Generates dense embeddings with `all-MiniLM-L6-v2`.
- Stores embeddings and metadata in ChromaDB.
- Retrieves the top 5 relevant chunks.
- Sends only retrieved context to the LLM.
- Refuses questions that are not supported by the knowledge base.
- Displays source files and retrieval distances.
- Provides both a command-line interface and Gradio web interface.

## Domain

The knowledge base focuses on Howard CS academics, courses, advising, research, career resources, internships, and student opportunities.

## Repository Structure

```text
AI-class-project-1/
├── data/                  # Curated source documents
├── ingest.py              # Cleaning, chunking, embedding, indexing
├── query.py               # Retrieval + grounded generation
├── app.py                 # Gradio interface
├── planning.md            # Project plan and architecture
├── requirements.txt       # Python dependencies
├── .env.example           # Environment-variable template
├── .gitignore             # Prevents secrets/index files from being committed
└── README.md
```

## Data Sources

There are currently 12 curated plain-text source documents in `data/`. Each document includes its source URL. The current collection is primarily official Howard University material. If the course rubric requires student-generated knowledge, student-created notes/interviews or instructor-approved public student perspectives should be added and clearly labeled before final submission.

## Chunking Strategy

- **Chunk size:** approximately 700 characters
- **Overlap:** 120 characters
- **Boundary:** paragraph boundaries are preferred
- **Preprocessing:** normalize whitespace and remove excessive blank lines

The overlap helps preserve context when relevant information falls near a chunk boundary. The ingestion script prints five sample chunks so the chunking can be inspected manually.

## Embeddings + Vector Store

**Embedding model:** `sentence-transformers/all-MiniLM-L6-v2`

**Vector store:** ChromaDB with persistent local storage.

`all-MiniLM-L6-v2` is small and fast, which makes it appropriate for a student project. A production system could test larger embedding models for improved semantic recall while comparing latency, memory usage, cost, and index size.

## Retrieval

For each question, the system embeds the query and retrieves the **top 5** most similar chunks. The retrieved documents include metadata for the original source file and URL. Retrieval distances are displayed for evaluation and debugging.

## Grounded Generation

The LLM is explicitly instructed to answer only from the retrieved context. If the retrieved context does not support the answer, it must refuse rather than fill gaps using general knowledge. Source-file names are required in the generated response, and the interface separately displays the retrieved sources.

## Setup

### 1. Create a virtual environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the API key

Copy `.env.example` to `.env` and add your Groq API key, or set `GROQ_API_KEY` in your shell. **Never commit the API key.**

### 4. Build the vector index

```bash
python ingest.py
```

The script reports the number of source documents and chunks and prints five sample chunks for inspection.

### 5. Run the CLI

```bash
python query.py
```

### 6. Run the web interface

```bash
python app.py
```

## Evaluation

Run all five questions and record the actual response, whether it is correct, and the retrieved sources. Do not mark a response correct simply because the wording sounds plausible; verify it against the expected answer and source documents.

| # | Evaluation question | Expected answer | Actual response | Judgment |
|---|---|---|---|---|
| 1 | What credit-hour requirement does Howard's BS in Computer Science have? | At least 120 credit hours. | **Run and record here.** | **Run and judge.** |
| 2 | What topics are covered in CSCI 354? | The topics documented in the CSCI 354 source. | **Run and record here.** | **Run and judge.** |
| 3 | Who are the Computer Science academic advisors listed for A-K and L-Z? | The advisors documented in the advising source. | **Run and record here.** | **Run and judge.** |
| 4 | What internship resources are available through Howard's undergraduate resources? | The resources documented in the internship source. | **Run and record here.** | **Run and judge.** |
| 5 | What are some research areas in Howard EECS? | Several areas documented in the research sources. | **Run and record here.** | **Run and judge.** |

### Out-of-scope test

Question:

```text
What is the weather in Washington, DC tomorrow?
```

Expected behavior: the assistant should state that the information is not supported by the Howard CS knowledge base rather than inventing a weather forecast.

## Failure Analysis

One anticipated failure is a broad question retrieving only a subset of a larger course or program topic. In that case, the generated answer may be incomplete even if every retrieved chunk is individually relevant. The evaluation should document at least one real failure or limitation observed during testing and explain whether the problem came from retrieval, chunking, source coverage, or generation.

## Spec Reflection

### What worked

The pipeline separates ingestion, retrieval, and generation. Metadata preserves source information, and the grounded prompt reduces unsupported answers.

### What could improve

The current system uses dense semantic retrieval only. Hybrid keyword + semantic search, metadata filters, reranking, and chunk-size comparisons could improve retrieval quality.

### Stretch Goals

- Hybrid search
- Compare multiple chunking strategies
- Metadata filtering
- Conversational memory
- Retrieval reranking

## AI Usage

AI assistance was used for implementation support, debugging, prompt design, interface scaffolding, and documentation support. Source selection, factual verification, evaluation judgments, and final submission review remain the student's responsibility.

## Architecture

```text
Document Ingestion
        ↓
Cleaning + Chunking
        ↓
Embedding + ChromaDB Vector Store
        ↓
Top-k Semantic Retrieval
        ↓
Grounded LLM Generation + Source Attribution
```

## Limitations

This is a small educational RAG system, not an authoritative university advising service. Source pages may change, the corpus is limited, and retrieval can miss relevant information. Users should verify important academic or administrative information with official Howard University resources.
