from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class UniverseSelector(ABC):
    @abstractmethod
    def select(self, data: pd.DataFrame, as_of: pd.Timestamp) -> list[str]:
        ...


class LiquidityUniverseSelector(UniverseSelector):
    def __init__(self, min_price: float, min_dollar_volume: float, min_history_days: int) -> None:
        self.min_price = min_price
        self.min_dollar_volume = min_dollar_volume
        self.min_history_days = min_history_days

    def select(self, data: pd.DataFrame, as_of: pd.Timestamp) -> list[str]:
        eligible: list[str] = []
        for symbol, df in data[data["timestamp"] <= as_of].groupby("symbol"):
            if len(df) < self.min_history_days:
                continue
            last = df.sort_values("timestamp").iloc[-1]
            dv = (df["close"] * df["volume"]).tail(20).mean()
            if last["close"] >= self.min_price and dv >= self.min_dollar_volume:
                eligible.append(symbol)
        return sorted(eligible)
