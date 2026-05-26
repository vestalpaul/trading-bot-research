from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import pandas as pd


@dataclass(slots=True)
class Bar:
    symbol: str
    timestamp: pd.Timestamp
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(slots=True)
class AssetMetadata:
    symbol: str
    asset_type: str = "equity"
    sector: str | None = None
    exchange: str | None = None


@dataclass(slots=True)
class Signal:
    symbol: str
    timestamp: pd.Timestamp
    score: float
    reason: dict[str, float] = field(default_factory=dict)


@dataclass(slots=True)
class Order:
    symbol: str
    side: str
    quantity: int
    order_type: str = "market"
    limit_price: float | None = None
    stop_price: float | None = None
    created_at: pd.Timestamp = field(default_factory=lambda: pd.Timestamp.utcnow())


@dataclass(slots=True)
class Fill:
    symbol: str
    side: str
    quantity: int
    fill_price: float
    fee: float
    slippage: float
    timestamp: pd.Timestamp


@dataclass(slots=True)
class Position:
    symbol: str
    quantity: int
    avg_price: float
    entry_date: pd.Timestamp


@dataclass(slots=True)
class PortfolioSnapshot:
    timestamp: pd.Timestamp
    cash: float
    equity: float
    exposure: float


@dataclass(slots=True)
class Trade:
    symbol: str
    entry_date: pd.Timestamp
    exit_date: pd.Timestamp
    quantity: int
    entry_price: float
    exit_price: float
    pnl: float


@dataclass(slots=True)
class RiskEvent:
    timestamp: pd.Timestamp
    symbol: str | None
    reason: str
    action: str


@dataclass(slots=True)
class BacktestResult:
    metrics: dict[str, float]
    equity_curve: pd.DataFrame
    trades: list[Trade]
    fills: list[Fill]
    risk_events: list[RiskEvent]


@dataclass(slots=True)
class ExperimentRecord:
    name: str
    created_at: datetime
    params: dict[str, Any]
