# indicator_calculator.py

import pandas as pd
import numpy as np
import logging # Optional

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class IndicatorCalculator:
    """
    Provides static methods to calculate various technical indicators based on stock data.

    Each calculation method takes a pandas DataFrame (expected to have OHLC columns
    and a DatetimeIndex) and indicator-specific parameters, returning a pandas Series
    with the calculated indicator values, aligned to the original DataFrame's index.
    """

    def __init__(self):
        """
        Initializes the IndicatorCalculator.
        Currently, no state is stored, methods are static.
        """
        print("IndicatorCalculator initialized.")
        # logging.info("IndicatorCalculator initialized.")

    @staticmethod
    def calculate_sma(data: pd.DataFrame, period: int) -> pd.Series:
        """
        Calculates the Simple Moving Average (SMA) of the 'Close' price.

        Args:
            data (pd.DataFrame): DataFrame containing stock data. Must include a 'Close' column
                                 and have a DatetimeIndex.
            period (int): The lookback period (number of bars) for the SMA calculation. Must be > 0.

        Returns:
            pd.Series: A Series containing the calculated SMA values. The index matches the input data's index.
                       Returns an empty Series if input data is invalid, period is non-positive,
                       or the period is larger than the length of the data. NaN values will be present
                       at the beginning of the series (for the first 'period-1' points).
        """
        # --- Input Validation ---
        if not isinstance(data, pd.DataFrame) or data.empty:
            print("Warning (SMA): Input 'data' must be a non-empty DataFrame.")
            # logging.warning("SMA calculation skipped: Invalid data input.")
            return pd.Series(dtype=np.float64) # Return empty series for consistency

        if 'Close' not in data.columns:
            print("Warning (SMA): DataFrame must contain a 'Close' column.")
            # logging.warning("SMA calculation skipped: 'Close' column missing.")
            return pd.Series(dtype=np.float64)

        if not isinstance(period, int) or period <= 0:
            print(f"Warning (SMA): Period must be a positive integer (got {period}).")
            # logging.warning(f"SMA calculation skipped: Invalid period {period}.")
            return pd.Series(dtype=np.float64)

        if period > len(data):
            # Period is longer than the entire dataset
            print(f"Warning (SMA): Period ({period}) is larger than data length ({len(data)}). Returning empty Series.")
            # logging.warning(f"SMA calculation skipped: Period {period} > data length {len(data)}.")
            return pd.Series(dtype=np.float64)

        # --- Calculation ---
        print(f"Calculating SMA with period {period}...")
        # logging.info(f"Calculating SMA(period={period})")
        try:
            # Use pandas rolling mean for efficient calculation
            sma_series = data['Close'].rolling(window=period).mean()
            sma_series.name = f"SMA_{period}" # Assign a descriptive name
            return sma_series
        except Exception as e:
            # Catch potential errors during the rolling calculation
            print(f"Error calculating SMA(period={period}): {e}")
            # logging.error(f"Error calculating SMA(period={period}): {e}", exc_info=True)
            return pd.Series(dtype=np.float64) # Return empty series on error

    @staticmethod
    def calculate_rsi(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculates the Relative Strength Index (RSI).

        *** NOTE: THIS IS CURRENTLY A PLACEHOLDER IMPLEMENTATION ***
        It returns random dummy data for demonstration purposes within the framework.
        A proper implementation requires calculating average gains and losses.

        Args:
            data (pd.DataFrame): DataFrame containing stock data (needs 'Close' column).
            period (int): The lookback period for RSI (default 14). Must be > 0.

        Returns:
            pd.Series: Series containing the RSI values (typically 0-100).
                       Index matches the input data. Contains dummy data in this version.
                       Returns an empty Series on invalid input.
        """
        # --- Input Validation ---
        if not isinstance(data, pd.DataFrame) or data.empty:
            print("Warning (RSI): Input 'data' must be a non-empty DataFrame.")
            # logging.warning("RSI calculation skipped: Invalid data input.")
            return pd.Series(dtype=np.float64)

        if 'Close' not in data.columns:
            print("Warning (RSI): DataFrame must contain a 'Close' column.")
            # logging.warning("RSI calculation skipped: 'Close' column missing.")
            return pd.Series(dtype=np.float64)

        if not isinstance(period, int) or period <= 0:
            print(f"Warning (RSI): Period must be a positive integer (got {period}).")
            # logging.warning(f"RSI calculation skipped: Invalid period {period}.")
            return pd.Series(dtype=np.float64)

        if period >= len(data): # RSI needs at least 'period' bars + 1 for calculation usually
             print(f"Warning (RSI): Period ({period}) is too large for data length ({len(data)}). Returning empty Series.")
             # logging.warning(f"RSI calculation skipped: Period {period} >= data length {len(data)}.")
             return pd.Series(dtype=np.float64)

        print(f"Calculating RSI with period {period} (using DUMMY data)...")
        # logging.info(f"Calculating RSI(period={period}) - DUMMY DATA")

        # --- Proper RSI Calculation Logic (to be implemented later) ---
        # 1. Calculate price changes: delta = data['Close'].diff(1)
        # 2. Separate gains (up) and losses (down): gain = delta.where(delta > 0, 0.0); loss = -delta.where(delta < 0, 0.0)
        # 3. Calculate initial average gain/loss (SMA): avg_gain = gain.rolling(window=period).mean(); avg_loss = loss.rolling(window=period).mean()
        # 4. Calculate subsequent average gain/loss (smoothed, e.g., Wilder's):
        #    For i >= period: avg_gain[i] = (avg_gain[i-1] * (period - 1) + gain[i]) / period
        #    For i >= period: avg_loss[i] = (avg_loss[i-1] * (period - 1) + loss[i]) / period
        # 5. Calculate RS: rs = avg_gain / avg_loss (handle division by zero, replace inf with large number or NaN)
        # 6. Calculate RSI: rsi = 100.0 - (100.0 / (1.0 + rs))
        # rsi_series = ... (result of above calculation)
        # rsi_series.name = f"RSI_{period}"
        # return rsi_series
        # ---------------------------------------------------------------

        # --- Dummy Data Implementation ---
        # Generate random numbers between 0 and 100
        try:
            rsi_dummy = pd.Series(np.random.rand(len(data)) * 100, index=data.index)
            # Introduce NaNs at the beginning, similar to how real indicators behave
            rsi_dummy.iloc[:period] = np.nan # Typically need 'period' values to calculate first RSI
            rsi_dummy.name = f"RSI_{period}_dummy"
            return rsi_dummy
        except Exception as e:
            print(f"Error generating dummy RSI data (period={period}): {e}")
            # logging.error(f"Error generating dummy RSI(period={period}): {e}", exc_info=True)
            return pd.Series(dtype=np.float64)

    # --- Future Indicator Methods ---
    # @staticmethod
    # def calculate_ema(data: pd.DataFrame, period: int) -> pd.Series:
    #     """Calculates the Exponential Moving Average (EMA)."""
    #     # Input validation...
    #     # Calculation: return data['Close'].ewm(span=period, adjust=False).mean()
    #     pass

    # @staticmethod
    # def calculate_macd(data: pd.DataFrame, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> tuple[pd.Series, pd.Series, pd.Series]:
    #     """Calculates Moving Average Convergence Divergence (MACD)."""
    #     # Input validation...
    #     # ema_fast = data['Close'].ewm(span=fast_period, adjust=False).mean()
    #     # ema_slow = data['Close'].ewm(span=slow_period, adjust=False).mean()
    #     # macd_line = ema_fast - ema_slow
    #     # signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    #     # histogram = macd_line - signal_line
    #     # return macd_line, signal_line, histogram
    #     pass