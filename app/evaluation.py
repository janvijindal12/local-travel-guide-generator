from __future__ import annotations

import json
from pathlib import Path
from statistics import mean

from app.core import evaluate_guide, find_sample_guide, load_examples


ROOT = Path(__file__).resolve().parent.parent


def run_evaluation() -> dict[str, object]:
    examples = load_examples()
    tailored_scores = []
    baseline_scores = []
    rows = []
    for example in examples:
        tailored = evaluate_guide(example["guide"], example["destination"], example["interests"])
        baseline = evaluate_guide(
            "Enjoy a pleasant day exploring the area, then find a place to eat and relax.",
            example["destination"],
            example["interests"],
        )
        tailored_scores.append(tailored["relevance_score"])
        baseline_scores.append(baseline["relevance_score"])
        rows.append({
            "destination": example["destination"],
            "interests": example["interests"],
            "guide_found": find_sample_guide(example["destination"], example["interests"], examples) is not None,
            "tailored_relevance": tailored["relevance_score"],
            "generic_baseline_relevance": baseline["relevance_score"],
            "word_count": tailored["word_count"],
            "concise": tailored["concise"],
        })
    return {
        "method": "Lexical overlap and guide-length checks; not a human quality or factuality rating.",
        "example_count": len(rows),
        "matched_examples": sum(row["guide_found"] for row in rows),
        "mean_tailored_relevance": round(mean(tailored_scores), 2) if rows else 0,
        "mean_generic_baseline_relevance": round(mean(baseline_scores), 2) if rows else 0,
        "concise_examples": sum(row["concise"] for row in rows),
        "cases": rows,
    }


def main() -> None:
    result = run_evaluation()
    output = ROOT / "results" / "evaluation.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "cases"}, indent=2))


if __name__ == "__main__":
    main()
