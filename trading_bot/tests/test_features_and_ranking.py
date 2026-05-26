import pandas as pd

from trading_bot.cli.main import build_features, synthetic_data
from trading_bot.signals.ranking import RiskAdjustedRanker


def test_feature_pipeline_and_ranking_output():
    prices = synthetic_data(["SPY", "AAA", "BBB"], periods=260)
    feats = build_features(prices)
    latest = feats[max(feats)]
    assert {"ma20", "ret60", "volatility20", "rel_strength_60"}.issubset(set(latest.columns))
    ranked = RiskAdjustedRanker().rank(latest)
    assert ranked["score"].between(0, 100).all()
