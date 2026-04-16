import pandas as pd
import numpy as np
from strategy import generate_signals


def run_backtest():
    df = pd.read_csv("universe_data.csv", parse_dates=["Date"])
    symbols = df["Symbol"].unique()
    all_sharpes = []

    for ticker in symbols:
        ticker_df = df[df["Symbol"] == ticker].copy().set_index("Date")
        ticker_df = generate_signals(ticker_df)

        # Calculate Returns
        ticker_df["ret"] = ticker_df["Close"].pct_change()
        ticker_df["strat_ret"] = ticker_df["signal"].shift(1) * ticker_df["ret"]

        if ticker_df["strat_ret"].std() > 0:
            sharpe = (
                ticker_df["strat_ret"].mean() / ticker_df["strat_ret"].std()
            ) * np.sqrt(252)
            all_sharpes.append(sharpe)

    avg_score = np.mean(all_sharpes) if all_sharpes else 0
    print(f"FINAL_SCORE: {avg_score:.4f}")
    return avg_score


if __name__ == "__main__":
    run_backtest()
