# Auto‑Trading Project

A small Python framework for building, back‑testing, and (optionally) live‑trading systematic strategies.

## Features
- **Dynamic universe**: Pulls tradable US equity symbols from Alpaca, downloads price data via Yahoo Finance, and enriches it with trailing P/E ratios.
- **Strategy engine**: `strategy.py` contains a simple SMA‑plus‑PE‑ratio signal generator (auto‑optimised via `auto_optimize.py`).
- **Back‑test**: `backtest.py` and `run_backtest.py` compute daily returns and the Sharpe ratio.
- **Optimizer**: Exhaustive search over moving‑average, Bollinger‑Band and RSI variants; best config persisted to `best_config.json`.
- **Sentiment**: `live_sentiment.py` fetches recent news headlines and computes a lightweight sentiment score.
- **Live trade scaffolding**: `live_trade.py` (and the orchestrator) demonstrate how to place orders via Alpaca.
- **Tests**: Basic unittest coverage in `tests/`.

## Quick start
```bash
# Install dependencies
pip install -r requirements.txt

# Refresh the universe (price + PE data)
python prepare.py

# Run a back‑test
python run_backtest.py

# Optimise the strategy
python auto_optimize.py
```
