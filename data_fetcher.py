# data_fetcher.py

import yfinance as yf
import pandas as pd
import logging # Optional: Use logging for more structured output

# Setup basic logging if you want more detail than print statements
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataFetcher:
    """
    Handles fetching historical stock data using the yfinance library.

    Provides a method to retrieve OHLCV data for a given ticker, period, and interval,
    performing basic validation and error handling.
    """
    def __init__(self):
        """
        Initializes the DataFetcher.
        Currently, no specific configuration is needed at initialization.
        """
        print("DataFetcher initialized.")
        # logging.info("DataFetcher initialized.")

    def fetch_stock_data(self, ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """
        Fetches historical stock data (OHLCV) for a given ticker symbol.

        Args:
            ticker (str): The stock ticker symbol (e.g., "AAPL", "MSFT").
            period (str): The period for which to fetch data.
                          Valid periods: "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max".
                          (Note: yfinance limitations apply, especially for intraday data).
            interval (str): The data interval / frequency.
                            Valid intervals: "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h",
                                             "1d", "5d", "1wk", "1mo", "3mo".
                            (Note: Intraday data <1d often limited to recent history).

        Returns:
            pd.DataFrame: A pandas DataFrame containing the historical OHLCV data.
                          The index is a DatetimeIndex.
                          Returns an empty DataFrame if no data is found for the ticker/period.

        Raises:
            ValueError: If the ticker symbol is empty or causes an issue during fetching
                        (e.g., invalid ticker, network error wrapped by yfinance).
            Exception: For other potential unexpected errors during the process.
        """
        if not ticker:
            raise ValueError("Ticker symbol cannot be empty.")

        print(f"Attempting to fetch data for {ticker} (Period: {period}, Interval: {interval})")
        # logging.info(f"Fetching data: Ticker={ticker}, Period={period}, Interval={interval}")

        try:
            # Instantiate the yfinance Ticker object
            stock_ticker = yf.Ticker(ticker)

            # Fetch historical data using the specified parameters
            # yfinance handles many internal errors, but can still raise exceptions or return empty DataFrames.
            data = stock_ticker.history(period=period, interval=interval)

            if data.empty:
                # It's common for yfinance to return empty if the ticker is valid but has no data for the period/interval.
                # We'll return the empty DataFrame and let the caller decide how to handle it (e.g., show a message).
                print(f"Warning: No data returned by yfinance for ticker '{ticker}' with period='{period}', interval='{interval}'.")
                # logging.warning(f"No data returned for Ticker={ticker}, Period={period}, Interval={interval}")
                return pd.DataFrame() # Return empty DataFrame explicitly

            # --- Data Cleaning (Optional but recommended) ---
            # 1. Check for required columns (yfinance usually provides them, but good practice)
            required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in data.columns for col in required_cols):
                 missing_cols = [col for col in required_cols if col not in data.columns]
                 # Raise an error here as this indicates unexpected data format
                 raise ValueError(f"Fetched data for '{ticker}' is missing required columns: {missing_cols}")

            # 2. Handle potential NaNs (though yfinance data is often quite clean)
            #    Decide on strategy: forward-fill, backward-fill, drop, or leave them.
            #    Dropping rows might be simplest if NaNs are rare.
            initial_rows = len(data)
            data.dropna(subset=required_cols, inplace=True)
            rows_after_na = len(data)
            if initial_rows != rows_after_na:
                print(f"Note: Dropped {initial_rows - rows_after_na} rows with NaN values in OHLCV columns for {ticker}.")
                # logging.info(f"Dropped {initial_rows - rows_after_na} NaN rows for {ticker}")

            if data.empty:
                 # If all rows had NaNs after fetching
                 print(f"Warning: Data for '{ticker}' became empty after removing NaN values.")
                 # logging.warning(f"Data empty after NaN removal for {ticker}")
                 return pd.DataFrame()


            # --- Index Check ---
            # Ensure the index is a DatetimeIndex (crucial for time series operations)
            if not isinstance(data.index, pd.DatetimeIndex):
                # This would be highly unusual for yfinance, indicates a problem.
                raise TypeError(f"Data index for '{ticker}' is not a DatetimeIndex. Type: {type(data.index)}")

            print(f"Successfully fetched and cleaned {len(data)} data points for {ticker}.")
            # logging.info(f"Successfully fetched {len(data)} points for {ticker}")
            return data

        except Exception as e:
            # Catch potential errors from yfinance (e.g., network issues, invalid ticker format issues)
            # or errors from our cleaning steps.
            error_message = f"Error fetching or processing data for '{ticker}' (Period: {period}, Interval: {interval}): {e}"
            print(error_message)
            # logging.error(error_message, exc_info=True) # Log full traceback if using logging

            # Re-raise as a ValueError to signal a fetch/processing problem to the caller.
            # Include the original error message for context.
            raise ValueError(error_message) from e