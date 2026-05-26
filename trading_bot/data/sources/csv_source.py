from __future__ import annotations

import pandas as pd

from trading_bot.data.sources.base import MarketDataSource


class CSVMarketDataSource(MarketDataSource):
    def __init__(self, path: str) -> None:
        self.path = path

    def get_history(
        self, symbols: list[str], start: pd.Timestamp, end: pd.Timestamp, timeframe: str = "1d"
    ) -> pd.DataFrame:
        df = pd.read_csv(self.path, parse_dates=["timestamp"])
        df = df[df["symbol"].isin(symbols)]
        return df[(df["timestamp"] >= start) & (df["timestamp"] <= end)].copy()
