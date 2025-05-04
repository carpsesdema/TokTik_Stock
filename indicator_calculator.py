# indicator_calculator.py

import pandas as pd
import numpy as np # For dummy RSI data

class IndicatorCalculator:
    """
    Provides methods to calculate various technical indicators.
    Uses pandas for calculations where possible.
    """

    def __init__(self):
        """Initializes the IndicatorCalculator."""
        print("IndicatorCalculator initialized.")

    @staticmethod
    def calculate_sma(data: pd.DataFrame, period: int) -> pd.Series:
        """
        Calculates the Simple Moving Average (SMA).

        Args:
            data (pd.DataFrame): DataFrame containing stock data (needs 'Close' column).
            period (int): The lookback period for the SMA.

        Returns:
            pd.Series: Series containing the SMA values, indexed like the input data.
                       Returns an empty Series if input is invalid or period is too large.
        """
        if 'Close' not in data.columns or data.empty or not isinstance(period, int) or period <= 0:
            print("Warning (SMA): Invalid input data or period.")
            return pd.Series(dtype=np.float64)
        if period > len(data):
            print(f"Warning (SMA): Period ({period}) is larger than data length ({len(data)}).")
            return pd.Series(dtype=np.float64) # Or calculate with available data? Returning empty for now.

        print(f"Calculating SMA with period {period}...")
        try:
            sma = data['Close'].rolling(window=period).mean()
            return sma
        except Exception as e:
            print(f"Error calculating SMA: {e}")
            return pd.Series(dtype=np.float64)

    @staticmethod
    def calculate_rsi(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculates the Relative Strength Index (RSI).
        *** Currently returns DUMMY DATA for framework demonstration. ***
        A proper implementation would involve calculating average gains and losses.

        Args:
            data (pd.DataFrame): DataFrame containing stock data (needs 'Close' column).
            period (int): The lookback period for RSI (default 14).

        Returns:
            pd.Series: Series containing the RSI values (0-100), indexed like the input data.
                       Returns dummy data in this version.
        """
        if 'Close' not in data.columns or data.empty or not isinstance(period, int) or period <= 0:
            print("Warning (RSI): Invalid input data or period.")
            return pd.Series(dtype=np.float64)
        if period > len(data):
             print(f"Warning (RSI): Period ({period}) is larger than data length ({len(data)}).")
             # Fallback for dummy data generation
             return pd.Series(np.random.rand(len(data)) * 100, index=data.index, name=f"RSI_{period}_dummy")


        print(f"Calculating RSI with period {period} (using dummy data)...")
        # --- Proper RSI Calculation (Conceptual) ---
        # 1. Calculate price changes (delta)
        # delta = data['Close'].diff()
        # 2. Separate gains and losses
        # gain = delta.where(delta > 0, 0)
        # loss = -delta.where(delta < 0, 0)
        # 3. Calculate average gains and losses (e.g., using Wilder's smoothing or simple rolling mean)
        # avg_gain = gain.rolling(window=period).mean() # Simplified example
        # avg_loss = loss.rolling(window=period).mean() # Simplified example
        # 4. Calculate RS (Relative Strength)
        # rs = avg_gain / avg_loss
        # 5. Calculate RSI
        # rsi = 100 - (100 / (1 + rs))
        # --------------------------------------------

        # *** Using Dummy Data for Now ***
        # Replace this with a real calculation later
        rsi_dummy = pd.Series(np.random.rand(len(data)) * 100, index=data.index, name=f"RSI_{period}_dummy")
        # Add some NaNs at the beginning, similar to real indicators
        rsi_dummy.iloc[:period-1] = np.nan
        return rsi_dummy

    # --- Add methods for other indicators here (e.g., EMA, MACD) ---
    # @staticmethod
    # def calculate_ema(data: pd.DataFrame, period: int) -> pd.Series: ...
    # @staticmethod
    # def calculate_macd(data: pd.DataFrame, fast=12, slow=26, signal=9) -> tuple[pd.Series, pd.Series, pd.Series]: ...