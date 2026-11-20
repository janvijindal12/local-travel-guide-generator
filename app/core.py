from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "guides.jsonl"


def load_examples(path: Path = DATA_PATH) -> list[dict[str, str]]:
    if not path.exists():
        return []
    rows: list[dict[str, str]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        required = ("destination", "interests", "guide")
        if not isinstance(value, dict) or not all(key in value for key in required):
            raise ValueError(f"Dataset row {line_number} must include destination, interests, and guide")
        rows.append({key: str(value[key]).strip() for key in required})
    return rows


def normalize(value: str) -> str:
    return " ".join(value.casefold().split())


def split_interests(value: str) -> set[str]:
    return {normalize(part) for part in re.split(r"[,;]", value) if normalize(part)}


def find_sample_guide(destination: str, interests: str, examples: list[dict[str, str]] | None = None) -> str | None:
    entries = examples if examples is not None else load_examples()
    place = normalize(destination)
    wanted = split_interests(interests)
    if not place or not wanted:
        return None

    best: tuple[float, int, str] | None = None
    for position, entry in enumerate(entries):
        if normalize(entry["destination"]) != place:
            continue
        available = split_interests(entry["interests"])
        overlap = len(wanted & available)
        if overlap:
            score = overlap / len(wanted)
            candidate = (score, -position, entry["guide"])
            if best is None or candidate[:2] > best[:2]:
                best = candidate
    return best[2] if best else None


def build_prompt(destination: str, interests: str) -> str:
    return (
        f"Write a concise, welcoming mini-guide for {destination}. "
        f"The traveler is interested in {interests}. Give three specific ideas, "
        "include a practical local tip, and avoid inventing opening hours or prices."
    )


def evaluate_guide(guide: str, destination: str, interests: str) -> dict[str, Any]:
    tokens = set(re.findall(r"[a-z0-9]+", normalize(guide)))
    wanted = {term for term in re.findall(r"[a-z0-9]+", normalize(interests)) if len(term) > 2}
    interest_hits = sorted(tokens & wanted)
    return {
        "word_count": len(guide.split()),
        "concise": len(guide.split()) <= 180,
        "interest_terms_found": interest_hits,
        "destination_terms_found": sorted(tokens & set(re.findall(r"[a-z0-9]+", normalize(destination)))),
        "relevance_score": round(len(interest_hits) / max(1, len(wanted)), 2),
    }
