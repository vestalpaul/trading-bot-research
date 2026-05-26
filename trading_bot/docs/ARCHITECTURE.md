# ARCHITECTURE
- `data`: models and source interfaces/adapters.
- `universe`: liquidity and history-based filtering.
- `features`: technical/risk features with no look-ahead.
- `signals`: ranking + entry/exit rules.
- `portfolio`: sizing and risk controls.
- `execution`: simulation-only broker.
- `backtest`: engine, costs, performance metrics.
- `storage`: experiment logging.
- `cli`: rank/backtest/paper/init-experiment commands.
