# finance_app.py

"""
Main application controller module for Ava's Awesome Finance App.
"""

import sys
import pandas as pd
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QStatusBar
)
from PySide6.QtGui import QColor # Needed for pg config
from PySide6.QtCore import Qt
import pyqtgraph as pg
import logging

# --- Import Modular Components ---
# Import UI builder and theme function
from ui_manager import AppUI, apply_dark_theme
# Import core logic components
from data_fetcher import DataFetcher
from chart_manager import ChartManager
from indicator_calculator import IndicatorCalculator

# ---- Main Application Window (Controller) ----
class FinanceApp(QMainWindow):
    """
    The main application window controller.

    Orchestrates UI, data fetching, indicator calculation, and plotting.
    """
    def __init__(self):
        """Initializes the FinanceApp."""
        super().__init__()
        self.setWindowTitle("Ava's Pro Finance App")
        self.resize(1200, 800)

        # Initialize core logic components
        self.data_fetcher = DataFetcher()
        self.indicator_calculator = IndicatorCalculator()
        self.chart_manager = None # Initialized after UI

        # Initialize application state
        self.current_data: pd.DataFrame | None = None
        self.current_ticker: str = ""
        self.indicators_config: list = []
        self.indicator_results: dict = {}

        # Build the UI using the dedicated AppUI class from ui_manager
        # AppUI takes care of creating widgets and layouts
        self.ui = AppUI(self)
        self.ui.setup_ui()

        # Initialize ChartManager using the graphics_widget created by AppUI
        self.chart_manager = ChartManager(self.ui.graphics_widget)

        # Setup Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready. Enter ticker and fetch data.")

        # Connect signals from UI elements (provided by self.ui) to slots
        self._connect_signals()
        # Set the initial valid intervals based on the default period
        self._update_interval_options()

        print("FinanceApp (Controller) initialized successfully!")

    def _connect_signals(self):
        """Connects UI signals to slots."""
        # Access UI elements via self.ui instance
        self.ui.fetch_button.clicked.connect(self._request_fetch_and_plot)
        self.ui.ticker_input.returnPressed.connect(self._request_fetch_and_plot)
        self.ui.period_combo.currentTextChanged.connect(self._update_interval_options)
        self.ui.add_indicator_button.clicked.connect(self._handle_add_indicator_request)
        print("Signal connections established.")

    def _update_interval_options(self):
        """Updates the available intervals based on the selected period."""
        # Get necessary constants/maps from the UI manager
        interval_map = self.ui.get_interval_map()
        valid_intervals_list = self.ui.get_valid_intervals()
        default_interval_const = self.ui.get_default_interval()

        selected_period = self.ui.period_combo.currentText()
        current_interval = self.ui.interval_combo.currentText()
        self.ui.interval_combo.clear()

        allowed_intervals = []
        # Determine allowed intervals based on selected period
        if selected_period in ["1y", "2y", "5y", "10y", "max"]:
            allowed_intervals.extend(interval_map["daily_weekly"])
            allowed_intervals.extend(interval_map["monthly"])
        elif selected_period in ["6mo", "ytd"]:
            allowed_intervals.extend(interval_map["intraday_medium"])
            allowed_intervals.extend(interval_map["daily_weekly"])
            allowed_intervals.extend(interval_map["monthly"])
        elif selected_period in ["1mo", "3mo"]:
            allowed_intervals.extend(interval_map["intraday_short"])
            allowed_intervals.extend(interval_map["intraday_medium"])
            allowed_intervals.extend(interval_map["daily_weekly"])
        else: # 1d, 5d
            allowed_intervals.extend(interval_map["intraday_short"])
            allowed_intervals.extend(interval_map["intraday_medium"])

        # Sort intervals based on typical order (e.g., minutes, hours, days, weeks)
        unique_intervals = sorted(list(set(allowed_intervals)), key=lambda x: (valid_intervals_list.index(x) if x in valid_intervals_list else 999))
        self.ui.interval_combo.addItems(unique_intervals)

        # Restore previous selection or set default
        if current_interval in unique_intervals:
            self.ui.interval_combo.setCurrentText(current_interval)
        elif default_interval_const in unique_intervals:
             self.ui.interval_combo.setCurrentText(default_interval_const)
        elif unique_intervals:
             self.ui.interval_combo.setCurrentIndex(0)

        print(f"Interval options updated for period '{selected_period}': {unique_intervals}")


    # --- Action Slots ---

    def _request_fetch_and_plot(self):
        """Fetches data based on UI selections and triggers plotting."""
        ticker = self.ui.ticker_input.text().strip().upper()
        period = self.ui.period_combo.currentText()
        interval = self.ui.interval_combo.currentText()

        if not ticker or not interval:
            QMessageBox.warning(self, "Input Missing", "Please enter a ticker and select an interval.")
            self.status_bar.showMessage("Fetch aborted: Missing ticker or interval.", 4000)
            return

        print(f"Request received: Ticker={ticker}, Period={period}, Interval={interval}")
        self.status_bar.showMessage(f"Fetching {ticker} ({period} / {interval})...", 0)
        QApplication.processEvents()

        self.current_ticker = ticker
        self.indicators_config = []
        self.indicator_results = {}

        try:
            fetched_data = self.data_fetcher.fetch_stock_data(ticker, period=period, interval=interval)
            self.current_data = fetched_data

            required_cols = ["Open", "High", "Low", "Close", "Volume"]
            if self.current_data.empty or not all(col in self.current_data.columns for col in required_cols):
                 warning_msg = f"No valid OHLCV data found for '{ticker}' ({period}/{interval})."
                 print(warning_msg)
                 self.status_bar.showMessage(warning_msg, 6000)
                 self.chart_manager.clear_chart()
                 self.current_data = None
                 return

            self.status_bar.showMessage(f"Plotting {ticker}...", 0)
            QApplication.processEvents()
            self._recalculate_and_plot_all()
            self.status_bar.showMessage(f"{ticker} ({period}/{interval}) plotted successfully.", 5000)

        except ValueError as ve:
            error_message = f"Data Fetch Error ({ticker}): {ve}"
            print(error_message)
            self.status_bar.showMessage(f"Error fetching {ticker}: Check inputs/network.", 8000)
            QMessageBox.critical(self, "Data Fetch Error", f"Could not fetch data for {ticker}:\n\n{ve}")
            self.current_data = None
            self.chart_manager.clear_chart()
        except Exception as e:
            error_message = f"Unexpected error ({ticker}): {e}"
            print(error_message)
            self.status_bar.showMessage("An unexpected error occurred. Check logs.", 8000)
            QMessageBox.critical(self, "Application Error", f"An unexpected error occurred:\n\n{e}")
            self.current_data = None
            self.chart_manager.clear_chart()

    def _handle_add_indicator_request(self):
        """Handles the 'Add Indicator' button click."""
        if self.current_data is None or self.current_data.empty:
            self.status_bar.showMessage("Cannot add indicator: Fetch stock data first.", 4000)
            return

        indicator_type = self.ui.indicator_combo.currentText()
        period = self.ui.indicator_period_spinbox.value()
        indicator_id = f"{indicator_type.lower()}_{period}"

        if any(ind['id'] == indicator_id for ind in self.indicators_config):
            self.status_bar.showMessage(f"{indicator_type}({period}) is already added.", 3000)
            return

        plot_type = 'overlay' if indicator_type == 'SMA' else 'subplot'
        config = {'id': indicator_id, 'type': indicator_type, 'params': {'period': period}, 'plot_type': plot_type}

        print(f"Adding indicator request: {config}")
        self.indicators_config.append(config)
        self.status_bar.showMessage(f"Added {indicator_type}({period}). Replotting...", 0)
        QApplication.processEvents()

        self._recalculate_and_plot_all()
        self.status_bar.showMessage(f"Indicators updated for {self.current_ticker}.", 4000)


    def _recalculate_and_plot_all(self):
        """Clears chart, plots base data, calculates/plots indicators."""
        if self.current_data is None or self.current_data.empty:
            print("Plotting skipped: No current stock data available.")
            return

        print("Recalculating all indicators and updating plot...")

        self.chart_manager.clear_chart()
        self.chart_manager.plot_stock_data(self.current_data, self.current_ticker)

        if self.chart_manager.price_plot is None:
            print("Base data plotting failed, skipping indicators.")
            self.status_bar.showMessage("Error plotting base data.", 5000)
            return

        self.indicator_results.clear()
        next_subplot_row = 2

        for config in self.indicators_config:
            indicator_id = config['id']
            indicator_type = config['type']
            params = config['params']
            plot_type = config['plot_type']
            calculated_data = None

            try:
                if indicator_type == 'SMA':
                    calculated_data = self.indicator_calculator.calculate_sma(self.current_data, params['period'])
                elif indicator_type == 'RSI':
                    calculated_data = self.indicator_calculator.calculate_rsi(self.current_data, params['period'])

                if calculated_data is not None and not calculated_data.empty:
                    self.indicator_results[indicator_id] = calculated_data
                    name = f"{indicator_type}({params['period']})"
                    if plot_type == 'overlay':
                        color = 'orange' if 'sma' in indicator_id else 'purple'
                        self.chart_manager.add_overlay_indicator(indicator_id, calculated_data, name, color, width=2)
                    elif plot_type == 'subplot':
                        self.chart_manager.add_subplot_indicator(indicator_id, calculated_data, name, indicator_type, next_subplot_row, color='cyan')
                        next_subplot_row += 1
                else:
                     print(f"Indicator {indicator_id} calculation returned no data.")

            except Exception as e:
                error_msg = f"Error processing indicator {indicator_id}: {e}"
                print(error_msg)
                self.status_bar.showMessage(f"Error with indicator {indicator_id}.", 5000)

        print("Recalculation and plotting complete.")


# ---- Application Entry Point ----
def main():
    """Initializes and runs the Qt application."""
    print("Starting Ava's Pro Finance App...")
    try:
        if hasattr(Qt, 'AA_EnableHighDpiScaling'): QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'): QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    except AttributeError: print("Note: High DPI attributes not available.")

    app = QApplication(sys.argv)
    apply_dark_theme(app) # Apply theme using function from ui_manager
    pg.setConfigOption('background', QColor(40, 40, 40))
    pg.setConfigOption('foreground', 'w')

    window = FinanceApp()
    window.showMaximized()

    print("Entering the main event loop...")
    exit_code = app.exec()
    print(f"Application finished with exit code: {exit_code}")
    sys.exit(exit_code)

if __name__ == "__main__":
    print("-" * 60)
    print("Requires: PySide6, yfinance, pyqtgraph, pandas, numpy, pytz")
    print("Files: finance_app.py, ui_manager.py, data_fetcher.py, chart_manager.py, indicator_calculator.py") # Added ui_manager.py
    print("Ensure virtual environment is active and all files are in the same directory.")
    print("-" * 60)
    main()