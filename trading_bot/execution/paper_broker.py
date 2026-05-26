from __future__ import annotations

from trading_bot.backtest.costs import apply_costs
from trading_bot.data.models import Fill, Order, PortfolioSnapshot, Position
from trading_bot.execution.broker_base import BrokerInterface


class PaperBroker(BrokerInterface):
    simulation_only = True

    def __init__(self, cash: float = 100_000, commission_bps: float = 1.0, slippage_bps: float = 2.0) -> None:
        self.cash = cash
        self.commission_bps = commission_bps
        self.slippage_bps = slippage_bps
        self.positions: dict[str, Position] = {}

    def submit_order(self, order: Order, price: float) -> Fill | None:
        fill_price, fee, slip = apply_costs(price, order.quantity, order.side, self.commission_bps, self.slippage_bps)
        notional = fill_price * order.quantity
        if order.side == "buy":
            if self.cash < notional + fee:
                return None
            self.cash -= notional + fee
            pos = self.positions.get(order.symbol)
            if pos:
                new_qty = pos.quantity + order.quantity
                avg = (pos.avg_price * pos.quantity + fill_price * order.quantity) / new_qty
                self.positions[order.symbol] = Position(order.symbol, new_qty, avg, pos.entry_date)
            else:
                self.positions[order.symbol] = Position(order.symbol, order.quantity, fill_price, order.created_at)
        else:
            pos = self.positions.get(order.symbol)
            if not pos or pos.quantity < order.quantity:
                return None
            self.cash += notional - fee
            left = pos.quantity - order.quantity
            if left == 0:
                del self.positions[order.symbol]
            else:
                self.positions[order.symbol] = Position(order.symbol, left, pos.avg_price, pos.entry_date)
        return Fill(order.symbol, order.side, order.quantity, fill_price, fee, slip, order.created_at)

    def snapshot(self, mark_prices: dict[str, float]) -> PortfolioSnapshot:
        market_val = sum(mark_prices.get(sym, 0.0) * pos.quantity for sym, pos in self.positions.items())
        equity = self.cash + market_val
        exposure = market_val / equity if equity > 0 else 0.0
        import pandas as pd

        return PortfolioSnapshot(pd.Timestamp.utcnow(), self.cash, equity, exposure)
