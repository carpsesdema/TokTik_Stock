# Candle Analyze

A desktop application built with Python for fetching, visualizing, and analyzing historical stock market data using interactive charts and technical indicators.

## Features

* **Data Fetching:** Retrieves historical OHLCV data using `yfinance` based on user-specified ticker, period, and interval.
* **Interactive Charting:** Displays clear, interactive financial charts using `pyqtgraph`:
    * Custom-built CandlestickItem for efficient rendering.
    * Synchronized volume bar chart.
    * Ability to add technical indicator overlays (SMA) and subplots (RSI placeholder).
* **GUI:** Intuitive interface built with PySide6, featuring toolbar controls and an indicator management dock.
* **Modular Design:** Code is structured into logical modules for UI, data, charting, and calculations.

## Screenshots

Here are a few examples of the application interface:

*Screenshot 1:*
`![App Screenshot 1](assets/Screenshot 2025-05-03 214147.png)`

*Screenshot 2:*
`![App Screenshot 2](assets/Screenshot 2025-05-03 214541.png)`

*Screenshot 3:*
`![App Screenshot 3](assets/Screenshot 2025-05-03 214610.png)`

*(You can customize the Alt text like "App Screenshot 1" inside the square brackets `[]` if you like, e.g., `![Main Window]`)*

## Technology Stack

* **Language:** Python 3
* **GUI:** PySide6
* **Charting:** pyqtgraph
* **Data Handling:** pandas, NumPy
* **Data Source:** yfinance
* **Other libraries:** pytz

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone [YOUR_REPOSITORY_URL]
    cd [repository-folder-name]
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Ensure your `requirements.txt` file is up-to-date and included in your repo)*

## Usage

Run the main application file from the project's root directory:

```bash
python finance_app.py