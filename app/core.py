from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "guides.jsonl"


def load_examples(path: Path = DATA_PATH) -> list[dict[str, str]]:
    if not path.exists():
        return []
    rows: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        value = json.loads(line)
        if isinstance(value, dict) and all(key in value for key in ("destination", "interests", "guide")):
            rows.append({key: str(value[key]) for key in ("destination", "interests", "guide")})
    return rows


def normalize(value: str) -> str:
    return " ".join(value.casefold().split())


def find_sample_guide(destination: str, interests: str, examples: list[dict[str, str]] | None = None) -> str | None:
    entries = examples if examples is not None else load_examples()
    place = normalize(destination)
    wanted = {part.strip() for part in normalize(interests).replace(";", ",").split(",") if part.strip()}
    if not place or not wanted:
        return None

    best: tuple[int, str] | None = None
    for entry in entries:
        if normalize(entry["destination"]) != place:
            continue
        available = {part.strip() for part in normalize(entry["interests"]).replace(";", ",").split(",") if part.strip()}
        overlap = len(wanted & available)
        if overlap and (best is None or overlap > best[0]):
            best = (overlap, entry["guide"])
    return best[1] if best else None


def build_prompt(destination: str, interests: str) -> str:
    return (
        f"Write a concise, welcoming mini-guide for {destination}. "
        f"The traveler is interested in {interests}. Give three specific ideas, "
        "include a practical local tip, and avoid inventing opening hours or prices."
    )


def evaluate_guide(guide: str, destination: str, interests: str) -> dict[str, Any]:
    words = guide.split()
    tokens = set(normalize(guide).replace(".", " ").replace(",", " ").split())
    interest_terms = {x for x in normalize(interests).replace(",", " ").split() if len(x) > 2}
    destination_terms = {x for x in normalize(destination).split() if len(x) > 2}
    interest_hits = sorted(tokens & interest_terms)
    destination_hits = sorted(tokens & destination_terms)
    return {
        "word_count": len(words),
        "concise": len(words) <= 180,
        "interest_terms_found": interest_hits,
        "destination_terms_found": destination_hits,
        "relevance_score": round((len(interest_hits) + len(destination_hits)) / max(1, len(interest_terms) + len(destination_terms)), 2),
    }
