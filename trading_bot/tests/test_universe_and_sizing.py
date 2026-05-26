import pandas as pd

from trading_bot.cli.main import synthetic_data
from trading_bot.portfolio.sizing import FixedFractionSizer
from trading_bot.universe.filters import LiquidityUniverseSelector


def test_liquidity_filter_and_position_sizing():
    prices = synthetic_data(["SPY", "AAA"], periods=220)
    selector = LiquidityUniverseSelector(5.0, 1_000_000, 200)
    symbols = selector.select(prices, prices["timestamp"].max())
    assert "SPY" in symbols
    qty = FixedFractionSizer(0.1, 0.1).size(100_000, 100)
    assert qty == 100
