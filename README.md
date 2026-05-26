# trading-bot-research

Research-first, **simulation-only** modular trading bot scaffold for U.S. equities/ETFs.

## Safety
- No live order routing.
- No broker credentials/secrets.
- Paper broker only.

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

## Commands
```bash
python -m trading_bot.cli.main rank --config trading_bot/config/example.yaml
python -m trading_bot.cli.main backtest --config trading_bot/config/example.yaml
python -m trading_bot.cli.main paper --config trading_bot/config/example.yaml
python -m trading_bot.cli.main init-experiment --name momentum_ranker_v1
```

## Testing
```bash
pytest
ruff check .
```
