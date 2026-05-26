from __future__ import annotations

import pandas as pd


def stop_price_from_atr(close: float, atr: float, multiple: float) -> float:
    return float(close - atr * multiple)


def trailing_drawdown(equity_curve: pd.Series) -> pd.Series:
    peak = equity_curve.cummax()
    return equity_curve / peak - 1.0
