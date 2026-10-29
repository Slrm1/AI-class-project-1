# Evaluation Results

Retrieval was run against the index of 78 chunks. Because `GROQ_API_KEY` was not set, responses were produced by the deterministic extractive fallback in `query.py`. That fallback uses only the two highest-ranked chunks, truncates each excerpt to 420 characters, and includes its source filename. These are real pipeline outputs, not guessed model answers.

The questions match `planning.md`. The full write-up, including distances and the failure case, is in `README.md`.

## Test Questions

### 1. CSCI-136
**Question:** What do students say CSCI-136 covers, and which programming languages might the class use?

**Expected:** C++ or Python depending on section. Topics include classes and OOP, linked lists (vectors in C++), sorting, dictionaries and hash tables, trees and traversal, and Big-O / runtime / space complexity.

**Retrieval:** Top chunk distance 0.200 from `02_reddit_csci136_topics.txt`. It contains that topic list.

**Actual response summary:** Returned the student reply stating that the language may be C++ or Python and listing classes/OOP, linked lists, sorting, dictionaries and hash tables, trees, and Big-O/runtime/space complexity. Source: `02_reddit_csci136_topics.txt`.

**Judgment:** Accurate. The response includes every expected topic and both possible languages.

### 2. Computer Organization
**Question:** What do students say about the difficulty of Computer Organization at Howard?

**Expected:** Organization I and II are very difficult, the workload is tremendous, and MIPS is much harder than C++, Python, or Java. A separate comment says the Computer Organization professors cannot teach.

**Retrieval:** The MIPS reply is first, distance 0.390, `03_reddit_computer_organization.txt`. The “cannot teach” comment was not in the top 4.

**Actual response summary:** Returned that Computer Organization I and II are very difficult, the workload is tremendous, and the courses use MIPS assembly, which the student describes as harder than high-level languages. Source: `03_reddit_computer_organization.txt`.

**Judgment:** Partially accurate. The central difficulty and workload claims are present, but the separate criticism of the instructors was not retrieved.

### 3. BisonHub registration
**Question:** How do students say a new student actually registers for classes in BisonHub?

**Expected:** Press the orange “register from plan” button. If it is missing, onboarding tasks are unfinished. Do not wait for an advisor to email first.

**Retrieval:** Button instructions are first, distance 0.331, `04_reddit_bisonhub_registration.txt`. The “do not wait” sentence was not in the top 4.

**Actual response summary:** Returned the instruction to press the orange “register from plan” button and explained that a missing button means onboarding tasks are incomplete. Source: `04_reddit_bisonhub_registration.txt`.

**Judgment:** Accurate. It directly answers the procedural question. The extra advice not to wait for an advisor was not needed to complete the procedure.

### 4. Blackstone CSCI 135
**Question:** What do Rate My Professors reviews say about Jeremy Blackstone's CSCI 135 class specifically?

**Expected:** Assignments are posted at the start, they are not numerous or hard, students can work at their own pace, and exams follow the homework. The harsh review on that page is about CSCI 454.

**Retrieval:** Failure. The March 26, 2026 review with the exam policy is rank 8 (distance 0.390). The top hit is the CSCI 454 complaint (distance 0.261).

**Actual response summary:** The first excerpt discussed a negative CSCI 454 experience, while the second offered only brief praise for CSCI 135. It did not return the requested CSCI 135 assignment or exam-policy details.

**Judgment:** Inaccurate. The response mixes courses and cannot state the expected evidence because that review is not in the top four.

### 5. Most useful feedback
**Question:** Which Howard CS professor do the documents say gives the most useful feedback?

**Expected:** No single winner. Hazzazi (CSCI 354) and Aryal (CSCI 136) reviews are tagged “gives good feedback.”

**Retrieval:** Those reviews are not in the top 8. Top hit is a Blackstone “best professor” review at distance 0.388.

**Actual response summary:** Returned general praise for Blackstone and a Reddit comment about faculty support. It did not retrieve the Hazzazi or Aryal reviews tagged “gives good feedback.”

**Judgment:** Inaccurate. The retrieved evidence neither answers the feedback question nor supports naming one winner.

## Out-of-Scope Test

**Question:** What is the weather in Washington, DC tomorrow?

**Actual response:** I don't have enough information in the collected Howard CS student documents to answer that.

**Passed refusal test?** Yes. Best distance 0.819, above the 0.65 gate. Groq is not called.

## Failure Analysis

**Observed failure:** The Blackstone CSCI 135 exam-policy review is stored as its own chunk and still loses the top 4 to shorter CSCI 135 praise and to a CSCI 454 complaint.

**Cause:** Retrieval, specifically `all-MiniLM-L6-v2` cosine ranking at k=4.

**Why it happened:** The useful review is longer. Extra sentences about C++ and homework move it to distance 0.390. “The goat” and the CSCI 454 review sit at 0.261–0.306 because they are dominated by the professor’s name. See `README.md`.

**Possible improvement:** A reranker, or a keyword boost when the query names a course number, so CSCI 454 cannot outrank a chunk that literally says CSCI 135 and “exams.”
