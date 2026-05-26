from __future__ import annotations

import pandas as pd

from trading_bot.data.sources.base import MarketDataSource


class YFinanceMarketDataSource(MarketDataSource):
    """Prototype adapter; falls back to synthetic-compatible empty behavior if yfinance unavailable."""

    def get_history(
        self, symbols: list[str], start: pd.Timestamp, end: pd.Timestamp, timeframe: str = "1d"
    ) -> pd.DataFrame:
        try:
            import yfinance as yf
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("yfinance is optional and not installed") from exc
        frames: list[pd.DataFrame] = []
        for symbol in symbols:
            hist = yf.download(symbol, start=start.date(), end=end.date(), interval="1d", progress=False)
            if hist.empty:
                continue
            hist = hist.rename(
                columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"}
            )
            hist = hist[["open", "high", "low", "close", "volume"]].reset_index(names="timestamp")
            hist["symbol"] = symbol
            frames.append(hist)
        if not frames:
            return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume", "symbol"])
        return pd.concat(frames, ignore_index=True)
