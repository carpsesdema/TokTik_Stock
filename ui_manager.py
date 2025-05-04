# ui_manager.py

"""
Manages the User Interface creation and styling for the Finance App.

Contains the AppUI class responsible for building widgets and layouts,
and the apply_dark_theme function for styling the application.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QSpinBox, QGroupBox,
    QToolBar, QDockWidget,
    QSizePolicy # <<< Added import here
)
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt, QSize
import pyqtgraph as pg

# --- UI Related Constants ---
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
    """Applies a dark color theme and stylesheet to the QApplication."""
    # (Styling code remains the same)
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
        QStatusBar { color: lightgray; padding: 3px; }
        QStatusBar QLabel { color: lightgray; }
        QGroupBox {
            border: 1px solid gray; border-radius: 5px; margin-top: 0.5em;
            font-weight: bold; color: #cccccc; padding: 5px;
        }
        QGroupBox::title {
            subcontrol-origin: margin; subcontrol-position: top center;
            padding: 0 5px; background-color: #404040; border-radius: 3px;
        }
        QDockWidget { titlebar-close-icon: url(none); titlebar-normal-icon: url(none); }
        QDockWidget::title {
            text-align: center; background: #404040; padding: 4px;
            border-radius: 3px; color: #cccccc; font-weight: bold;
        }
        QToolBar { background-color: #353535; border: none; padding: 2px; spacing: 5px; }
        QToolBar QLabel { color: #cccccc; padding: 2px 5px; }
        QToolBar QLineEdit, QToolBar QComboBox {
             padding: 3px; border: 1px solid #505050; border-radius: 3px;
             background-color: #3c3c3c; color: white; min-height: 20px;
             min-width: 80px;
        }
        QToolBar QLineEdit { min-width: 100px; }
        QToolBar QPushButton {
            padding: 4px 10px; border: 1px solid #555; border-radius: 4px;
            background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #606060, stop: 1 #454545);
            color: white; min-height: 20px;
        }
        QToolBar QPushButton:hover { background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #707070, stop:1 #555555); }
        QToolBar QPushButton:pressed { background-color: #353535; }
        QToolBar QPushButton:disabled { background-color: #404040; color: #808080; }
        QLabel { color: #cccccc; padding: 2px; }
        QLineEdit, QComboBox, QSpinBox {
            padding: 5px; border: 1px solid #505050; border-radius: 3px;
            background-color: #3c3c3c; color: white; min-height: 20px;
        }
        QComboBox::drop-down { border: none; }
        QComboBox QAbstractItemView { background-color: #3c3c3c; color: white; selection-background-color: #2a82da; }
        QPushButton {
            padding: 6px 15px; border: 1px solid #555; border-radius: 4px;
            background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #606060, stop: 1 #404040);
            color: white; min-height: 20px;
        }
        QPushButton:hover { background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #707070, stop:1 #505050); }
        QPushButton:pressed { background-color: #353535; }
        QPushButton:disabled { background-color: #404040; color: #808080; }
        QToolTip { color: black; background-color: lightyellow; border: 1px solid black; }
    """
    app.setStyleSheet(style_sheet)

# ---- UI Builder Class ----
class AppUI:
    """Handles UI creation and provides access to key elements."""
    # (Docstring remains the same)
    def __init__(self, main_window: QMainWindow):
        """Initializes the UI builder."""
        self.main_window = main_window
        self.ticker_input: QLineEdit = None
        self.period_combo: QComboBox = None
        self.interval_combo: QComboBox = None
        self.fetch_button: QPushButton = None
        self.graphics_widget: pg.GraphicsLayoutWidget = None
        self.indicator_combo: QComboBox = None
        self.indicator_period_spinbox: QSpinBox = None
        self.add_indicator_button: QPushButton = None
        self.indicator_dock: QDockWidget = None

    def setup_ui(self):
        """Creates the main UI structure."""
        print("Setting up professional UI from ui_manager...")
        self.graphics_widget = pg.GraphicsLayoutWidget(show=True)
        self.graphics_widget.setMinimumSize(600, 400)
        self.main_window.setCentralWidget(self.graphics_widget)
        self._create_main_toolbar()
        self._create_indicator_dock_widget()
        print("Professional UI setup complete.")

    def _create_main_toolbar(self):
        """Creates and populates the main application toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)

        toolbar.addWidget(QLabel("Ticker:"))
        self.ticker_input = QLineEdit()
        self.ticker_input.setPlaceholderText("e.g., AAPL")
        self.ticker_input.setMinimumWidth(120)
        toolbar.addWidget(self.ticker_input)

        toolbar.addWidget(QLabel("Period:"))
        self.period_combo = QComboBox()
        self.period_combo.addItems(FETCH_PERIODS)
        self.period_combo.setCurrentText(DEFAULT_PERIOD)
        toolbar.addWidget(self.period_combo)

        toolbar.addWidget(QLabel("Interval:"))
        self.interval_combo = QComboBox()
        toolbar.addWidget(self.interval_combo)

        self.fetch_button = QPushButton("Fetch")
        self.fetch_button.setToolTip("Fetch data for the selected ticker, period, and interval")
        toolbar.addWidget(self.fetch_button)

        spacer = QWidget()
        # --- FIX HERE ---
        # Access SizePolicy directly after importing it
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        # --- END FIX ---
        toolbar.addWidget(spacer)

        self.main_window.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

    def _create_indicator_dock_widget(self):
        """Creates the dock widget for adding indicators."""
        # (This method remains the same as before)
        self.indicator_dock = QDockWidget("Indicator Controls", self.main_window)
        self.indicator_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.indicator_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable)

        dock_content_widget = QWidget()
        dock_layout = QVBoxLayout(dock_content_widget)
        dock_layout.setContentsMargins(10, 10, 10, 10)
        dock_layout.setSpacing(10)

        indicator_select_layout = QHBoxLayout()
        indicator_select_layout.addWidget(QLabel("Indicator:"))
        self.indicator_combo = QComboBox()
        self.indicator_combo.addItems(["SMA", "RSI"])
        indicator_select_layout.addWidget(self.indicator_combo)
        dock_layout.addLayout(indicator_select_layout)

        period_select_layout = QHBoxLayout()
        period_select_layout.addWidget(QLabel("Period:"))
        self.indicator_period_spinbox = QSpinBox()
        self.indicator_period_spinbox.setRange(1, 500)
        self.indicator_period_spinbox.setValue(14)
        self.indicator_period_spinbox.setToolTip("Lookback period for the indicator")
        period_select_layout.addWidget(self.indicator_period_spinbox)
        dock_layout.addLayout(period_select_layout)

        self.add_indicator_button = QPushButton("Add Indicator")
        self.add_indicator_button.setToolTip("Add the selected indicator to the chart")
        dock_layout.addWidget(self.add_indicator_button)

        dock_layout.addStretch(1)
        self.indicator_dock.setWidget(dock_content_widget)
        self.main_window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.indicator_dock)

    # --- Helper methods to access constants ---
    # (These remain the same)
    def get_interval_map(self):
        return INTERVALS_FOR_PERIOD
    def get_valid_intervals(self):
        return VALID_INTERVALS
    def get_default_interval(self):
        return DEFAULT_INTERVAL