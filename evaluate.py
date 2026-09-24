"""Run the five evaluation questions plus the out-of-scope check.

Retrieval always runs. Generation runs when GROQ_API_KEY is set.
"""

import json
from pathlib import Path

from query import answer, retrieve

QUESTIONS = [
    {
        "id": 1,
        "question": "What do students say CSCI-136 covers, and which programming languages might the class use?",
        "expected": (
            "C++ or Python depending on professor and section. Topics: classes/OOP, linked lists "
            "(vectors in C++), sorting, dictionaries and hash tables, trees and traversal, Big-O, "
            "runtime and space complexity."
        ),
    },
    {
        "id": 2,
        "question": "What do students say about the difficulty of Computer Organization at Howard?",
        "expected": (
            "Computer Organization I and II are very difficult, with a tremendous workload. "
            "MIPS assembly is much harder than C++, Python, or Java. Another student says "
            "Computer Organization professors cannot teach."
        ),
    },
    {
        "id": 3,
        "question": "How do students say a new student actually registers for classes in BisonHub?",
        "expected": (
            "Press the orange Register from plan button. If it is missing, BisonHub onboarding "
            "tasks are unfinished and registration is blocked. Do not wait for an advisor to email first."
        ),
    },
    {
        "id": 4,
        "question": "What do Rate My Professors reviews say about Jeremy Blackstone's CSCI 135 class specifically?",
        "expected": (
            "CSCI 135 reviews: assignments posted at the start, not many and not difficult, self-paced, "
            "exams follow homework, little time if you already know C++. Page stats 4.8/5, 92% would "
            "take again, difficulty 2.3. The harsh review is about CSCI 454, not CSCI 135."
        ),
    },
    {
        "id": 5,
        "question": "Which Howard CS professor do the documents say gives the most useful feedback?",
        "expected": (
            "No single winner. Hazzazi (CSCI 354) and Aryal (CSCI 136) reviews are tagged "
            "'gives good feedback.' The documents do not rank one professor above the others."
        ),
    },
]

OUT_OF_SCOPE = "What is the weather in Washington, DC tomorrow?"


def dump_retrieval(question: str, source_type=None):
    rows = []
    for doc, meta, distance in retrieve(question, source_type=source_type):
        rows.append(
            {
                "source_file": meta["source_file"],
                "source_type": meta.get("source_type"),
                "distance": round(float(distance), 4),
                "chunk": doc,
            }
        )
    return rows


def main():
    report = {"questions": [], "out_of_scope": None, "filter_compare": None}
    for item in QUESTIONS:
        retrieved = dump_retrieval(item["question"])
        entry = {**item, "retrieved": retrieved, "response": None, "error": None}
        try:
            result = answer(item["question"])
            entry["response"] = result["answer"]
            entry["sources"] = result["sources"]
        except Exception as exc:
            entry["error"] = str(exc)
        report["questions"].append(entry)
        print(f"\n===== Q{item['id']} =====")
        print(item["question"])
        for row in retrieved:
            print(f"  {row['distance']:.4f} {row['source_file']}")
        print(entry["response"] or entry["error"])

    try:
        refused = answer(OUT_OF_SCOPE)
        report["out_of_scope"] = {"question": OUT_OF_SCOPE, "response": refused["answer"], "retrieved": dump_retrieval(OUT_OF_SCOPE)}
    except Exception as exc:
        report["out_of_scope"] = {"question": OUT_OF_SCOPE, "error": str(exc), "retrieved": dump_retrieval(OUT_OF_SCOPE)}
    print("\n===== OUT OF SCOPE =====")
    print(report["out_of_scope"].get("response") or report["out_of_scope"].get("error"))

    filter_q = "What do reviews say about Jeremy Blackstone's CSCI 135 class?"
    report["filter_compare"] = {
        "question": filter_q,
        "all": dump_retrieval(filter_q),
        "rmp_only": dump_retrieval(filter_q, source_type="rmp"),
    }

    Path("eval_results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("\nWrote eval_results.json")


if __name__ == "__main__":
    main()
