import os
import pandas as pd
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.data.historical import NewsClient
from alpaca.data.requests import NewsRequest
from strategy import generate_signals

load_dotenv()

t_client = TradingClient(
    os.getenv("ALPACA_API_KEY"), os.getenv("ALPACA_SECRET_KEY"), paper=True
)
n_client = NewsClient(os.getenv("ALPACA_API_KEY"), os.getenv("ALPACA_SECRET_KEY"))


def get_sentiment(ticker):
    """Fetch the last 5 news headlines for a ticker and compute a very simple sentiment score.
    Positive keywords add +1, negative keywords subtract 1.
    """
    try:
        news = n_client.get_news(NewsRequest(symbols=ticker, limit=5))
    except Exception as e:
        print(f"Failed to fetch news for {ticker}: {e}")
        return 0
    score = 0
    for article in news.news:
        text = article.headline.lower()
        if any(word in text for word in ["bullish", "growth", "upgrade", "beat"]):
            score += 1
        if any(word in text for word in ["bearish", "drop", "downgrade", "miss"]):
            score -= 1
    return score


def run_live():
    """Iterate over a small subset of symbols, check sentiment, and (placeholder) execute trade logic.
    The actual order submission is omitted – you can integrate the logic from `live_trade.py` here.
    """
    universe = pd.read_csv("universe_data.csv")
    # Limit to first 10 symbols for safety during testing
    symbols = universe["Symbol"].unique()[:10]

    for ticker in symbols:
        sentiment = get_sentiment(ticker)
        if sentiment < 0:
            print(f"Skipping {ticker} due to negative sentiment (score={sentiment}).")
            continue
        print(f"Processing {ticker} (sentiment score={sentiment}) …")
        # Placeholder: you would pull recent price data, generate signals, and place orders.
        # For now we just demonstrate the sentiment filter.
        # Example: df = ...; signals = generate_signals(df)
        # ... (order submission logic) ...


if __name__ == "__main__":
    run_live()
