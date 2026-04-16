import os
from re import search

import yfinance as yf
import pandas as pd
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

api_key = os.getenv("ALPACA_API_KEY")
api_secret = os.getenv("ALPACA_SECRET_KEY")
is_paper = os.getenv("ALPACA_PAPER_TRADE", "true").lower() == "true"
print(
    f"Loaded Alpaca credentials: key={'***' if not api_key else api_key[:4]}, secret={'***' if not api_secret else 'set'}"
)

client = TradingClient(api_key, api_secret, paper=is_paper)


def update_universe():
    """Fetch a dynamic list of tradable US equities, download price data,
    enrich it with fundamentals (PE Ratio), and write to CSV files.
    """
    # 1️⃣ Get tradable symbols from Alpaca (limit to 50 for speed)
    search = GetAssetsRequest(asset_class=AssetClass.US_EQUITY)
    assets = client.get_all_assets(search)
    symbols = [
        a.symbol
        for a in assets
        if a.tradable and a.status == "active" and a.exchange in ["NASDAQ", "NYSE"]
    ][:50]

    print(f"Syncing data for {len(symbols)} tickers...")

    # 2️⃣ Download price data (Close) for the last 2 years
    price_data = (
        yf.download(symbols, period="2y", interval="1d")["Close"].stack().reset_index()
    )
    price_data.columns = ["Date", "Symbol", "Close"]

    # 3️⃣ Pull fundamental info (trailing P/E ratio) for each ticker
    fundamentals = []
    for s in symbols:
        try:
            pe = yf.Ticker(s).info.get("trailingPE", 0)
            fundamentals.append({"Symbol": s, "PE_Ratio": pe})
        except Exception:
            fundamentals.append({"Symbol": s, "PE_Ratio": 0})
    fundamentals_df = pd.DataFrame(fundamentals)

    # 4️⃣ Merge price and fundamentals
    merged = price_data.merge(fundamentals_df, on="Symbol")

    # 5️⃣ Write CSVs (price‑only for backward compatibility, enriched for advanced back‑tests)
    merged.to_csv("universe_data.csv", index=False)
    price_data.to_csv("universe.csv", index=False)
    print("Universe updated (price + PE_Ratio).")


if __name__ == "__main__":
    update_universe()
