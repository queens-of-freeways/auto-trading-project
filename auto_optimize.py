import os
import subprocess
import re
import sys
import json

# Path definitions (use raw strings to avoid escape issues)
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
STRATEGY_PATH = os.path.join(PROJECT_ROOT, "strategy.py")
BACKTEST_CMD = [sys.executable, os.path.join(PROJECT_ROOT, "backtest.py")]

# Candidate strategy configurations
candidates = [
    # Moving Average variants
    {"type": "ma", "short": 5, "long": 20},
    {"type": "ma", "short": 10, "long": 30},
    {"type": "ma", "short": 15, "long": 50},
    {"type": "ma", "short": 20, "long": 50},
    {"type": "ma", "short": 30, "long": 60},
    # Bollinger Band variants (std multipliers)
    {"type": "boll", "window": 20, "std": 1.0},
    {"type": "boll", "window": 20, "std": 1.5},
    {"type": "boll", "window": 20, "std": 2.0},
    {"type": "boll", "window": 20, "std": 2.5},
    {"type": "boll", "window": 20, "std": 3.0},
    # RSI variants
    {"type": "rsi", "period": 14, "low": 30, "high": 70},
    {"type": "rsi", "period": 14, "low": 20, "high": 80},
    {"type": "rsi", "period": 14, "low": 40, "high": 60},
    # Combined MA + RSI variants
    {
        "type": "combined",
        "ma_short": 10,
        "ma_long": 30,
        "rsi_period": 14,
        "rsi_low": 30,
        "rsi_high": 70,
    },
    {
        "type": "combined",
        "ma_short": 5,
        "ma_long": 20,
        "rsi_period": 14,
        "rsi_low": 30,
        "rsi_high": 70,
    },
]


def generate_code(cfg):
    """Return the full content for strategy.py based on cfg dict."""
    header = "import pandas as pd\n\n\n"
    func_start = (
        'def generate_signals(df):\n    """\n    Auto‑generated strategy\n    """\n'
    )
    body = ""
    if cfg["type"] == "ma":
        body = (
            f"    df['SMA_short'] = df['Close'].rolling(window={cfg['short']}).mean()\n"
            f"    df['SMA_long'] = df['Close'].rolling(window={cfg['long']}).mean()\n"
            "    df['signal'] = 0\n"
            "    df.loc[df['SMA_short'] > df['SMA_long'], 'signal'] = 1\n"
            "    df.loc[df['SMA_short'] < df['SMA_long'], 'signal'] = -1\n"
        )
    elif cfg["type"] == "boll":
        body = (
            f"    df['SMA'] = df['Close'].rolling(window={cfg['window']}).mean()\n"
            f"    df['STD'] = df['Close'].rolling(window={cfg['window']}).std()\n"
            f"    df['Upper'] = df['SMA'] + {cfg['std']} * df['STD']\n"
            f"    df['Lower'] = df['SMA'] - {cfg['std']} * df['STD']\n"
            "    df['signal'] = 0\n"
            "    df.loc[df['Close'] < df['Lower'], 'signal'] = 1\n"
            "    df.loc[df['Close'] > df['Upper'], 'signal'] = -1\n"
        )
    elif cfg["type"] == "rsi":
        body = (
            f"    delta = df['Close'].diff()\n"
            "    up = delta.clip(lower=0)\n"
            "    down = -delta.clip(upper=0)\n"
            f"    roll_up = up.rolling(window={cfg['period']}).mean()\n"
            f"    roll_down = down.rolling(window={cfg['period']}).mean()\n"
            "    rs = roll_up / roll_down\n"
            "    df['RSI'] = 100 - (100 / (1 + rs))\n"
            "    df['signal'] = 0\n"
            f"    df.loc[df['RSI'] < {cfg['low']}, 'signal'] = 1\n"
            f"    df.loc[df['RSI'] > {cfg['high']}, 'signal'] = -1\n"
        )
    elif cfg["type"] == "combined":
        body = (
            f"    df['SMA_short'] = df['Close'].rolling(window={cfg['ma_short']}).mean()\n"
            f"    df['SMA_long'] = df['Close'].rolling(window={cfg['ma_long']}).mean()\n"
            "    delta = df['Close'].diff()\n"
            "    up = delta.clip(lower=0)\n"
            "    down = -delta.clip(upper=0)\n"
            f"    roll_up = up.rolling(window={cfg['rsi_period']}).mean()\n"
            f"    roll_down = down.rolling(window={cfg['rsi_period']}).mean()\n"
            "    rs = roll_up / roll_down\n"
            "    df['RSI'] = 100 - (100 / (1 + rs))\n"
            "    df['signal'] = 0\n"
            f"    df.loc[(df['SMA_short'] > df['SMA_long']) & (df['RSI'] < {cfg['rsi_low']}), 'signal'] = 1\n"
            f"    df.loc[(df['SMA_short'] < df['SMA_long']) & (df['RSI'] > {cfg['rsi_high']}), 'signal'] = -1\n"
        )
    else:
        raise ValueError("Unsupported config type")

    func_end = "    return df\n"
    return header + func_start + body + func_end


def run_backtest():
    """Execute backtest.py and return the Sharpe ratio as float."""
    try:
        result = subprocess.run(
            BACKTEST_CMD, capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=120
        )
    except subprocess.TimeoutExpired:
        print("Backtest timed out")
        return -float("inf")
    out = result.stdout
    # Find line with Sharpe Ratio
    match = re.search(r"Sharpe Ratio:\s*([\-\d\.]+)", out)
    if match:
        return float(match.group(1))
    else:
        print("Sharpe not found in output")
        return -float("inf")


def main():
    best_sharpe = -float("inf")
    best_code = None
    best_cfg = None
    for idx, cfg in enumerate(candidates, 1):
        code = generate_code(cfg)
        # Write candidate to strategy.py
        with open(STRATEGY_PATH, "w", encoding="utf-8") as f:
            f.write(code)
        sharpe = run_backtest()
        print(
            f"Iteration {idx}/{len(candidates)} – {cfg['type']} – Sharpe: {sharpe:.4f}"
        )
        if sharpe > best_sharpe:
            best_sharpe = sharpe
            best_code = code
            best_cfg = cfg
    # After search, write best version back to strategy.py
    if best_code is not None:
        with open(STRATEGY_PATH, "w", encoding="utf-8") as f:
            f.write(best_code)
        # Persist best configuration to a JSON file for later reference
        best_cfg_path = os.path.join(PROJECT_ROOT, "best_config.json")
        try:
            with open(best_cfg_path, "w", encoding="utf-8") as f:
                json.dump(best_cfg, f, indent=2)
            print(f"Best configuration saved to {best_cfg_path}")
        except Exception as e:
            print(f"Failed to write best config: {e}")
        print("\nBest configuration:", best_cfg)
        print("Best Sharpe:", best_sharpe)
    else:
        print("No valid candidate found")


if __name__ == "__main__":
    main()
