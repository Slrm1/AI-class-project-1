# The Unofficial Howard CS Guide

A retrieval-augmented guide to what Howard University computer science students actually say about courses, professors, registration, and internships. Ask a plain-language question and the system answers from retrieved posts and reviews, with the source file named in the response.

Demo video: [3–5 minute demo](20260924-0236-10.9956642.mp4)

## Project Goal

Official pages list course titles and credit hours. They do not say that Computer Organization is the semester that uses MIPS, that BisonHub hides registration behind an orange “register from plan” button, or that one professor’s CSCI 135 reviews and CSCI 454 review describe different classes. That advice is scattered across r/HowardUniversity and Rate My Professors. This system makes those pages searchable.

## Features

- Loads 16 local `.txt` documents collected from public threads and review pages.
- Cleans HTML entities and whitespace, then drops the `Source` / `URL` / `Type` header from the embedded text (those values are stored as metadata).
- Chunks on paragraph boundaries at 720 characters, with a 100-character overlap only when a paragraph is longer than that.
- Embeds chunks with `all-MiniLM-L6-v2` and stores them in a local ChromaDB collection using cosine distance.
- Retrieves the top 4 chunks. A dropdown can limit that search to Reddit threads or Rate My Professors.
- Sends only those chunks to Groq. If the best cosine distance is worse than 0.65, the pipeline refuses before the model is called.
- Appends a source-file list in code, and shows the retrieved chunks and distances in a separate field.

## Domain

Unofficial Howard University computer science student knowledge: course workload, professor reviews, how registration actually works in BisonHub, advising, and internship paths students name to each other. Catalog copy does not carry this. It lives in threads and reviews a new student would not know to open, and the same professor is often praised in one course and criticized in another.

## Repository Structure

```text
AI-class-project-1-1/
├── data/                  # 16 plain-text source documents
├── ingest.py              # Clean, chunk, embed, index
├── query.py               # Retrieval, distance gate, grounded generation
├── app.py                 # Gradio interface
├── evaluate.py            # Runs the five test questions
├── planning.md            # Spec, including the metadata-filter stretch
├── requirements.txt
├── .env.example
└── README.md
```

## Data Sources

Sixteen documents in `data/`. Reddit text is from archived r/HowardUniversity threads (PullPush). Professor files are public Rate My Professors reviews saved as plain text because those pages are JavaScript-rendered and block a simple scrape. Each file records its URL.

| File | What it is | URL |
|---|---|---|
| `01_reddit_how_is_howard_cs.txt` | Teaching quality, Blackstone, Computer Organization professors, alumni network | https://www.reddit.com/r/HowardUniversity/comments/1cdwjwn/how_is_howard_university_for_computer_science/ |
| `02_reddit_csci136_topics.txt` | What CSCI-136 covers, and C++ vs Python | https://www.reddit.com/r/HowardUniversity/comments/kpqcf5/csci136_syllabus/ |
| `03_reddit_computer_organization.txt` | Computer Organization I and II, MIPS workload | https://www.reddit.com/r/HowardUniversity/comments/ll492a/computer_science_majors_how_hard_is_it/ |
| `04_reddit_bisonhub_registration.txt` | The orange “register from plan” button | https://www.reddit.com/r/HowardUniversity/comments/1dfhalm/registering_for_cs_courses/ |
| `05_reddit_cs_advisor.txt` | Ladan Johnson not answering email; do not wait for advisors | https://www.reddit.com/r/HowardUniversity/comments/1dfvnjh/compsci_advisor/ |
| `06_reddit_google_step_and_internships.txt` | Google STEP, Handshake, CEA fairs | https://www.reddit.com/r/HowardUniversity/comments/u7bhv8/q_a/ |
| `07_reddit_freshman_coursework.txt` | First-year Python and C++ labs, ALEKS, textbooks | https://www.reddit.com/r/HowardUniversity/comments/u7bhv8/q_a/ |
| `08_reddit_staying_in_cs.txt` | Corporate visits, Googler in Residence, self-teaching | https://www.reddit.com/r/HowardUniversity/comments/1cnaz8b/convince_me_to_remain_a_cs_major/ |
| `09_reddit_campus_wifi.txt` | Campus Wi-Fi outages | https://www.reddit.com/r/HowardUniversity/comments/y1nyek/wifi_at_howard/ |
| `10_reddit_switching_into_cs.txt` | Switching into CS, and Computer Information Systems as the alternative | https://www.reddit.com/r/HowardUniversity/comments/1cmpdea/rejected_from_major_switch/ |
| `11_rmp_jeremy_blackstone.txt` | CSCI 135 reviews and one CSCI 454 review | https://www.ratemyprofessors.com/professor/2640220 |
| `12_rmp_gloria_washington.txt` | Mixed CSCI 135 and CSCI 136 reviews | https://www.ratemyprofessors.com/professor/2084505 |
| `13_rmp_saurav_aryal.txt` | CSCI 135, 136, and 354 reviews | https://www.ratemyprofessors.com/professor/2672438 |
| `14_rmp_guy_lingani.txt` | CSCI 365 cloud computing elective | https://www.ratemyprofessors.com/professor/2992359 |
| `15_rmp_jiang_li.txt` | CSCI 201 and CSCI 453 reviews | https://www.ratemyprofessors.com/professor/2323879 |
| `16_rmp_noha_hazzazi.txt` | CSCI 120, 135, and 354 reviews | https://www.ratemyprofessors.com/professor/2418869 |

`05` also includes advising comments from https://www.reddit.com/r/HowardUniversity/comments/1l7ba0c/advsing/ and https://www.reddit.com/r/HowardUniversity/comments/1ecs231/cs_non_technical_elective_course/. `06` and `07` are two slices of one Q&A so internship facts and first-year labs are not forced into one document. The earlier official catalog files were removed from `data/` so they are not retrieved.

## Chunking Strategy

- **Chunk size:** 720 characters
- **Overlap:** 100 characters, used only when a paragraph is longer than 720, and snapped forward to a word boundary
- **Boundary:** one blank-line paragraph (one comment or one review) is one chunk when it fits. A fragment shorter than 80 characters is appended to the previous chunk.
- **Preprocessing:** HTML-unescape, collapse whitespace, drop the three header lines from the embedded text

These documents are short opinions. A review is often 400–600 characters once it includes the professor, the course, and the claim. The first setting in `planning.md` was 450 characters, and neighboring paragraphs were packed together until that cap. That split two facts the evaluation questions need. The MIPS sentence was cut off “Computer Organization,” and “Exams follow the homework structure” was cut off the March 26, 2026 Blackstone CSCI 135 review. The half that still contained the course name then lost to other chunks that only contained the word “difficulty.” 720 characters is about one review or one comment, so the name and the claim stay in the same embedding. Overlap still matters for the few comments longer than 720 (the advising note and one internship comment), where a sentence can sit on the cut.

`python ingest.py` indexed **16 documents into 78 chunks**, inside the 50–2,000 range.

## Sample Chunks

Each of these is one stored chunk. Paragraphs at or under 720 characters are stored whole.

**Chunk 1** — `02_reddit_csci136_topics.txt`

> Student reply: I took the class last semester as a computer science major. Depending on the professor and what section you registered for, CSCI-136 will be taught in either C++ or Python. It covers data structures and algorithms, such as but not limited to: using classes (object-oriented programming); linked lists (and vectors if you are in the C++ class); sorting algorithms; dictionaries and hash tables; trees, binary trees, and tree-traversal methods; and a huge emphasis on Big-O notation, runtime complexity, and space complexity.

**Chunk 2** — `03_reddit_computer_organization.txt`

> Student reply: It depends on what you define as hard. When I took my first CS class at Howard, I did not know how to code at all. My first semester was difficult, but my second semester was much easier. Computer Organization I and Computer Organization II are very difficult. The workload in both classes is tremendous, and learning how to code in any assembly language (we used MIPS) is ten times harder than coding in a high-level language such as C++, Python, or Java.

**Chunk 3** — `04_reddit_bisonhub_registration.txt`

> Student reply from Downtown_Ad5455: If you see an orange button that says register from plan, press that. If you do not see that button, it means you have not finished all of your onboarding tasks in BisonHub, and they will not let you register for classes until you do that.

**Chunk 4** — `05_reddit_cs_advisor.txt`

> Thread question from RepresentativeBaby19: Has anyone been able to get in contact with the computer science academic advisor LaDan Johnson? He has responded to zero emails. The student is trying to figure out how the first-semester schedule should look.

**Chunk 5** — `11_rmp_jeremy_blackstone.txt`

> Review of Professor Jeremy Blackstone, course CSCI 135, March 26, 2026. Quality 5.0. Difficulty 1.0. For credit, attendance not mandatory, would take again, grade A+, textbook N/A. Most simplistic and straightforward professor ever. All assignments (not many or difficult by any means) are posted at the beginning. You can work at your own pace while following along during lectures if needed. If you already know C++, this is like a review course. Exams follow the homework structure. Most carefree class, takes up little time. Tags: extra credit, clear grading criteria, graded by few things.

## Embeddings + Vector Store

**Embedding model:** `sentence-transformers/all-MiniLM-L6-v2` (normalized embeddings)

**Vector store:** ChromaDB, persistent directory `chroma_db/`, collection `howard_cs_guide`, cosine distance. Each chunk stores `source_file`, `source_url`, `source_type` (`reddit` or `rmp`), and the chunk index.

`all-MiniLM-L6-v2` is small enough to run on a laptop with no API key and no per-query cost. That is the right trade for this project. For a production deployment I would measure a larger model (a current API embedding model, or a larger open model such as a BGE or E5 variant) on this same question set before switching. The tradeoffs that matter here:

- **Accuracy on short opinions.** MiniLM ranks the name and course number well (CSCI-136 at distance 0.20) and ranks a detailed exam review *behind* a one-line “the goat” review. A larger model might not do that. It also costs more and is slower.
- **Context length.** These chunks are under 720 characters. A long-context embedding model would not help and would add latency.
- **Multilingual support.** The corpus is English. A multilingual model would be unused capacity.
- **Local vs API.** Local MiniLM keeps student reviews on the machine and has no rate limit. An API model means every review text leaves the machine, plus a bill and a failure mode when the network is down.

## Retrieval

The query is embedded with the same model. ChromaDB returns the **top 4** chunks by cosine distance (0 is identical). On this corpus, useful hits land around 0.20–0.45. The weather query’s best hit is 0.82. If the best distance is above **0.65**, `query.py` refuses without calling the LLM.

### Query 1 — CSCI-136 topics

**Query:** What do students say CSCI-136 covers, and which programming languages might the class use?

| Distance | Source | Why it came back |
|---|---|---|
| 0.200 | `02_reddit_csci136_topics.txt` | The student reply that names C++ or Python and lists classes, linked lists, sorting, hash tables, trees, and Big-O |
| 0.286 | `02_reddit_csci136_topics.txt` | The original question asking for the CSCI-136 syllabus |
| 0.313 | `02_reddit_csci136_topics.txt` | Follow-up comparing CSCI-136 with CSCI-135 |
| 0.397 | `07_reddit_freshman_coursework.txt` | First-year Python and C++ labs. Related languages, not the CSCI-136 topic list |

The top chunk is the answer. It shares the course number with the query and also contains the topic list the query does not name word-for-word (“hash tables,” “Big-O”), which is what the embedding is for.

### Query 2 — Computer Organization

**Query:** What do students say about the difficulty of Computer Organization at Howard?

| Distance | Source | Why it came back |
|---|---|---|
| 0.390 | `03_reddit_computer_organization.txt` | Computer Organization I and II, tremendous workload, MIPS harder than C++, Python, or Java |
| 0.398 | `12_rmp_gloria_washington.txt` | Gloria Washington’s page header, which contains “Level of difficulty 3.7” |
| 0.417 | `03_reddit_computer_organization.txt` | The question that asked how hard the major is |
| 0.421 | `11_rmp_jeremy_blackstone.txt` | Blackstone’s page header, “Level of difficulty 2.3” |

The top chunk is the one that answers the question. The next two professor headers are distractors: the query says “difficulty,” and those pages use that word for a 1–5 rating of a different person. They score only slightly worse than the real answer, which is why a higher top-k would start feeding the model noise.

### Query 3 — BisonHub registration

**Query:** How do students say a new student actually registers for classes in BisonHub?

| Distance | Source | Why it came back |
|---|---|---|
| 0.331 | `04_reddit_bisonhub_registration.txt` | Press the orange “register from plan” button; if it is missing, onboarding tasks are unfinished |
| 0.453 | `05_reddit_cs_advisor.txt` | A different registration path: ProctorU placement and an advisor override for math |
| 0.515 | `07_reddit_freshman_coursework.txt` | First-year labs. Weak match |
| 0.589 | `04_reddit_bisonhub_registration.txt` | The question asking how to register, without the answer |

The top chunk is the procedure. The math-override chunk is about BisonHub registration too, but it is a different situation (getting Calculus onto the plan). A grounded answer can mention it only as a separate case.

## Grounded Generation

Grounding is enforced in two places, not only by asking the model to behave.

1. **Pipeline gate.** If no chunks come back, or the best cosine distance is greater than 0.65, `answer()` returns the refusal sentence and does not call Groq. The weather question hits this gate (best distance 0.82).
2. **Prompt.** The system prompt says to use only the retrieved context, to use the refusal sentence when the context is not enough, and not to invent names, ratings, or dates. It also says to report disagreement and not to crown a single professor when the context does not rank one. Temperature is 0.
3. **Citations in code.** After generation, if the model text does not already contain `Sources:`, `query.py` appends the source file names from the retrieved metadata. The Gradio “Retrieved from” box lists those files, distances, and a preview independently of what the model writes.

The model is Groq `meta-llama/llama-4-scout-17b-16e-instruct` (`GROQ_MODEL` overrides it). The key is read from `.env` and is not committed.

## Example Responses

### Out of scope (this response does not call the LLM)

**Query:** What is the weather in Washington, DC tomorrow?

**Answer:**

> I don't have enough information in the collected Howard CS student documents to answer that.

The best retrieved chunk was a Gloria Washington review at distance **0.819**, then more of the same page at 0.840 and 0.853, then Guy Lingani at 0.907. All of those are above the 0.65 gate, so the refusal is produced by the pipeline. The retrieved-from panel still shows those weak chunks, which is how you can see that the search found nothing on weather.

### In-scope answers

`python evaluate.py` calls Groq for the five test questions and writes `eval_results.json`. This environment does not have `GROQ_API_KEY`, so those answer strings are not invented here. After you copy `.env.example` to `.env` and set the key, run `python evaluate.py` and paste the two strongest answers into this section. Retrieval for those questions is already recorded above and in the evaluation table.

## Query Interface

`app.py` is a Gradio page with four visible parts:

- **Your question** — a text box. Press Ask, or press Enter.
- **Limit sources (optional)** — All sources, Reddit threads only, or Rate My Professors only. This sets a ChromaDB `where` filter on `source_type`.
- **Answer** — the grounded paragraph, or the refusal sentence.
- **Retrieved from** — each chunk’s file name, source type, cosine distance, and a short preview.

Example questions are listed under the form, including the weather refusal.

### Sample interaction (retrieval, recorded from the index)

**Input:** What do students say CSCI-136 covers, and which programming languages might the class use?  
**Filter:** All sources

**Retrieved from:**

- `02_reddit_csci136_topics.txt` (reddit, distance 0.200) — CSCI-136 may be C++ or Python and covers classes, linked lists, sorting, dictionaries and hash tables, trees, and Big-O.
- `02_reddit_csci136_topics.txt` (reddit, distance 0.286) — the thread question asking for the syllabus.
- `02_reddit_csci136_topics.txt` (reddit, distance 0.313) — follow-up comparing it with CSCI-135.
- `07_reddit_freshman_coursework.txt` (reddit, distance 0.397) — first-year Python and C++ labs.

The answer box is filled by Groq from those chunks once `GROQ_API_KEY` is set. The citation list is added in `query.py` even if the model omits it.

### Stretch: metadata filter

Same question shape, two filters. Query: “What do reviews say about Jeremy Blackstone's CSCI 135 class?”

| Filter | Best hits | Distance |
|---|---|---|
| Rate My Professors only | Four chunks, all from `11_rmp_jeremy_blackstone.txt` (the CSCI 454 complaint, then three CSCI 135 reviews) | 0.316–0.366 |
| Reddit threads only | CSCI-136 syllabus thread, then a JacSLB comment about Computer Organization professors. No review text, because the reviews are not Reddit posts. | 0.580–0.616 |

The filter does what it claims: Rate My Professors mode cannot wander into a Reddit thread, and Reddit mode cannot quote a Rate My Professors page. Reddit-only distances are weak because the detailed CSCI 135 comments live on the review page, not in the threads. The threads only say that Blackstone helped a student pass the C++ course.

## Evaluation

Run `python evaluate.py` after the index exists and `GROQ_API_KEY` is set. Judgments below separate **retrieval** (measured) from **generation** (not run in this environment, so no accuracy label is assigned to an answer that was never produced).

| # | Question | Expected answer | Retrieval | Generation |
|---|---|---|---|---|
| 1 | What do students say CSCI-136 covers, and which programming languages might the class use? | C++ or Python depending on section. Topics: classes and OOP, linked lists (vectors in C++), sorting, dictionaries and hash tables, trees and traversal, Big-O, runtime and space complexity. | Top chunk is that reply, distance 0.200, from `02_reddit_csci136_topics.txt`. | Not run. No API key. |
| 2 | What do students say about the difficulty of Computer Organization at Howard? | Organization I and II are very difficult, the workload is tremendous, and MIPS is much harder than C++, Python, or Java. A separate comment says Computer Organization professors cannot teach. | The MIPS reply is first, distance 0.390, from `03_reddit_computer_organization.txt`. The “cannot teach” comment was not in the top 4. | Not run. No API key. |
| 3 | How do students say a new student actually registers for classes in BisonHub? | Press the orange register-from-plan button. If it is missing, onboarding is unfinished and registration is blocked. Do not wait for an advisor to email first. | The button instructions are first, distance 0.331, from `04_reddit_bisonhub_registration.txt`. The “do not wait” sentence was not in the top 4. | Not run. No API key. |
| 4 | What do Rate My Professors reviews say about Jeremy Blackstone’s CSCI 135 class specifically? | CSCI 135: assignments posted up front, not numerous or hard, self-paced, exams follow homework, little time if you already know C++. Page stats 4.8/5, 92% would take again, difficulty 2.3. The harsh review is CSCI 454, not CSCI 135. | See the failure case. The March 26, 2026 review that states the exam policy is rank 8 (distance 0.390). The top hit is the CSCI 454 complaint (0.261). | Not run. No API key. |
| 5 | Which Howard CS professor do the documents say gives the most useful feedback? | No single winner. A CSCI 354 review of Noha Hazzazi and a CSCI 136 review of Saurav Aryal are tagged “gives good feedback.” The documents do not rank one professor. | Those two reviews are not in the top 8. Top hits are Blackstone praise (0.388), a “teaching yourself” comment, and the thread question about professor support. | Not run. No API key. |

### Out-of-scope test

**Question:** What is the weather in Washington, DC tomorrow?

**Actual response:** I don't have enough information in the collected Howard CS student documents to answer that.

**Passed refusal test?** Yes. Best distance 0.819, above the 0.65 gate, so Groq was not called.

## Failure Analysis

**Observed failure:** For “What do Rate My Professors reviews say about Jeremy Blackstone’s CSCI 135 class specifically?”, the only review that says assignments are posted at the start and that exams follow the homework is not retrieved.

**Cause:** Retrieval. The chunk exists and is intact (`11_rmp_jeremy_blackstone.txt`, the March 26, 2026 CSCI 135 review). Its cosine distance is 0.390, which would be an acceptable score on its own. Four other chunks score 0.261–0.306 and take the top 4: the CSCI 454 review about a changed final, the one-line “The goat” CSCI 135 review, the December 2023 “cares about you understanding” review, and the October 2025 “best computer science professor” review.

**Why it happened:** `all-MiniLM-L6-v2` is matching the query’s proper nouns (Blackstone, CSCI 135, reviews) more tightly when the chunk is *mostly* those nouns. “The goat” is a short chunk that is almost only the name, the course, and a sentiment, so it sits closer to the query. The March 26 review adds C++, self-paced work, homework, and exams. Those extra sentences move the embedding. The CSCI 454 review ranks first even though it is the wrong course, because it is a long, emotional review of the same professor and the query says “reviews.” Top-k is 4, so the exam-policy chunk never reaches the prompt. A grounded model cannot state that policy, because it is not allowed to use anything outside the retrieved text. Raising chunk size will not fix this one: the review is already a single chunk under 720 characters. A reranker, or a lexical boost on the course number, would.

Question 5 fails for the same kind of reason. “Gives good feedback” is a tag on the Hazzazi CSCI 354 review and the Aryal CSCI 136 review. The query “most useful feedback” retrieved “best computer science professor” and a thread about professors providing support instead. The tag never entered the top 8. MiniLM is not treating that tag as the answer to a superlative question.

## Spec Reflection

**What the spec settled:** `planning.md` required paragraph-aware chunks, cosine distance, top 4, source metadata, and a refusal when the documents do not support the answer. The ingestion script follows that shape, and the distance gate is the refusal the spec described, implemented in code rather than left as a sentence in the prompt.

**Where implementation diverged:** The spec started at 450 characters and packed neighboring paragraphs up to that cap. After the first retrieval test, the MIPS sentence and the Blackstone exam sentence were in the next chunk and were not retrieved. The chunk size was raised to 720, and packing across paragraphs was removed so one comment or one review stays whole. `planning.md` was updated with that reason. Top-k stayed at 4. Raising it would have pulled the exam review in (it is rank 8, so not even k=5) and would also have pulled more “level of difficulty” headers into the Computer Organization question.

## AI Usage

1. **Chunking.** The chunking section of `planning.md` was given as the spec for `chunk_text()`. The first implementation packed paragraphs up to 450 characters with an 80-character overlap. That matched the first draft of the spec and failed the retrieval check: key sentences landed in the next chunk. It was replaced with one paragraph per chunk, a 720-character cap, and word-aligned overlap only when a paragraph is split. The spec was updated to match what retrieval actually needed.

2. **Interface and grounding.** The Gradio sketch in the assignment puts the answer and the sources in two boxes. The first pass combined them into one Markdown field. That was split back apart so the citation list is not only whatever the model types. A source-type dropdown was added for the metadata-filter stretch, which the spec’s stretch section describes. A distance gate was added in `query.py` so an off-topic question refuses even if the model would otherwise write a fluent answer from general knowledge. The system prompt was also tightened to forbid crowning a professor when the context does not rank one, which the first prompt did not say.

## Architecture

```text
Document Ingestion (data/*.txt, cleaned in ingest.py)
        ↓
Chunking (720 characters, 100 overlap only on long paragraphs)
        ↓
Embedding (sentence-transformers all-MiniLM-L6-v2)
        +
Vector store (ChromaDB, cosine, metadata: source_file, source_url, source_type, chunk)
        ↓
Retrieval (top 4; optional source_type filter; refuse if best distance > 0.65)
        ↓
Generation (Groq meta-llama/llama-4-scout-17b-16e-instruct, context-only prompt)
        +
Source list appended in code
```

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

Copy `.env.example` to `.env` and set `GROQ_API_KEY`. Get a free key at https://console.groq.com. The file is listed in `.gitignore`.

### 4. Build the vector index

```bash
python ingest.py
```

### 5. Run the CLI

```bash
python query.py
```

### 6. Run the web interface

```bash
python app.py
```

Open http://localhost:7860.

### 7. Run the evaluation questions

```bash
python evaluate.py
```

## Limitations

This is a small class project, not an advising service. The corpus is 16 public threads and review pages, not a survey of current students. Review pages change, and a short glowing review can outrank a specific one, as the Blackstone failure shows. Ratings describe whoever wrote them. Check the source link before making a schedule decision. Do not treat a generated paragraph as the department’s position.
