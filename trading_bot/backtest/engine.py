from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from trading_bot.backtest.metrics import compute_metrics
from trading_bot.data.models import BacktestResult, Order, RiskEvent, Trade
from trading_bot.execution.paper_broker import PaperBroker
from trading_bot.features.risk import stop_price_from_atr


@dataclass
class BacktestConfig:
    initial_cash: float = 100_000
    top_n: int = 5
    rebalance_freq: str = "W-FRI"


class BacktestEngine:
    def __init__(self, ranker, entry_rule, exit_rule, sizer, risk_manager, cfg: BacktestConfig) -> None:
        self.ranker = ranker
        self.entry_rule = entry_rule
        self.exit_rule = exit_rule
        self.sizer = sizer
        self.risk_manager = risk_manager
        self.cfg = cfg

    def run(self, prices: pd.DataFrame, features_by_date: dict[pd.Timestamp, pd.DataFrame]) -> BacktestResult:
        broker = PaperBroker(cash=self.cfg.initial_cash)
        risk_events: list[RiskEvent] = []
        fills = []
        trades: list[Trade] = []
        equity_rows = []
        rebalance_dates = set(pd.date_range(prices["timestamp"].min(), prices["timestamp"].max(), freq=self.cfg.rebalance_freq))

        for dt, day_df in prices.groupby("timestamp"):
            mark = dict(zip(day_df["symbol"], day_df["close"], strict=False))
            # exits
            for sym, pos in list(broker.positions.items()):
                row = day_df[day_df["symbol"] == sym]
                if row.empty:
                    continue
                row = row.iloc[0]
                hold_days = (dt - pos.entry_date).days
                stop = stop_price_from_atr(pos.avg_price, row.get("atr20", 0.0), 2.0)
                if self.exit_rule.should_exit(row, pos.avg_price, hold_days, stop):
                    order = Order(sym, "sell", pos.quantity, created_at=dt)
                    fill = broker.submit_order(order, row["close"])
                    if fill:
                        fills.append(fill)
                        trades.append(Trade(sym, pos.entry_date, dt, pos.quantity, pos.avg_price, fill.fill_price, (fill.fill_price - pos.avg_price) * pos.quantity))
            # entries on rebalance
            if dt in rebalance_dates and dt in features_by_date:
                ranked = self.ranker.rank(features_by_date[dt], top_n=self.cfg.top_n)
                snap = broker.snapshot(mark)
                for _, r in ranked.iterrows():
                    if r["symbol"] in broker.positions or not self.entry_rule.should_enter(r):
                        continue
                    qty = self.sizer.size(snap.equity, r["close"], risk_scale=max(0.1, 1 - r["volatility20"]))
                    if qty <= 0:
                        continue
                    order = Order(r["symbol"], "buy", qty, created_at=dt)
                    reviewed, event = self.risk_manager.evaluate_order(order, snap.equity, snap.exposure, r["close"])
                    if event:
                        risk_events.append(event)
                    if reviewed:
                        fill = broker.submit_order(reviewed, r["close"])
                        if fill:
                            fills.append(fill)
            snap = broker.snapshot(mark)
            equity_rows.append({"timestamp": dt, "equity": snap.equity, "cash": snap.cash, "exposure": snap.exposure})

        curve = pd.DataFrame(equity_rows)
        turnover = sum(abs(f.fill_price * f.quantity) for f in fills) / self.cfg.initial_cash
        avg_exposure = curve["exposure"].mean() if not curve.empty else 0.0
        metrics = compute_metrics(curve, [t.__dict__ for t in trades], avg_exposure, turnover)
        return BacktestResult(metrics, curve, trades, fills, risk_events)
