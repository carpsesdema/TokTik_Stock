# finance_app.py

import sys
import pandas as pd
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox,
    QComboBox, QSpinBox, QGroupBox,
    QStatusBar
)
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
import pyqtgraph as pg

# Import our modular components
from data_fetcher import DataFetcher
from chart_manager import ChartManager
from indicator_calculator import IndicatorCalculator

# --- Constants ---
FETCH_PERIODS = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
DEFAULT_PERIOD = "1y"
VALID_INTERVALS = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
DEFAULT_INTERVAL = "1d"
INTERVALS_FOR_PERIOD = {
    "intraday_short": ["1m", "2m", "5m", "15m", "30m"],
    "intraday_medium": ["60m", "90m", "1h"],
    "daily_weekly": ["1d", "5d", "1wk"],
    "monthly": ["1mo", "3mo"]
}

# --- Styling Function ---
def apply_dark_theme(app):
    """Applies a dark theme to the Qt application."""
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
    dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.black)
    dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, QColor(40, 40, 40))
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(127, 127, 127))
    app.setPalette(dark_palette)
    style_sheet = """
        QMainWindow { background-color: #2d2d2d; }
        QStatusBar { color: lightgray; }
        QStatusBar QLabel { color: lightgray; }
        QGroupBox { border: 1px solid gray; border-radius: 5px; margin-top: 0.5em; font-weight: bold; color: #cccccc; }
        QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 3px; background-color: #404040; border-radius: 3px; }
        QLabel { color: #cccccc; padding: 2px; }
        QLineEdit, QComboBox, QSpinBox { padding: 5px; border: 1px solid #505050; border-radius: 3px; background-color: #3c3c3c; color: white; min-height: 20px; }
        QComboBox::drop-down { border: none; }
        QComboBox QAbstractItemView { background-color: #3c3c3c; color: white; selection-background-color: #2a82da; }
        QPushButton { padding: 6px 15px; border: 1px solid #555; border-radius: 4px; background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #606060, stop: 1 #404040); color: white; min-height: 20px; }
        QPushButton:hover { background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #707070, stop: 1 #505050); border: 1px solid #666; }
        QPushButton:pressed { background-color: #353535; border: 1px solid #444; }
        QPushButton:disabled { background-color: #404040; border: 1px solid #444; color: #808080; }
        QToolTip { color: black; background-color: lightyellow; border: 1px solid black; }
    """
    app.setStyleSheet(style_sheet)

# ---- UI Builder Class ----
class AppUI:
    """Handles the creation and layout of UI widgets."""
    def __init__(self, main_window):
        self.main_window = main_window # Reference to the QMainWindow

    def setup_ui(self):
        """Creates and arranges UI widgets."""
        print("Setting up UI elements...")

        # Create central widget and main layout
        self.main_window.central_widget = QWidget()
        self.main_window.main_layout = QVBoxLayout(self.main_window.central_widget)
        self.main_window.setCentralWidget(self.main_window.central_widget)

        # --- Top Controls Layout ---
        top_controls_layout = QHBoxLayout()

        # --- Data Selection Group ---
        data_group = QGroupBox("Data Selection")
        data_layout = QHBoxLayout(data_group)

        data_layout.addWidget(QLabel("Ticker:"))
        self.ticker_input = QLineEdit()
        self.ticker_input.setPlaceholderText("e.g., AAPL")
        data_layout.addWidget(self.ticker_input, stretch=2)

        data_layout.addWidget(QLabel("Period:"))
        self.period_combo = QComboBox()
        self.period_combo.addItems(FETCH_PERIODS)
        self.period_combo.setCurrentText(DEFAULT_PERIOD)
        data_layout.addWidget(self.period_combo, stretch=1)

        data_layout.addWidget(QLabel("Interval:"))
        self.interval_combo = QComboBox()
        data_layout.addWidget(self.interval_combo, stretch=1)

        self.fetch_button = QPushButton("Fetch & Plot")
        data_layout.addWidget(self.fetch_button)

        top_controls_layout.addWidget(data_group)

        # --- Chart Area ---
        self.graphics_widget = pg.GraphicsLayoutWidget(show=True)
        self.graphics_widget.setMinimumHeight(500)

        # --- Indicator Control Group ---
        indicator_group = QGroupBox("Add Indicator")
        indicator_layout = QHBoxLayout(indicator_group)

        indicator_layout.addWidget(QLabel("Indicator:"))
        self.indicator_combo = QComboBox()
        self.indicator_combo.addItems(["SMA", "RSI"])
        indicator_layout.addWidget(self.indicator_combo, stretch=1)

        indicator_layout.addWidget(QLabel("Period:"))
        self.indicator_period_spinbox = QSpinBox()
        self.indicator_period_spinbox.setRange(1, 500)
        self.indicator_period_spinbox.setValue(14)
        indicator_layout.addWidget(self.indicator_period_spinbox, stretch=1)

        self.add_indicator_button = QPushButton("Add")
        indicator_layout.addWidget(self.add_indicator_button)

        # --- Assemble Main Layout ---
        self.main_window.main_layout.addLayout(top_controls_layout)
        self.main_window.main_layout.addWidget(self.graphics_widget, stretch=1)
        self.main_window.main_layout.addWidget(indicator_group)

        print("UI setup complete.")


# ---- Main Application Window (Controller) ----
class FinanceApp(QMainWindow):
    """
    Main application class. Handles logic, state, and coordination.
    Uses AppUI for UI construction and ChartManager for plotting.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ava's Awesome Finance App - Refactored UI")
        self.resize(1100, 900)

        # Instantiate core components (Data & Calculation)
        self.data_fetcher = DataFetcher()
        self.indicator_calculator = IndicatorCalculator()
        # ChartManager needs the graphics widget from the UI, initialized later

        # Application state
        self.current_data = None
        self.current_ticker = ""
        self.indicators_config = []
        self.indicator_results = {}

        # --- Setup UI ---
        # Create the UI instance (which sets central widget and layout)
        self.ui = AppUI(self)
        self.ui.setup_ui() # Build the widgets and layouts

        # --- Setup Chart Manager ---
        # Now that the UI (and graphics_widget) exists, create ChartManager
        self.chart_manager = ChartManager(self.ui.graphics_widget)

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready.")

        # Connect signals after UI and managers are set up
        self._connect_signals()
        self._update_interval_options() # Set initial interval options

        print("FinanceApp initialized successfully!")

    def _connect_signals(self):
        """Connects UI signals to application slots."""
        # Access UI elements via self.ui
        self.ui.fetch_button.clicked.connect(self._request_fetch_and_plot)
        self.ui.ticker_input.returnPressed.connect(self._request_fetch_and_plot)
        self.ui.add_indicator_button.clicked.connect(self._handle_add_indicator_request)
        self.ui.period_combo.currentTextChanged.connect(self._update_interval_options)
        print("Signal connections established.")

    def _update_interval_options(self):
        """Updates the available intervals based on the selected period."""
        # Access UI elements via self.ui
        selected_period = self.ui.period_combo.currentText()
        current_interval = self.ui.interval_combo.currentText()
        self.ui.interval_combo.clear()

        allowed_intervals = []
        if selected_period in ["1y", "2y", "5y", "10y", "max"]:
            allowed_intervals.extend(INTERVALS_FOR_PERIOD["daily_weekly"])
            allowed_intervals.extend(INTERVALS_FOR_PERIOD["monthly"])
        elif selected_period in ["6mo", "ytd"]:
            allowed_intervals.extend(INTERVALS_FOR_PERIOD["intraday_medium"])
            allowed_intervals.extend(INTERVALS_FOR_PERIOD["daily_weekly"])
            allowed_intervals.extend(INTERVALS_FOR_PERIOD["monthly"])
        elif selected_period in ["1mo", "3mo"]:
            allowed_intervals.extend(INTERVALS_FOR_PERIOD["intraday_short"])
            allowed_intervals.extend(INTERVALS_FOR_PERIOD["intraday_medium"])
            allowed_intervals.extend(INTERVALS_FOR_PERIOD["daily_weekly"])
        else:
            allowed_intervals.extend(INTERVALS_FOR_PERIOD["intraday_short"])
            allowed_intervals.extend(INTERVALS_FOR_PERIOD["intraday_medium"])

        unique_intervals = sorted(list(set(allowed_intervals)), key=lambda x: (x.rstrip('mhdwkmo'), int(x[:-1]) if x[:-1].isdigit() else 0))
        self.ui.interval_combo.addItems(unique_intervals)

        if current_interval in unique_intervals:
            self.ui.interval_combo.setCurrentText(current_interval)
        elif DEFAULT_INTERVAL in unique_intervals:
             self.ui.interval_combo.setCurrentText(DEFAULT_INTERVAL)
        elif unique_intervals:
             self.ui.interval_combo.setCurrentIndex(0)

        print(f"Interval options updated for period '{selected_period}': {unique_intervals}")


    # --- Action Coordination Methods ---
    def _request_fetch_and_plot(self):
        """Fetches data based on UI selections and triggers plotting."""
        # Access UI elements via self.ui
        ticker = self.ui.ticker_input.text().strip().upper()
        period = self.ui.period_combo.currentText()
        interval = self.ui.interval_combo.currentText()

        if not ticker:
            QMessageBox.warning(self, "Missing Ticker", "Please enter a ticker symbol.")
            return
        if not interval:
            QMessageBox.warning(self, "Missing Interval", "Please select a valid interval.")
            return

        print(f"Request received: Ticker={ticker}, Period={period}, Interval={interval}")
        self.status_bar.showMessage(f"Fetching {ticker} ({period} / {interval})...")
        QApplication.processEvents()

        self.current_ticker = ticker
        self.indicators_config = []
        self.indicator_results = {}

        try:
            fetched_data = self.data_fetcher.fetch_stock_data(ticker, period=period, interval=interval)
            self.current_data = fetched_data

            if self.current_data.empty or not all(col in self.current_data.columns for col in ["Open", "High", "Low", "Close", "Volume"]):
                 warning_msg = f"No data or incomplete OHLCV data found for '{ticker}' ({period}/{interval})."
                 print(warning_msg)
                 self.status_bar.showMessage(warning_msg, 5000)
                 self.chart_manager.clear_chart()
                 self.current_data = None
                 return

            self.status_bar.showMessage(f"Plotting {ticker}...")
            QApplication.processEvents()
            self._recalculate_and_plot_all()
            self.status_bar.showMessage(f"{ticker} ({period}/{interval}) plotted successfully.", 5000)

        except ValueError as ve:
            error_message = f"Data Fetch Error ({ticker}): {ve}"
            print(error_message)
            self.status_bar.showMessage(error_message, 8000)
            QMessageBox.critical(self, "Data Fetch Error", str(ve))
            self.current_data = None
            self.chart_manager.clear_chart()
        except Exception as e:
            error_message = f"Unexpected error ({ticker}): {e}"
            print(error_message)
            self.status_bar.showMessage(error_message, 8000)
            QMessageBox.critical(self, "Application Error", error_message)
            self.current_data = None
            self.chart_manager.clear_chart()

    def _handle_add_indicator_request(self):
        """Handles the 'Add Indicator' button click."""
        if self.current_data is None or self.current_data.empty:
            self.status_bar.showMessage("Fetch stock data before adding indicators.", 3000)
            return

        # Access UI elements via self.ui
        indicator_type = self.ui.indicator_combo.currentText()
        period = self.ui.indicator_period_spinbox.value()
        indicator_id = f"{indicator_type.lower()}_{period}"

        if any(ind['id'] == indicator_id for ind in self.indicators_config):
            self.status_bar.showMessage(f"{indicator_type} ({period}) is already added.", 3000)
            return

        plot_type = 'overlay' if indicator_type == 'SMA' else 'subplot'
        config = {'id': indicator_id, 'type': indicator_type, 'params': {'period': period}, 'plot_type': plot_type}

        print(f"Adding indicator request: {config}")
        self.indicators_config.append(config)
        self.status_bar.showMessage(f"Added {indicator_type}({period}). Replotting...")
        QApplication.processEvents()

        self._recalculate_and_plot_all()
        self.status_bar.showMessage(f"Indicators updated.", 3000)


    def _recalculate_and_plot_all(self):
        """
        Clears chart, plots base data, calculates/plots indicators.
        (Logic remains largely the same, uses self.chart_manager and state)
        """
        if self.current_data is None or self.current_data.empty:
            print("Cannot plot, no current stock data available.")
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
                self.status_bar.showMessage(error_msg, 5000)

        print("Recalculation and plotting complete.")


# ---- Application Execution ----
def main():
    print("Starting Ava's Awesome Finance App (Refactored UI Edition)...")

    try:
        if hasattr(Qt, 'AA_EnableHighDpiScaling'): QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'): QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    except AttributeError: print("Note: High DPI attributes not available.")

    app = QApplication(sys.argv)
    apply_dark_theme(app)
    pg.setConfigOption('background', QColor(40, 40, 40))
    pg.setConfigOption('foreground', 'w')

    window = FinanceApp()
    window.show()
    print("Entering the main event loop...")
    sys.exit(app.exec())

if __name__ == "__main__":
    print("-" * 60)
    print("Requires: PySide6, yfinance, pyqtgraph, pandas, numpy, pytz")
    print("Files: finance_app.py, data_fetcher.py, chart_manager.py, indicator_calculator.py")
    print("Ensure virtual environment is active and files are in the same directory.")
    print("-" * 60)
    main()