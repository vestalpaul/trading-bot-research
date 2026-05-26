from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class SignalModel(ABC):
    @abstractmethod
    def rank(self, features: pd.DataFrame, top_n: int | None = None) -> pd.DataFrame:
        ...


class RiskAdjustedRanker(SignalModel):
    def rank(self, features: pd.DataFrame, top_n: int | None = None) -> pd.DataFrame:
        df = features.copy()
        if df.empty:
            return df
        components = {
            "trend": (df["close"] > df["ma50"]).astype(float) + (df["ma50"] > df["ma200"]).astype(float),
            "momentum": df["ret20"].rank(pct=True) + df["ret60"].rank(pct=True),
            "risk": (1 - df["volatility20"].rank(pct=True)) + (1 - df["max_drawdown_126"].abs().rank(pct=True)),
            "liquidity": df["dollar_volume_20"].rank(pct=True),
            "relative_strength": df["rel_strength_60"].rank(pct=True),
            "volume_expansion": df["vol_expansion"].rank(pct=True),
        }
        for k, v in components.items():
            df[f"score_{k}"] = v
        raw = sum(components.values())
        df["score_raw"] = raw
        df["score"] = ((raw - raw.min()) / (raw.max() - raw.min() + 1e-12) * 100).round(2)
        ranked = df.sort_values("score", ascending=False).reset_index(drop=True)
        return ranked.head(top_n) if top_n else ranked
