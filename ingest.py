import yfinance as yf
import pandas as pd
import sys

TICKERS = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS"]

def fetch_data(ticker_list, period="1y"):
    print(f"Fetching data for: {ticker_list}")
    raw = yf.download(ticker_list, period=period, interval="1d", group_by="ticker")

    if raw.empty:
        print("FATAL: yfinance returned an empty DataFrame. Aborting.")
        sys.exit(1)

    frames = []
    for ticker in ticker_list:
        if ticker not in raw.columns.get_level_values(0):
            print(f"WARNING: {ticker} missing from response entirely. Skipping.")
            continue
        sub = raw[ticker].copy()
        sub["Ticker"] = ticker
        sub = sub.reset_index()
        frames.append(sub)

    if not frames:
        print("FATAL: no ticker data survived flattening. Aborting.")
        sys.exit(1)

    long_df = pd.concat(frames, ignore_index=True)
    return long_df

def validate(df, expected_tickers):
    fetched_tickers = set(df["Ticker"].unique())
    missing = set(expected_tickers) - fetched_tickers
    if missing:
        print(f"WARNING: no data at all for: {missing}")

    null_counts = df[["Open", "High", "Low", "Close"]].isnull().sum()
    if null_counts.sum() > 0:
        print(f"WARNING: null values found:\n{null_counts}")

    rows_per_ticker = df.groupby("Ticker").size()
    print("\nRows fetched per ticker:")
    print(rows_per_ticker)

    if rows_per_ticker.min() < 200:
        print("WARNING: some tickers have suspiciously few rows for a 1y daily pull. Check manually.")

    return len(missing) == 0

if __name__ == "__main__":
    df = fetch_data(TICKERS)
    ok = validate(df, TICKERS)

    print("\nSample rows:")
    print(df.head())
    print("\nShape:", df.shape)

    df.to_csv("raw_market_data.csv", index=False)
    print(f"\nSaved to raw_market_data.csv. Validation passed: {ok}")
