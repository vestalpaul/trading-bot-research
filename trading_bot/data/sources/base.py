from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class MarketDataSource(ABC):
    """Interface for historical market data providers."""

    @abstractmethod
    def get_history(
        self,
        symbols: list[str],
        start: pd.Timestamp,
        end: pd.Timestamp,
        timeframe: str = "1d",
    ) -> pd.DataFrame:
        """Return OHLCV data indexed by timestamp with `symbol` column."""
