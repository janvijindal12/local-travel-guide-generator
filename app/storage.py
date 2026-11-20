from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


class GuideStore:
    def __init__(self, path: Path):
        self.path = path

    def save(self, destination: str, interests: str, guide: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "destination": destination.strip(),
            "interests": interests.strip(),
            "guide": guide.strip(),
        }
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")
