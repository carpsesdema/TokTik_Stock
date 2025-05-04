# finance_app.py

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox # Added QMessageBox for later use
)
# We'll need QtCore and QtGui later, but let's keep imports minimal for now

# ---- Main Application Window ----
class FinanceApp(QMainWindow):
    """
    Main window class for the Finance Analysis Application.
    Handles UI setup, signal connections, and core logic orchestration.
    """
    def __init__(self):
        """
        Constructor for the FinanceApp window.
        Initializes the window, sets up the UI, and connects signals.
        """
        super().__init__()
        self.setWindowTitle("Ava's Awesome Finance App")
        self.resize(800, 600) # A decent starting size

        # Placeholder for storing fetched stock data (for Phase 2)
        self.current_data = None

        # --- Core UI Setup ---
        # Set up the central widget and main layout first
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget) # Main vertical layout
        self.setCentralWidget(self.central_widget)

        # Call dedicated methods to build the UI and connect signals
        self._setup_ui()
        self._connect_signals()

        print("FinanceApp initialized successfully!") # Let's add some feedback

    def _setup_ui(self):
        """
        Creates and arranges the widgets in the main window.
        Keeps the UI creation logic separate and organized.
        """
        print("Setting up UI elements...")

        # --- Input Area (Top Row using QHBoxLayout) ---
        self.input_layout = QHBoxLayout() # Horizontal layout for inputs

        self.ticker_label = QLabel("Ticker Symbol:")
        self.ticker_input = QLineEdit()
        self.ticker_input.setPlaceholderText("e.g., AAPL, MSFT, ^GSPC") # Add examples
        self.fetch_button = QPushButton("Fetch & Plot Data") # Slightly more descriptive

        # Add widgets to the input layout
        self.input_layout.addWidget(self.ticker_label)
        self.input_layout.addWidget(self.ticker_input) # Input field will stretch
        self.input_layout.addWidget(self.fetch_button)

        # --- Chart Area Placeholder ---
        # This QWidget will be replaced by a pyqtgraph widget in Phase 2
        self.chart_placeholder = QWidget()
        # Give it a distinct background and border to make it visible
        self.chart_placeholder.setStyleSheet("background-color: #E0E0E0; border: 1px solid #B0B0B0;")
        # Set a minimum height, but allow it to expand
        self.chart_placeholder.setMinimumHeight(400)

        # --- Add Layouts and Widgets to Main Layout ---
        self.main_layout.addLayout(self.input_layout) # Add the input row at the top
        self.main_layout.addWidget(self.chart_placeholder, stretch=1) # Add chart area, allowing it to stretch vertically

        print("UI setup complete.")

    def _connect_signals(self):
        """
        Connects widget signals (like button clicks) to their corresponding methods (slots).
        """
        # Connect the button's 'clicked' signal to our placeholder data fetching method
        self.fetch_button.clicked.connect(self._on_fetch_data_clicked)
        # Allow pressing Enter in the QLineEdit to trigger the fetch as well
        self.ticker_input.returnPressed.connect(self._on_fetch_data_clicked)
        print("Signal connections established.")

    # --- Action Methods (Slots) ---
    def _on_fetch_data_clicked(self):
        """
        Placeholder slot called when the 'Fetch Data' button is clicked
        or Enter is pressed in the ticker input field.
        """
        ticker = self.ticker_input.text().strip().upper() # Get, clean, and uppercase the ticker

        if not ticker:
            # Use QMessageBox for user feedback if the ticker is empty
            QMessageBox.warning(self, "Missing Ticker", "Oops! Please enter a ticker symbol before fetching data.")
            print("Fetch button clicked, but ticker input was empty.")
            return # Stop processing if no ticker is provided

        print(f"Action triggered: Fetch data requested for ticker: {ticker}")
        # --- TODO in Phase 2 ---
        # 1. Call the actual data fetching logic using yfinance
        # 2. Store the fetched data in self.current_data
        # 3. Call a method to update the chart (e.g., self._update_chart())
        # -------------------------
        # For now, just showing a simple message box as confirmation
        QMessageBox.information(self, "Action Triggered", f"Okay, ready to fetch data for {ticker}! (Implementation coming in Phase 2)")


# ---- Application Execution ----
def main():
    """
    Main function to initialize and run the QApplication.
    """
    print("Starting Ava's Awesome Finance App...")
    # Create the Qt Application instance
    # sys.argv allows passing command line arguments to Qt, if any
    app = QApplication(sys.argv)

    # Create and show the main window
    window = FinanceApp()
    window.show() # Make the window visible

    print("Entering the main event loop...")
    # Start the Qt event loop. The application will run until the window is closed.
    # sys.exit() ensures a clean exit code is returned.
    sys.exit(app.exec())

if __name__ == "__main__":
    # This block runs only when the script is executed directly
    print("------------------------------------------------------")
    print("Reminder: Ensure you have installed the required libraries:")
    print("pip install PySide6 yfinance pyqtgraph pandas numpy")
    print("Make sure your virtual environment is activated!")
    print("------------------------------------------------------")
    main() # Run the main function