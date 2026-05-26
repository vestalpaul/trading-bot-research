from __future__ import annotations


def apply_costs(price: float, qty: int, side: str, bps_commission: float, bps_slippage: float) -> tuple[float, float, float]:
    notional = price * qty
    fee = notional * (bps_commission / 10_000)
    slip_val = notional * (bps_slippage / 10_000)
    slip_per_share = slip_val / max(qty, 1)
    fill_price = price + slip_per_share if side == "buy" else price - slip_per_share
    return fill_price, fee, slip_val
