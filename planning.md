# Planning — The Unofficial Howard CS Guide

> Spec written before the student-knowledge pipeline. Official catalog pages that were in the first draft are not the corpus this system retrieves from. Stretch work (metadata filtering) is specified at the bottom and was added before that feature was implemented.

## Domain

Unofficial Howard University computer science student knowledge: what students actually say about courses, professors, registration, advising, internships, and getting through the major. Official catalogs list credit hours and course titles, but they do not say whether Computer Organization is the class that wrecks a semester, which CSCI 135 professor posts the assignments up front, or that BisonHub hides the register button until onboarding tasks are done. That advice lives in r/HowardUniversity threads and public Rate My Professors reviews, scattered across pages a new student would not know to open.

## Documents

Fifteen public sources. Reddit text was taken from archived r/HowardUniversity threads. Professor pages are public Rate My Professors reviews, saved as plain text with the page URL. Each file keeps the professor or thread name inside the body so a chunk can stand alone.

| File | What it is | URL |
|---|---|---|
| `01_reddit_how_is_howard_cs.txt` | Thread on teaching quality, Blackstone, Computer Organization professors, alumni network | https://www.reddit.com/r/HowardUniversity/comments/1cdwjwn/how_is_howard_university_for_computer_science/ |
| `02_reddit_csci136_topics.txt` | Student description of CSCI-136 languages and topics | https://www.reddit.com/r/HowardUniversity/comments/kpqcf5/csci136_syllabus/ |
| `03_reddit_computer_organization.txt` | Workload of Computer Organization I and II and MIPS | https://www.reddit.com/r/HowardUniversity/comments/ll492a/computer_science_majors_how_hard_is_it/ |
| `04_reddit_bisonhub_registration.txt` | How the orange “register from plan” button actually works | https://www.reddit.com/r/HowardUniversity/comments/1dfhalm/registering_for_cs_courses/ |
| `05_reddit_cs_advisor.txt` | Ladan Johnson not answering email, and not waiting on advisors | https://www.reddit.com/r/HowardUniversity/comments/1dfvnjh/compsci_advisor/ |
| `06_reddit_google_step_and_internships.txt` | Google STEP, Handshake, CEA fairs, NASA and NY Times examples | https://www.reddit.com/r/HowardUniversity/comments/u7bhv8/q_a/ |
| `07_reddit_freshman_coursework.txt` | First-year Python and C++ labs, ALEKS, textbooks, 3.5 GPA | https://www.reddit.com/r/HowardUniversity/comments/u7bhv8/q_a/ |
| `08_reddit_staying_in_cs.txt` | Corporate visits, Google-in-Residence, self-teaching | https://www.reddit.com/r/HowardUniversity/comments/1cnaz8b/convince_me_to_remain_a_cs_major/ |
| `09_reddit_campus_wifi.txt` | Campus Wi-Fi outages and professors not adjusting deadlines | https://www.reddit.com/r/HowardUniversity/comments/y1nyek/wifi_at_howard/ |
| `10_reddit_switching_into_cs.txt` | Switching into CS is competitive; CIS is the nearby alternative | https://www.reddit.com/r/HowardUniversity/comments/1cmpdea/rejected_from_major_switch/ |
| `11_rmp_jeremy_blackstone.txt` | CSCI 135 praise and one harsh CSCI 454 review | https://www.ratemyprofessors.com/professor/2640220 |
| `12_rmp_gloria_washington.txt` | Mixed CSCI 135 / CSCI 136 reviews | https://www.ratemyprofessors.com/professor/2084505 |
| `13_rmp_saurav_aryal.txt` | CSCI 135, 136, and 354 reviews, including feedback and labs | https://www.ratemyprofessors.com/professor/2672438 |
| `14_rmp_guy_lingani.txt` | CSCI 365 cloud computing elective | https://www.ratemyprofessors.com/professor/2992359 |
| `15_rmp_jiang_li.txt` | CSCI 201 and CSCI 453 reviews | https://www.ratemyprofessors.com/professor/2323879 |
| `16_rmp_noha_hazzazi.txt` | CSCI 120, 135, and 354 reviews, including a “gives good feedback” tag | https://www.ratemyprofessors.com/professor/2418869 |

`05` also includes the related advising comments from https://www.reddit.com/r/HowardUniversity/comments/1l7ba0c/advsing/ and https://www.reddit.com/r/HowardUniversity/comments/1ecs231/cs_non_technical_elective_course/ because those threads are about the same advisor problem. `06` and `07` are two slices of one long Q&A so internship facts and first-year coursework are not glued into a single document.

## Chunking Strategy

- Chunk size: 720 characters
- Overlap: 100 characters
- Boundary: one blank-line paragraph is one chunk when it is at or under 720 characters. That paragraph is one student comment or one professor review. A paragraph longer than 720 characters is split on sentence boundaries, with a 100-character overlap snapped to a word boundary. A leftover shorter than 80 characters is appended to the previous chunk instead of being embedded on its own.

The first draft used 450 characters and also packed neighboring paragraphs into the same chunk until the cap was hit. That cut two facts in half. The MIPS sentence was separated from “Computer Organization,” and “exams follow the homework structure” was separated from the rest of the Blackstone CSCI 135 review. The half that still held the course name lost to other chunks that merely contained the word “difficulty.” Keeping each review or comment whole, up to 720 characters, leaves the name and the claim in the same embedding. Overlap is only needed when a comment is longer than that cap.

Chunks that are too small (under ~150 characters, or a cutoff like “Professor Smith’s exams are heavily”) embed almost no meaning, so semantic search matches stray words. Chunks that are too large (a 1,500-character merge of Blackstone, campus safety, and SAT scores) make one embedding represent several questions, so the top hit is only loosely about the query. The target range is 50–2,000 chunks. Fewer than 50 would mean each chunk covers too much; more than 2,000 would mean the pieces are fragments.

## Retrieval Approach

Embedding model: `all-MiniLM-L6-v2` via `sentence-transformers`, with normalized embeddings. Vector store: ChromaDB persistent collection `howard_cs_guide`, cosine distance. Each chunk is stored with `source_file`, `source_url`, `source_type` (`reddit` or `rmp`), and chunk index.

Top-k is 4. Four chunks is enough to cover a short review plus a nearby comment without stuffing the prompt with a fifth loosely related post. Too few (k=1) drops the dissenting review. Too many (k=8 or more) pulls in Wi-Fi complaints or major-switch threads that share words like “professor” or “Howard” and can drag the answer off topic.

Semantic search matches a query like “which class uses assembly” to a chunk that says “MIPS” because the embedding model places related meanings near each other even when the query and the document do not share those exact words.

If cost were not a constraint in production, I would compare this model with a larger embedding model (for example a current OpenAI or Voyage model, or a larger MiniLM / BGE variant). I would weigh accuracy on short opinionated text, context length (these chunks are short, so a huge context window does not help), multilingual support (this corpus is English-only, so multilingual models are unused capacity), latency, and whether the model runs locally or through an API. Local MiniLM has no per-query cost and no rate limit. An API model can be more accurate on slang and nicknames but adds cost, a network dependency, and a privacy question because student reviews would leave the machine.

## Evaluation Plan

Each expected answer is something a grader can check against the source files.

1. **What do students say CSCI-136 covers, and which programming languages might the class use?**
   - Expected: It depends on the professor and section. The class may be C++ or Python. Topics named in the thread: classes and object-oriented programming, linked lists (and vectors in the C++ section), sorting algorithms, dictionaries and hash tables, trees, binary trees, and tree traversal, plus a heavy emphasis on Big-O, runtime complexity, and space complexity. Source: `02_reddit_csci136_topics.txt`.

2. **What do students say about the difficulty of Computer Organization at Howard?**
   - Expected: Computer Organization I and II are very difficult, the workload in both is tremendous, and MIPS assembly is much harder than C++, Python, or Java. A separate student specifically calls out Computer Organization professors as unable to teach. Sources: `03_reddit_computer_organization.txt` and `01_reddit_how_is_howard_cs.txt`.

3. **How do students say a new student actually registers for classes in BisonHub?**
   - Expected: If an orange button says “register from plan,” press it. If that button is missing, onboarding tasks in BisonHub are unfinished and registration stays blocked. Students also say not to wait for an advisor to email first. Source: `04_reddit_bisonhub_registration.txt` and `05_reddit_cs_advisor.txt`.

4. **What do Rate My Professors reviews say about Jeremy Blackstone’s CSCI 135 class specifically?**
   - Expected: CSCI 135 reviews describe a straightforward class: assignments are posted at the beginning, there are not many and they are not difficult, students can work at their own pace, exams follow the homework, and the class takes little time if you already know C++. Overall page stats on that same document: 4.8/5 quality, 92% would take again, difficulty 2.3. The negative review on that page is about CSCI 454 (one assignment graded, final questions changed), not CSCI 135. Source: `11_rmp_jeremy_blackstone.txt`.

5. **Which Howard CS professor do the documents say gives the most useful feedback?**
   - Expected: The documents do not name a single winner. A CSCI 354 review of Noha Hazzazi is tagged “Gives good feedback,” and a CSCI 136 review of Saurav Aryal is also tagged “Gives good feedback.” Blackstone reviews praise understanding but do not rank feedback, and one Blackstone review (CSCI 454) describes sloppy grading. Gloria Washington reviews criticize unclear instructions and rudeness and do not praise feedback. A grounded answer should report those mentions and refuse to crown one professor.

### Out-of-scope test

Ask: `What is the weather in Washington, DC tomorrow?` The system should say it does not have enough information in the collected documents. It should not forecast weather.

## Anticipated Challenges

- The same professor is praised and criticized in different courses (Blackstone CSCI 135 vs CSCI 454, Gloria Washington CSCI 135 vs CSCI 136). A chunk from the wrong course will make a confident wrong answer.
- Student spelling and nicknames (“LaDan” vs “Ladan,” “the goat,” “MIPS”) may not sit close to a formal query in MiniLM’s space, so retrieval can miss the only chunk that has the fact.
- Key facts can sit on a chunk boundary (a course number in one chunk and the complaint in the next). Overlap is there to reduce that, but it will not fix a split between two documents.
- The model may know Howard advising from training data (for example an L–Z advisor name that never appears in these files) and present it as if the documents said it. Grounding has to forbid that.
- Reddit threads mix CS advice with admissions stats, housing, and campus safety. Cleaning has to drop navigation and off-topic comments or those chunks will win weak queries.

## AI Tool Plan

- Ingestion and chunking: give the model this Chunking Strategy section, the Documents table (plain `.txt` files with a `URL:` line and a `Type:` line), and the architecture diagram. Ask it to implement `clean_text()` and `chunk_text()` using the chunk size and overlap in that section, splitting on paragraphs and then sentences. I will reject a version that splits only on a fixed character count with no paragraph check, and I will reject any cleaner that deletes the professor or course name. After the first retrieval test, if a key sentence is landing in the next chunk and missing the top results, I will raise the chunk size and update this section rather than keep the original number.
- Embedding and retrieval: give the model the Retrieval Approach section and the diagram. Ask it to embed with `all-MiniLM-L6-v2`, store cosine embeddings in ChromaDB with `source_file`, `source_url`, `source_type`, and chunk index, and return top 4 with distances. I will check that distance is cosine, not an unexplained default.
- Generation and interface: give the model the grounding rule (answer only from retrieved chunks; otherwise the exact refusal sentence), the required output (answer text plus a source list built in code, not only by the model), and the Gradio layout (question box, optional source-type filter, answer box, sources box). I will read the system prompt before running it and tighten it if it only “suggests” grounding.

## Architecture

```text
Document Ingestion (local .txt in data/, cleaned in ingest.py)
        ↓
Chunking (720 chars, 100 overlap, paragraph then sentence)
        ↓
Embedding (sentence-transformers all-MiniLM-L6-v2)
        +
Vector store (ChromaDB, cosine, metadata: source_file, source_url, source_type, chunk)
        ↓
Retrieval (top 4 semantic search; optional metadata filter on source_type)
        ↓
Generation (Groq meta-llama/llama-4-scout-17b-16e-instruct, context-only prompt)
        +
Source list appended in code
```

## Stretch — Metadata Filtering

Added before implementation. The query interface will let the user restrict retrieval to `reddit`, `rmp`, or all sources. ChromaDB `where` filters on `source_type`. A comparison query (“What do reviews say about Jeremy Blackstone’s CSCI 135?”) should be run twice: unfiltered, and filtered to Rate My Professors. The filtered run should not depend on the Reddit comment that only says he helped a student pass.
