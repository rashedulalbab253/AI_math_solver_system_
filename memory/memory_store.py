import json
import os
from typing import Optional, List


class MemoryStore:
    def __init__(self, path="memory/memory.json"):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)

        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                json.dump([], f)

    def save(self, record: dict):
        data = self._load_all()
        data.append(record)
        with open(self.path, "w") as f:
            json.dump(data, f, indent=2)

    def find_similar(self, problem_text: str) -> Optional[dict]:
        """
        Very simple similarity:
        match by route + keywords
        (Enough for assignment)
        """
        data = self._load_all()
        for item in data:
            if item["problem_text"] in problem_text or problem_text in item["problem_text"]:
                return item
        return None

    def _load_all(self) -> List[dict]:
        with open(self.path, "r") as f:
            return json.load(f)
