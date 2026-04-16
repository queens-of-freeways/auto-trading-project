import pandas as pd


def generate_signals(df):
    """
    Auto‑generated strategy
    """
    df['SMA'] = df['Close'].rolling(window=20).mean()
    df['STD'] = df['Close'].rolling(window=20).std()
    df['Upper'] = df['SMA'] + 1.5 * df['STD']
    df['Lower'] = df['SMA'] - 1.5 * df['STD']
    df['signal'] = 0
    df.loc[df['Close'] < df['Lower'], 'signal'] = 1
    df.loc[df['Close'] > df['Upper'], 'signal'] = -1
    return df
