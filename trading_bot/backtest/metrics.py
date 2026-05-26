from __future__ import annotations

import numpy as np
import pandas as pd


def compute_metrics(equity_curve: pd.DataFrame, trades: list[dict], exposure: float, turnover: float) -> dict[str, float]:
    eq = equity_curve["equity"]
    rets = eq.pct_change().dropna()
    total_return = eq.iloc[-1] / eq.iloc[0] - 1
    ann_return = (1 + total_return) ** (252 / max(len(rets), 1)) - 1 if len(rets) else 0.0
    ann_vol = rets.std() * np.sqrt(252) if len(rets) else 0.0
    sharpe = ann_return / ann_vol if ann_vol > 0 else 0.0
    downside = rets[rets < 0].std() * np.sqrt(252) if len(rets) else 0.0
    sortino = ann_return / downside if downside and downside > 0 else 0.0
    dd = eq / eq.cummax() - 1
    pnls = [t["pnl"] for t in trades]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]
    return {
        "total_return": float(total_return),
        "annualized_return": float(ann_return),
        "annualized_volatility": float(ann_vol),
        "sharpe_ratio": float(sharpe),
        "sortino_ratio": float(sortino),
        "max_drawdown": float(dd.min()),
        "win_rate": float(len(wins) / len(pnls)) if pnls else 0.0,
        "avg_win": float(np.mean(wins)) if wins else 0.0,
        "avg_loss": float(np.mean(losses)) if losses else 0.0,
        "exposure": float(exposure),
        "turnover": float(turnover),
        "number_of_trades": float(len(trades)),
    }
