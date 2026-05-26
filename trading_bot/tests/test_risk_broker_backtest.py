import pandas as pd

from trading_bot.backtest.costs import apply_costs
from trading_bot.backtest.engine import BacktestConfig, BacktestEngine
from trading_bot.cli.main import build_features, synthetic_data
from trading_bot.data.models import Order
from trading_bot.execution.paper_broker import PaperBroker
from trading_bot.portfolio.risk_manager import RiskConfig, SimpleRiskManager
from trading_bot.portfolio.sizing import FixedFractionSizer
from trading_bot.signals.entries import TopRankEntryRule
from trading_bot.signals.exits import CompositeExitRule
from trading_bot.signals.ranking import RiskAdjustedRanker
from trading_bot.storage.experiment_log import JsonExperimentLogger


def test_cost_model():
    fill, fee, slip = apply_costs(100, 10, "buy", 1, 2)
    assert fill > 100 and fee > 0 and slip > 0


def test_risk_manager_rejection():
    rm = SimpleRiskManager(RiskConfig(max_position_fraction=0.01, max_portfolio_exposure=0.0))
    o, event = rm.evaluate_order(Order("AAA", "buy", 100), equity=100_000, exposure=0.0, price=100)
    assert o is None and event is not None


def test_paper_broker_and_backtest_and_experiment(tmp_path):
    broker = PaperBroker(cash=10_000)
    buy = broker.submit_order(Order("AAA", "buy", 10, created_at=pd.Timestamp("2025-01-01")), 100)
    assert buy is not None
    sell = broker.submit_order(Order("AAA", "sell", 10, created_at=pd.Timestamp("2025-01-02")), 102)
    assert sell is not None

    prices = synthetic_data(["SPY", "AAA", "BBB"], periods=260)
    feats = build_features(prices)
    engine = BacktestEngine(RiskAdjustedRanker(), TopRankEntryRule(30), CompositeExitRule(), FixedFractionSizer(0.1, 0.1), SimpleRiskManager(RiskConfig()), BacktestConfig())
    result = engine.run(prices, feats)
    assert "sharpe_ratio" in result.metrics

    logger = JsonExperimentLogger(root=str(tmp_path))
    path = logger.log({"name": "exp1", "backtest_results": result.metrics})
    assert path.exists()
