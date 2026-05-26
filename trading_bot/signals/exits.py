from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class ExitRule(ABC):
    @abstractmethod
    def should_exit(self, price_row: pd.Series, entry_price: float, holding_days: int, stop_price: float | None) -> bool:
        ...


class CompositeExitRule(ExitRule):
    def __init__(self, fixed_stop_pct: float = 0.08, max_holding_days: int = 20) -> None:
        self.fixed_stop_pct = fixed_stop_pct
        self.max_holding_days = max_holding_days

    def should_exit(self, price_row: pd.Series, entry_price: float, holding_days: int, stop_price: float | None) -> bool:
        fixed_stop = entry_price * (1 - self.fixed_stop_pct)
        active_stop = max(fixed_stop, stop_price or fixed_stop)
        return price_row["close"] <= active_stop or holding_days >= self.max_holding_days
