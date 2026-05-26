# PROJECT_STATE
## Goal
Scaffold a modular research/backtest/paper-trading foundation for systematic strategies.
## Target market
U.S. equities and ETFs.
## Timeframe
Daily bars (swing).
## Automation level
Research scanner + backtesting + paper simulation only.
## Current architecture
Data adapters, feature pipeline, ranker, risk manager, paper broker, backtest engine, CLI, tests.
## Accepted decisions
Python-first; pandas/numpy; no live execution.
## Open questions
Walk-forward validation design, sector/correlation model, intraday extension.
## Strategy hypotheses
Risk-adjusted trend/momentum ranking can improve candidate quality.
## Data sources
Synthetic local data default; CSV and yfinance prototype adapters.
## Broker preference
Paper broker in v1; live broker stubs only.
## Risk limits
Position and exposure caps; stop and drawdown controls scaffolded.
## Next milestone
Walk-forward split + richer stop/portfolio constraints.
