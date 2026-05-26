from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from trading_bot.backtest.engine import BacktestConfig, BacktestEngine
from trading_bot.features.technical import DefaultFeaturePipeline
from trading_bot.portfolio.risk_manager import RiskConfig, SimpleRiskManager
from trading_bot.portfolio.sizing import FixedFractionSizer
from trading_bot.signals.entries import TopRankEntryRule
from trading_bot.signals.exits import CompositeExitRule
from trading_bot.signals.ranking import RiskAdjustedRanker
from trading_bot.storage.experiment_log import JsonExperimentLogger
from trading_bot.universe.filters import LiquidityUniverseSelector


def synthetic_data(symbols: list[str], periods: int = 260) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    dates = pd.bdate_range(end=pd.Timestamp("2025-12-31"), periods=periods)
    rows = []
    for i, s in enumerate(symbols):
        px = 50 + i * 20
        for d in dates:
            ret = rng.normal(0.0005, 0.02)
            px = max(2.0, px * (1 + ret))
            rows.append({"timestamp": d, "symbol": s, "open": px * 0.99, "high": px * 1.01, "low": px * 0.98, "close": px, "volume": int(1_000_000 + rng.normal(0, 100_000))})
    return pd.DataFrame(rows)


def build_features(prices: pd.DataFrame, benchmark_symbol: str = "SPY") -> dict[pd.Timestamp, pd.DataFrame]:
    pipe = DefaultFeaturePipeline()
    selector = LiquidityUniverseSelector(5.0, 2_000_000, 200)
    out = {}
    for dt in sorted(prices["timestamp"].unique()):
        eligible = selector.select(prices, dt)
        if benchmark_symbol not in prices["symbol"].unique() or len(eligible) == 0:
            continue
        bench = prices[prices["symbol"] == benchmark_symbol]
        feats = pipe.transform(prices[prices["symbol"].isin(eligible)], bench, dt)
        if not feats.empty:
            out[dt] = feats
    return out


def cmd_rank(config_path: str) -> None:
    cfg = yaml.safe_load(Path(config_path).read_text())
    prices = synthetic_data(cfg["universe"]) if cfg.get("use_synthetic_data", True) else synthetic_data(cfg["universe"])
    features_by_date = build_features(prices, cfg.get("benchmark", "SPY"))
    latest = max(features_by_date)
    ranked = RiskAdjustedRanker().rank(features_by_date[latest], top_n=cfg.get("top_n", 10))
    print(ranked[["symbol", "score", "score_trend", "score_momentum", "score_risk", "score_relative_strength"]].to_string(index=False))


def cmd_backtest(config_path: str) -> None:
    cfg = yaml.safe_load(Path(config_path).read_text())
    prices = synthetic_data(cfg["universe"])
    feats = build_features(prices, cfg.get("benchmark", "SPY"))
    engine = BacktestEngine(RiskAdjustedRanker(), TopRankEntryRule(40), CompositeExitRule(), FixedFractionSizer(0.1, 0.1), SimpleRiskManager(RiskConfig()), BacktestConfig(initial_cash=cfg.get("initial_cash", 100000), top_n=cfg.get("top_n", 5)))
    result = engine.run(prices, feats)
    out = Path(cfg.get("output_dir", "outputs"))
    out.mkdir(exist_ok=True)
    result.equity_curve.to_csv(out / "equity_curve.csv", index=False)
    pd.DataFrame([t.__dict__ for t in result.trades]).to_csv(out / "trades.csv", index=False)
    print(result.metrics)


def cmd_paper(config_path: str) -> None:
    print("Paper mode uses simulation-only broker. No live orders are sent.")
    cmd_backtest(config_path)


def cmd_init_experiment(name: str) -> None:
    path = JsonExperimentLogger().log({"name": name, "hypothesis_name": name, "universe": "US Equities + ETFs", "data_source": "synthetic", "data_version": "local synthetic v1", "feature_set": ["trend", "momentum", "risk", "liquidity"], "strategy_parameters": {"top_n": 5}, "transaction_cost_model": "1 bps commission", "slippage_assumptions": "2 bps", "train_test": "single-period backtest", "num_trials": 1, "selected_metrics": ["sharpe_ratio", "max_drawdown"], "backtest_results": {}, "failure_notes": "", "decision_outcome": "pending"})
    print(f"Created experiment record at {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ["rank", "backtest", "paper"]:
        p = sub.add_parser(name)
        p.add_argument("--config", default="trading_bot/config/example.yaml")
    p = sub.add_parser("init-experiment")
    p.add_argument("--name", required=True)
    args = parser.parse_args()
    if args.cmd == "rank":
        cmd_rank(args.config)
    elif args.cmd == "backtest":
        cmd_backtest(args.config)
    elif args.cmd == "paper":
        cmd_paper(args.config)
    else:
        cmd_init_experiment(args.name)


if __name__ == "__main__":
    main()
