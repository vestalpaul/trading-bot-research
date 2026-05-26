from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np
import pandas as pd


class FeaturePipeline(ABC):
    @abstractmethod
    def transform(self, data: pd.DataFrame, benchmark: pd.DataFrame, as_of: pd.Timestamp) -> pd.DataFrame:
        ...


class DefaultFeaturePipeline(FeaturePipeline):
    def transform(self, data: pd.DataFrame, benchmark: pd.DataFrame, as_of: pd.Timestamp) -> pd.DataFrame:
        rows = []
        bench = benchmark[benchmark["timestamp"] <= as_of].sort_values("timestamp")
        bench_ret_60 = bench["close"].pct_change(60).iloc[-1] if len(bench) > 60 else np.nan
        for symbol, df in data[data["timestamp"] <= as_of].groupby("symbol"):
            df = df.sort_values("timestamp")
            if len(df) < 200:
                continue
            close = df["close"]
            ret = close.pct_change()
            high_low = df["high"] - df["low"]
            atr20 = high_low.rolling(20).mean().iloc[-1]
            dd_lookback = close.tail(126)
            max_dd = ((dd_lookback / dd_lookback.cummax()) - 1.0).min()
            row = {
                "symbol": symbol,
                "close": close.iloc[-1],
                "ma20": close.rolling(20).mean().iloc[-1],
                "ma50": close.rolling(50).mean().iloc[-1],
                "ma200": close.rolling(200).mean().iloc[-1],
                "ret20": close.pct_change(20).iloc[-1],
                "ret60": close.pct_change(60).iloc[-1],
                "volatility20": ret.rolling(20).std().iloc[-1] * np.sqrt(252),
                "atr20": atr20,
                "max_drawdown_126": max_dd,
                "vol_expansion": df["volume"].tail(5).mean() / df["volume"].tail(20).mean(),
                "rel_strength_60": close.pct_change(60).iloc[-1] - bench_ret_60,
                "dollar_volume_20": (df["close"] * df["volume"]).tail(20).mean(),
            }
            rows.append(row)
        return pd.DataFrame(rows)
