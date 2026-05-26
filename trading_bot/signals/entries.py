from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class EntryRule(ABC):
    @abstractmethod
    def should_enter(self, row: pd.Series) -> bool:
        ...


class TopRankEntryRule(EntryRule):
    def __init__(self, min_score: float) -> None:
        self.min_score = min_score

    def should_enter(self, row: pd.Series) -> bool:
        return float(row["score"]) >= self.min_score
