# finance_app.py

import sys
import pandas as pd # Keep pandas import if used elsewhere, or remove if only needed by submodules
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox,
    QComboBox, QSpinBox # Added for indicator UI
)
import pyqtgraph as pg

# Import our modular components
from data_fetcher import DataFetcher
from chart_manager import ChartManager
from indicator_calculator import IndicatorCalculator # New import

# ---- Main Application Window ----
class FinanceApp(QMainWindow):
    """
    Main window class for the Finance Analysis Application.
    Coordinates UI, data fetching, indicator calculation, and charting.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ava's Awesome Finance App - Indicator Framework")
        self.resize(950, 800) # Increased size for indicator controls/plots

        # Instantiate core components
        self.data_fetcher = DataFetcher()
        self.indicator_calculator = IndicatorCalculator()
        self.chart_manager = None # Initialized in _setup_ui

        # Application state
        self.current_data = None
        self.current_ticker = ""
        # List to store configurations of added indicators
        # Example: {'id': 'sma_20', 'type': 'SMA', 'params': {'period': 20}, 'plot_type': 'overlay'}
        self.indicators_config = []
        # Dictionary to store calculated indicator data series {indicator_id: pd.Series}
        self.indicator_results = {}

        # UI Setup
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        self._setup_ui() # Creates UI and initializes ChartManager
        self._connect_signals()

        print("FinanceApp initialized successfully!")

    def _setup_ui(self):
        """Creates and arranges UI widgets."""
        print("Setting up UI elements...")

        # --- Input Area ---
        input_layout = QHBoxLayout()
        self.ticker_label = QLabel("Ticker Symbol:")
        self.ticker_input = QLineEdit()
        self.ticker_input.setPlaceholderText("e.g., AAPL, MSFT, ^GSPC")
        self.fetch_button = QPushButton("Fetch & Plot Data")
        input_layout.addWidget(self.ticker_label)
        input_layout.addWidget(self.ticker_input)
        input_layout.addWidget(self.fetch_button)

        # --- Chart Area ---
        self.graphics_widget = pg.GraphicsLayoutWidget(show=True)
        self.graphics_widget.setMinimumHeight(400) # Base height, will grow with subplots

        # Initialize ChartManager now that graphics_widget exists
        self.chart_manager = ChartManager(self.graphics_widget)

        # --- Indicator Control Area ---
        indicator_layout = QHBoxLayout()
        indicator_layout.addWidget(QLabel("Indicator:"))

        self.indicator_combo = QComboBox()
        self.indicator_combo.addItems(["SMA", "RSI"]) # Add more indicators here later
        indicator_layout.addWidget(self.indicator_combo)

        indicator_layout.addWidget(QLabel("Period:"))
        self.indicator_period_spinbox = QSpinBox()
        self.indicator_period_spinbox.setRange(1, 500) # Sensible range
        self.indicator_period_spinbox.setValue(14) # Default value
        indicator_layout.addWidget(self.indicator_period_spinbox)

        self.add_indicator_button = QPushButton("Add Indicator")
        indicator_layout.addWidget(self.add_indicator_button)
        indicator_layout.addStretch() # Push controls to the left

        # --- Assemble Main Layout ---
        self.main_layout.addLayout(input_layout)
        self.main_layout.addWidget(self.graphics_widget, stretch=1) # Chart area takes bulk space
        self.main_layout.addLayout(indicator_layout) # Indicator controls at the bottom

        print("UI setup complete.")

    def _connect_signals(self):
        """Connects UI signals to application slots."""
        self.fetch_button.clicked.connect(self._request_fetch_and_plot)
        self.ticker_input.returnPressed.connect(self._request_fetch_and_plot)
        self.add_indicator_button.clicked.connect(self._handle_add_indicator_request)
        print("Signal connections established.")

    # --- Action Coordination Methods ---
    def _request_fetch_and_plot(self):
        """Fetches base stock data and triggers full recalculation and plotting."""
        ticker = self.ticker_input.text().strip().upper()
        if not ticker:
            QMessageBox.warning(self, "Missing Ticker", "Please enter a ticker symbol.")
            return

        print(f"Request received to fetch and plot data for: {ticker}")
        self.current_ticker = ticker

        try:
            # Fetch data using DataFetcher
            fetched_data = self.data_fetcher.fetch_stock_data(ticker) # Using default period/interval for now
            self.current_data = fetched_data

            if self.current_data.empty:
                 QMessageBox.warning(self, "No Data", f"No data found for '{ticker}'.")
                 # Clear everything if no base data
                 self.chart_manager.clear_chart()
                 self.indicators_config = [] # Clear indicators if base data fails
                 self.indicator_results = {}
                 return # Stop processing

            # Data fetched successfully, now recalculate and plot everything
            self._recalculate_and_plot_all()

        except ValueError as ve:
            error_message = f"Data Fetch Error for '{ticker}':\n{ve}"
            print(error_message)
            QMessageBox.critical(self, "Data Fetch Error", str(ve))
            self.current_data = None
            self.chart_manager.clear_chart() # Clear chart on fetch error
            self.indicators_config = []
            self.indicator_results = {}
        except Exception as e:
            error_message = f"Unexpected error processing '{ticker}':\n{e}"
            print(error_message)
            QMessageBox.critical(self, "Application Error", error_message)
            self.current_data = None
            self.chart_manager.clear_chart()
            self.indicators_config = []
            self.indicator_results = {}

    def _handle_add_indicator_request(self):
        """Handles the 'Add Indicator' button click."""
        if self.current_data is None or self.current_data.empty:
            QMessageBox.warning(self, "No Data", "Fetch stock data before adding indicators.")
            return

        indicator_type = self.indicator_combo.currentText()
        period = self.indicator_period_spinbox.value()
        indicator_id = f"{indicator_type.lower()}_{period}"

        # Prevent adding the exact same indicator multiple times
        if any(ind['id'] == indicator_id for ind in self.indicators_config):
            QMessageBox.information(self, "Duplicate Indicator", f"{indicator_type} ({period}) is already added.")
            return

        # Determine plot type (this could be stored elsewhere later)
        plot_type = 'overlay' # Default
        if indicator_type == 'RSI':
            plot_type = 'subplot'
        # Add more conditions for other subplot indicators (MACD, etc.)

        # Create config dictionary
        config = {
            'id': indicator_id,
            'type': indicator_type,
            'params': {'period': period},
            'plot_type': plot_type
        }

        print(f"Adding indicator request: {config}")
        self.indicators_config.append(config)

        # Trigger recalculation and plotting of everything
        self._recalculate_and_plot_all()


    def _recalculate_and_plot_all(self):
        """
        Core logic: Clears chart, plots base data, calculates all configured
        indicators, and plots them according to their type (overlay/subplot).
        """
        if self.current_data is None or self.current_data.empty:
            print("Cannot plot, no current stock data available.")
            return

        print("Recalculating all indicators and updating plot...")

        # 1. Clear the entire chart managed by ChartManager
        self.chart_manager.clear_chart()

        # 2. Plot the base stock data (Price Chart)
        self.chart_manager.plot_stock_data(self.current_data, self.current_ticker)

        # If base plotting failed (e.g., error in data), price_plot_item might be None
        if self.chart_manager.price_plot_item is None:
            print("Base data plotting failed, skipping indicators.")
            return

        # 3. Calculate and Plot Indicators
        self.indicator_results.clear() # Clear previous results
        next_subplot_row = 1 # Start subplots below the price chart (row 0)

        for config in self.indicators_config:
            indicator_id = config['id']
            indicator_type = config['type']
            params = config['params']
            plot_type = config['plot_type']
            calculated_data = None

            try:
                # Calculate using IndicatorCalculator
                if indicator_type == 'SMA':
                    calculated_data = self.indicator_calculator.calculate_sma(self.current_data, params['period'])
                elif indicator_type == 'RSI':
                    calculated_data = self.indicator_calculator.calculate_rsi(self.current_data, params['period'])
                # Add elif blocks for other indicators...

                if calculated_data is not None and not calculated_data.empty:
                    self.indicator_results[indicator_id] = calculated_data

                    # Plot using ChartManager
                    name = f"{indicator_type}({params['period']})" # Legend/Title Name
                    if plot_type == 'overlay':
                        # Define colors (could make this more dynamic)
                        color = 'r' if 'sma' in indicator_id else 'purple'
                        self.chart_manager.add_overlay_indicator(
                            indicator_id=indicator_id,
                            values=calculated_data,
                            name=name,
                            color=color
                        )
                    elif plot_type == 'subplot':
                        self.chart_manager.add_subplot_indicator(
                            indicator_id=indicator_id,
                            values=calculated_data,
                            name=name,
                            y_label=indicator_type, # Use type as Y-label for subplot
                            row_index=next_subplot_row,
                            color='g' # Example color for RSI
                        )
                        next_subplot_row += 1 # Increment row for the next subplot
                else:
                     print(f"Indicator {indicator_id} calculation returned no data.")

            except Exception as e:
                print(f"Error calculating or plotting indicator {indicator_id}: {e}")
                # Optionally show a warning to the user, but don't stop plotting others
                # QMessageBox.warning(self, "Indicator Error", f"Could not process indicator {indicator_id}:\n{e}")

        print("Recalculation and plotting complete.")


# ---- Application Execution ----
def main():
    print("Starting Ava's Awesome Finance App (Modular Indicator Framework)...")
    app = QApplication(sys.argv)
    window = FinanceApp()
    window.show()
    print("Entering the main event loop...")
    sys.exit(app.exec())

if __name__ == "__main__":
    print("-" * 60)
    print("Requires: PySide6, yfinance, pyqtgraph, pandas, numpy")
    print("Files: finance_app.py, data_fetcher.py, chart_manager.py, indicator_calculator.py")
    print("Ensure virtual environment is active and files are in the same directory.")
    print("-" * 60)
    main()