import pandas as pd
import numpy as np
from strategy import generate_signals


def run_portfolio_backtest():
    df = pd.read_csv("universe.csv", parse_dates=["Date"])
    symbols = df["Symbol"].unique()
    all_sharpes = []

    for ticker in symbols:
        ticker_df = df[df["Symbol"] == ticker].copy().set_index("Date")
        ticker_df = generate_signals(ticker_df)

        ticker_df["ret"] = ticker_df["Close"].pct_change()
        ticker_df["strat_ret"] = ticker_df["signal"].shift(1) * ticker_df["ret"]

        if ticker_df["strat_ret"].std() > 0:
            s = (
                ticker_df["strat_ret"].mean() / ticker_df["strat_ret"].std()
            ) * np.sqrt(252)
            all_sharpes.append(s)

    avg_sharpe = np.mean(all_sharpes) if all_sharpes else 0
    print(f"Sharpe Ratio: {avg_sharpe:.4f}")
    return avg_sharpe


if __name__ == "__main__":
    run_portfolio_backtest()
