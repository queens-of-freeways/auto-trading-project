import os
import pandas as pd
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta
from strategy import generate_signals

load_dotenv()

trading_client = TradingClient(os.getenv('ALPACA_API_KEY'), os.getenv('ALPACA_SECRET_KEY'), paper=True)
data_client = StockHistoricalDataClient(os.getenv('ALPACA_API_KEY'), os.getenv('ALPACA_SECRET_KEY'))

def execute_trades():
    universe = pd.read_csv("universe.csv")
    symbols = universe["Symbol"].unique().tolist()

    requests_params = StockBarsRequest(
        symbol_or_symbols=symbols,
        timeframe=TimeFrame.Day,
        Start=datetime.now() - timedelta(days=150)
    )
    bars = data_client.get_stock_bars(requests_params).df

    positions = {p.symbol: p for p in trading_client.get_all_positions()}

    for ticker in symbols:
        try:
            ticker_bars = bars.loc[ticker].copy()
            df = generate_signals(ticker_bars)
            latest_signal = df['signal'].iloc[-1]

            if latest_signal == 1 and ticker not in positions:
                print(f"🚀 BUY SIGNAL: {ticker}")
                trading_client.submit_order(MarketOrderRequest(
                    symbol=ticker,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.GTC,
                ))

            elif latest_signal == -1 and ticker in positions:
                print(f"📉 SELL SIGNAL: {ticker}")
                trading_client.close_position(ticker)

        except Exception as e:
            print(f"Could not process {ticker}: {e}")

if __name__ == "__main__":
    execute_trades()