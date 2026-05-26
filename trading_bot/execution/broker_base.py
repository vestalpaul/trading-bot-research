from __future__ import annotations

from abc import ABC, abstractmethod

from trading_bot.data.models import Fill, Order, PortfolioSnapshot


class BrokerInterface(ABC):
    simulation_only: bool = True

    @abstractmethod
    def submit_order(self, order: Order, price: float) -> Fill | None:
        ...

    @abstractmethod
    def snapshot(self, mark_prices: dict[str, float]) -> PortfolioSnapshot:
        ...
