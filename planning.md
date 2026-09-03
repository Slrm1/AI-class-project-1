# Planning — The Unofficial Howard CS Guide

> Working plan for the first production AI project. Review the factual details and evaluation judgments before submission.

## Domain

Howard University Computer Science student-facing information. The goal is to make useful academic, research, advising, career, internship, and student-community information searchable through natural-language questions.

## Documents

The `data/` folder contains 12 curated plain-text source documents. Each document records a source URL. The current collection is primarily official Howard University material. Because the assignment emphasizes student-generated knowledge, the final version should be supplemented with genuinely student-created notes, interviews, or publicly available student perspectives if those materials are permitted by the instructor.

## Chunking Strategy

- Chunk size: approximately 700 characters
- Overlap: 120 characters
- Prefer paragraph boundaries
- Normalize whitespace and remove excessive blank lines before chunking

The overlap helps preserve context when a relevant statement falls near a boundary. The target is 50–2,000 chunks.

## Retrieval Approach

Use `sentence-transformers/all-MiniLM-L6-v2` for dense embeddings and ChromaDB as the persistent local vector store. Retrieve the top 5 chunks for each query and inspect distances and source relevance during evaluation.

The embedding model is lightweight and fast, making it practical for local student development. A production system could compare larger embedding models for semantic recall while measuring latency, memory, cost, and index size.

## Generation

The LLM receives only the retrieved chunks as context. The system prompt explicitly prohibits using outside knowledge and instructs the model to refuse unsupported questions. Responses include source-file attribution, while the interface also displays the retrieved sources and distances.

## Evaluation Plan

1. **What credit-hour requirement does Howard's BS in Computer Science have?**
   - Expected: At least 120 credit hours.
2. **What topics are covered in CSCI 354?**
   - Expected: The topics listed in the CSCI 354 source document, including advanced data structures and algorithm-related material.
3. **Who are the Computer Science academic advisors listed for A-K and L-Z?**
   - Expected: The advisors listed in the advising source document.
4. **What internship resources are available through Howard's undergraduate resources?**
   - Expected: The resources documented in the internship source document, including Handshake opportunities, externships, and micro-internships where supported by the source.
5. **What are some research areas in Howard EECS?**
   - Expected: Several areas listed in the research source documents, such as AI/ML, cybersecurity, HCI, networking, software engineering, databases/data visualization, distributed systems, and gaming.

### Out-of-scope test

Ask: `What is the weather in Washington, DC tomorrow?` The system should refuse because weather information is not part of the knowledge base.

## Anticipated Challenges

- University pages can change over time.
- Source documents vary in length and structure.
- Similar questions can retrieve overlapping chunks.
- An LLM may try to answer from general knowledge, so generation must remain grounded in retrieved context.
- API keys must remain outside GitHub.
- Student-generated knowledge must be clearly distinguished from official university information.

## AI Tool Plan

AI tools are being used to help implement and debug the retrieval pipeline, improve prompt design, scaffold the interface, and pressure-test evaluation. The student should review source selection, factual accuracy, evaluation judgments, and the final submission.

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
