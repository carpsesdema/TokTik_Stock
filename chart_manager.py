# chart_manager.py

import pyqtgraph as pg
from pyqtgraph import DateAxisItem
import numpy as np
import pandas as pd

class ChartManager:
    """
    Manages plotting on a pyqtgraph GraphicsLayoutWidget, supporting
    a main price plot and multiple indicator subplots or overlays.
    """
    def __init__(self, graphics_widget: pg.GraphicsLayoutWidget):
        if not isinstance(graphics_widget, pg.GraphicsLayoutWidget):
            raise TypeError("graphics_widget must be an instance of pg.GraphicsLayoutWidget")

        self.graphics_widget = graphics_widget
        self.ticker_label = ""
        self.price_plot_item = None # Reference to the main price PlotItem
        self.indicator_plots = {} # Dict to store references to indicator PlotItems {indicator_id: plot_item}
        self.main_plot_dates = None # Store dates (timestamps) used for the main plot

        # Basic configuration
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        print("ChartManager initialized.")

    def clear_chart(self):
        """Clears all plots and resets internal references."""
        print("Clearing chart...")
        self.graphics_widget.clear()
        self.price_plot_item = None
        self.indicator_plots = {}
        self.ticker_label = ""
        self.main_plot_dates = None
        # Optionally add a default message
        # self.graphics_widget.addLabel("Chart cleared. Fetch data to plot.", row=0, col=0)

    def plot_stock_data(self, data: pd.DataFrame, ticker: str):
        """
        Plots the main stock closing price chart (OHLC could be added later).

        Args:
            data (pd.DataFrame): DataFrame with stock data (DatetimeIndex, 'Close').
            ticker (str): The stock ticker symbol.
        """
        # Don't clear here, clear_chart should be called explicitly before plotting everything
        # self.clear_chart() # Moved clearing logic outside

        if data is None or data.empty:
            print("No stock data provided to plot.")
            self.graphics_widget.addLabel(f"No data available for {ticker}", row=0, col=0)
            return

        print(f"Plotting main stock data for {ticker}...")
        self.ticker_label = ticker

        # --- Prepare data ---
        try:
            if not isinstance(data.index, pd.DatetimeIndex):
                 raise ValueError("Data index must be a DatetimeIndex.")
            if 'Close' not in data.columns:
                raise ValueError("Data must contain a 'Close' column.")

            self.main_plot_dates = data.index.astype(np.int64) // 10**9 # Store timestamps
            close_prices = data['Close'].values
        except Exception as e:
            print(f"Error preparing stock data for plotting: {e}")
            self.graphics_widget.addLabel(f"Error preparing data for {ticker}", row=0, col=0)
            return

        # --- Create Main Price Plot Item (at row 0) ---
        date_axis = DateAxisItem(orientation='bottom')
        self.price_plot_item = self.graphics_widget.addPlot(row=0, col=0, axisItems={'bottom': date_axis})

        # --- Plot Close Price Data ---
        # Give it a name for the legend
        price_curve = self.price_plot_item.plot(x=self.main_plot_dates, y=close_prices, pen=pg.mkPen('b', width=2), name="Close")

        # --- Customize Plot ---
        self.price_plot_item.setTitle(f"{ticker} - Price and Indicators")
        self.price_plot_item.setLabel('left', 'Price')
        # Bottom label is handled by DateAxisItem
        self.price_plot_item.showGrid(x=True, y=True, alpha=0.3)
        self.price_plot_item.setMouseEnabled(x=True, y=True) # Allow pan/zoom

        # --- Add Legend to Price Plot ---
        # A legend is useful even with only one item initially, prepares for overlays
        self.price_plot_item.addLegend(offset=(30, 30)) # Offset slightly from top-left corner

        print("Main stock data plotted successfully.")

    def add_overlay_indicator(self, indicator_id: str, values: pd.Series, name: str, color='r', width=1):
        """
        Adds an indicator plot onto the main price chart.

        Args:
            indicator_id (str): Unique ID for this indicator plot.
            values (pd.Series): Indicator data (must have same index as price data).
            name (str): Name for the legend.
            color (str): Plot line color.
            width (int): Plot line width.
        """
        if self.price_plot_item is None:
            print("Warning: Cannot add overlay. Main price plot does not exist.")
            return
        if self.main_plot_dates is None or len(self.main_plot_dates) != len(values):
             print(f"Warning (Overlay {name}): Mismatched data lengths or missing dates.")
             return
        if values.isnull().all():
            print(f"Warning (Overlay {name}): All indicator values are NaN, skipping plot.")
            return

        print(f"Adding overlay indicator: {name}")
        valid_indices = ~values.isnull() # Plot only non-NaN values
        dates = self.main_plot_dates[valid_indices]
        vals = values.dropna().values

        if len(dates) == 0:
             print(f"Warning (Overlay {name}): No valid data points after dropping NaN.")
             return

        # Plot on the existing price_plot_item
        indicator_curve = self.price_plot_item.plot(x=dates, y=vals, pen=pg.mkPen(color, width=width), name=name)
        self.indicator_plots[indicator_id] = indicator_curve # Store reference if needed

    def add_subplot_indicator(self, indicator_id: str, values: pd.Series, name: str, y_label: str, row_index: int, color='g', width=1):
        """
        Adds an indicator plot in its own subplot below the main chart.

        Args:
            indicator_id (str): Unique ID for this indicator plot.
            values (pd.Series): Indicator data.
            name (str): Title/name for the subplot.
            y_label (str): Label for the Y-axis of the subplot.
            row_index (int): The row in the GraphicsLayoutWidget for this subplot (>= 1).
            color (str): Plot line color.
            width (int): Plot line width.
        """
        if self.main_plot_dates is None or len(self.main_plot_dates) != len(values):
             print(f"Warning (Subplot {name}): Mismatched data lengths or missing dates.")
             return
        if values.isnull().all():
            print(f"Warning (Subplot {name}): All indicator values are NaN, skipping plot.")
            return

        print(f"Adding subplot indicator: {name} at row {row_index}")
        valid_indices = ~values.isnull() # Plot only non-NaN values
        dates = self.main_plot_dates[valid_indices]
        vals = values.dropna().values

        if len(dates) == 0:
             print(f"Warning (Subplot {name}): No valid data points after dropping NaN.")
             return

        # --- Create Subplot Plot Item ---
        date_axis = DateAxisItem(orientation='bottom')
        indicator_plot_item = self.graphics_widget.addPlot(row=row_index, col=0, axisItems={'bottom': date_axis})

        # --- Plot Indicator Data ---
        indicator_curve = indicator_plot_item.plot(x=dates, y=vals, pen=pg.mkPen(color, width=width), name=name)

        # --- Customize Subplot ---
        indicator_plot_item.setLabel('left', y_label)
        indicator_plot_item.showGrid(x=True, y=True, alpha=0.3)
        indicator_plot_item.setMaximumHeight(150) # Limit height of subplots

        # --- *** Link X Axis to Main Plot *** ---
        if self.price_plot_item:
            indicator_plot_item.setXLink(self.price_plot_item) # Link panning/zooming!
        else:
            print("Warning: Could not link X-axis, main plot item not found.")

        self.indicator_plots[indicator_id] = indicator_plot_item # Store reference