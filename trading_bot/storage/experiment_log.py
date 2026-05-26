from __future__ import annotations

from abc import ABC, abstractmethod
import json
from datetime import datetime
from pathlib import Path
from typing import Any


class ExperimentLogger(ABC):
    @abstractmethod
    def log(self, record: dict[str, Any]) -> Path:
        ...


class JsonExperimentLogger(ExperimentLogger):
    def __init__(self, root: str = "experiments") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def log(self, record: dict[str, Any]) -> Path:
        stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = self.root / f"{record['name']}_{stamp}.json"
        path.write_text(json.dumps(record, indent=2, default=str), encoding="utf-8")
        return path
