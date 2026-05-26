from __future__ import annotations

from abc import ABC, abstractmethod


class PositionSizer(ABC):
    @abstractmethod
    def size(self, equity: float, price: float, risk_scale: float = 1.0) -> int:
        ...


class FixedFractionSizer(PositionSizer):
    def __init__(self, fraction: float, max_position_fraction: float) -> None:
        self.fraction = fraction
        self.max_position_fraction = max_position_fraction

    def size(self, equity: float, price: float, risk_scale: float = 1.0) -> int:
        target_value = equity * min(self.fraction * risk_scale, self.max_position_fraction)
        return max(int(target_value // price), 0)
