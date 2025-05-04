# data_fetcher.py

import yfinance as yf
import pandas as pd

class DataFetcher:
    """
    Handles fetching historical stock data using yfinance.
    """
    def __init__(self):
        """
        Initializes the DataFetcher.
        (Could add configuration later, e.g., for data source)
        """
        print("DataFetcher initialized.")

    def fetch_stock_data(self, ticker, period="1y", interval="1d"):
        """
        Fetches historical stock data for a given ticker.

        Args:
            ticker (str): The stock ticker symbol.
            period (str): The period for which to fetch data
                          (e.g., "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max").
            interval (str): The data interval
                            (e.g., "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo").
                            Note: Intraday data (<1d) is limited to the last 60 days.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the historical data (OHLC, Volume).
                          Index is DatetimeIndex. Returns an empty DataFrame if no data found.

        Raises:
            ValueError: If the ticker symbol is invalid or causes an issue during fetching.
            Exception: For other potential network or yfinance issues.
        """
        print(f"Attempting to fetch data for {ticker} (Period: {period}, Interval: {interval})")
        try:
            stock = yf.Ticker(ticker)
            # Note: yfinance might automatically adjust the period/interval based on availability
            data = stock.history(period=period, interval=interval)

            if data.empty:
                print(f"Warning: No data returned for ticker '{ticker}' with period '{period}'.")
                # Returning empty DataFrame, let caller handle it
                return pd.DataFrame()

            # Optional: Clean data slightly (e.g., remove rows with NaNs if necessary, though yfinance is usually clean)
            # data.dropna(inplace=True)

            print(f"Successfully fetched {len(data)} data points for {ticker}.")
            return data

        except Exception as e:
            # Catching potential errors during the fetch process
            error_message = f"Error fetching data for '{ticker}': {e}"
            print(error_message)
            # Re-raise a more specific error or a generic one
            raise ValueError(error_message) from e