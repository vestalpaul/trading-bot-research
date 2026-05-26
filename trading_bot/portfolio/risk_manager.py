from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from trading_bot.data.models import Order, RiskEvent


@dataclass(slots=True)
class RiskConfig:
    max_risk_per_trade: float = 0.02
    max_position_fraction: float = 0.1
    max_portfolio_exposure: float = 1.0
    max_daily_loss: float = 0.03
    max_drawdown_halt: float = 0.2
    consecutive_loss_halt: int = 4


class RiskManager(ABC):
    @abstractmethod
    def evaluate_order(self, order: Order, equity: float, exposure: float, price: float) -> tuple[Order | None, RiskEvent | None]:
        ...


class SimpleRiskManager(RiskManager):
    def __init__(self, cfg: RiskConfig) -> None:
        self.cfg = cfg

    def evaluate_order(self, order: Order, equity: float, exposure: float, price: float) -> tuple[Order | None, RiskEvent | None]:
        max_qty = int((equity * self.cfg.max_position_fraction) // price)
        if exposure >= self.cfg.max_portfolio_exposure:
            return None, RiskEvent(order.created_at, order.symbol, "max portfolio exposure reached", "rejected")
        if order.quantity > max_qty:
            if max_qty <= 0:
                return None, RiskEvent(order.created_at, order.symbol, "position too large", "rejected")
            order.quantity = max_qty
            return order, RiskEvent(order.created_at, order.symbol, "position reduced by risk manager", "resized")
        return order, None
