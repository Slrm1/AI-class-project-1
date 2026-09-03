# Planning — The Unofficial Howard CS Guide

> Draft planning document. Review and adjust before final submission.

## Domain

Howard University Computer Science student-facing information. The goal is to make useful academic, research, advising, career, and student-community information searchable through natural-language questions.

## Documents

The `data/` folder contains 12 curated plain-text source documents. Sources are primarily Howard University pages, with one Howard Magazine article. Each document records its source URL so answers can be attributed.

## Chunking Strategy

- Chunk size: about 700 characters
- Overlap: 120 characters
- Split on paragraph/sentence boundaries when possible
- Remove repeated whitespace and blank lines during preprocessing

The overlap helps preserve context when an important sentence falls near a chunk boundary. The target is a few hundred chunks rather than a very large index.

## Retrieval Approach

Use `sentence-transformers/all-MiniLM-L6-v2` to create dense embeddings and ChromaDB as the local vector store. Queries retrieve the top 5 most similar chunks. Similarity results are inspected during evaluation to check whether the retrieved context actually supports the answer.

The embedding model is small and fast, which is useful for a student project and local development. A production system could compare larger embedding models for better semantic recall, while considering latency, memory, cost, and embedding dimensionality.

## Evaluation Plan

1. **What credit-hour requirement does Howard's BS in Computer Science have?**
   - Expected: At least 120 credit hours.
2. **What topics are covered in CSCI 354?**
   - Expected: Advanced data structures, algorithm design, efficiency/complexity, trees, graphs, indexing, and search.
3. **Who are the Computer Science academic advisors listed by Howard for A-K and L-Z last names?**
   - Expected: Ladan Johnson for A-K and Bobbi Harewood for L-Z.
4. **What internship resources does Howard provide through its Office of Undergraduate Studies?**
   - Expected: Handshake opportunities, externships, and micro-internships; micro-internships are short-term paid professional assignments.
5. **What are some research areas in Howard EECS?**
   - Expected: AI/ML, cybersecurity, HCI, networking, software engineering, databases/data visualization, distributed systems, gaming, and other listed areas.

### Out-of-scope test

Ask a question unrelated to the documents, such as: `What is the weather in Washington, DC tomorrow?` The system should say that the answer is not supported by the available Howard CS knowledge base instead of inventing an answer.

## Anticipated Challenges

- Public university pages may change over time.
- Source documents have different writing styles and lengths.
- Similar questions can retrieve overlapping chunks.
- The LLM may try to answer from its general knowledge, so the prompt must explicitly restrict it to retrieved context.
- API keys and local environment setup must not be committed.

## AI Tool Plan

AI tools are used to help implement and debug the retrieval pipeline, improve prompts, inspect retrieval failures, and generate a basic interface. Human review is required for the source documents, evaluation answers, and final README/reflection.

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
