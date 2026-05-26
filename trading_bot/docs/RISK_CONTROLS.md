# RISK_CONTROLS
Default guardrails:
- max risk per trade: 2%
- max position size: 10%
- max portfolio exposure: 100%
- max daily loss: 3%
- max drawdown halt: 20%
- consecutive-loss halt: 4
- stop-loss: fixed percent and ATR-proxy path in exits/engine

Orders can be rejected/resized and risk events are logged.
