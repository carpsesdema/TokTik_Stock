# chart_manager.py

"""
Manages plotting financial data onto a pyqtgraph GraphicsLayoutWidget.

This module includes:
- ChartManager: Class orchestrating the creation and updating of price plots (candlestick),
  volume plots, and indicator overlays/subplots.
- CandlestickItem: A custom pyqtgraph GraphicsObject for efficiently drawing candlestick charts.
"""

import pyqtgraph as pg
from pyqtgraph import DateAxisItem, GraphicsObject, mkPen, mkBrush
import numpy as np
import pandas as pd
import pytz # Used by CandlestickItem for timestamp conversion if needed
from PySide6 import QtGui, QtCore
import logging # Optional

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# --- Custom Candlestick Item ---
class CandlestickItem(GraphicsObject):
    """
    Custom pyqtgraph GraphicsObject for displaying candlestick charts.

    Efficiently draws candlesticks using QPainter and QPicture caching.
    Supports hollow green candles for upward price movement and solid red
    for downward movement. Automatically calculates candle width based on
    the median time difference between data points.
    """
    def __init__(self, data: list):
        """
        Initializes the CandlestickItem.

        Args:
            data (list): A list of dictionaries, where each dictionary represents one candle
                         and must contain keys: 't' (Unix timestamp), 'o' (open), 'h' (high),
                         'l' (low), 'c' (close).
        """
        GraphicsObject.__init__(self)
        self.data = data  # Store the data for drawing and bounding box calculation
        self.picture = None # QPicture cache for efficient drawing
        self.generatePicture() # Initial drawing pass

    def generatePicture(self):
        """
        Generates the QPicture used for painting the candlesticks.

        This method pre-renders the candlestick shapes based on the current data.
        It calculates widths and sets appropriate pens/brushes for up/down candles.
        """
        self.picture = QtGui.QPicture()
        if not self.data:
            # Need to create and end painter even if there's no data for QPicture
            p = QtGui.QPainter(self.picture)
            p.end()
            return

        p = QtGui.QPainter(self.picture)

        # --- Calculate Candle Width ---
        # Use ~70% of the median time difference between points for width
        width_factor = 0.7 # Percentage of time diff for width
        w = 0 # Calculated width in seconds
        if len(self.data) > 1:
            # Extract timestamps, calculate differences, find median of positive diffs
            time_stamps = np.array([d['t'] for d in self.data])
            time_diffs = np.diff(time_stamps)
            valid_diffs = time_diffs[time_diffs > 0]
            if len(valid_diffs) > 0:
                median_diff = np.median(valid_diffs)
                w = median_diff * width_factor
                # Add a cap to prevent excessively wide candles for large gaps (e.g., weekly)
                w = min(w, 86400 * 5 * width_factor) # Example: max width = 70% of 5 days
            else: # Only one diff, or all diffs zero/negative? Use default.
                 w = 86400 * width_factor # Default to daily-like width if median fails
        elif len(self.data) == 1:
            # Only one data point, estimate width (e.g., assume daily)
            w = 86400 * width_factor
        else: # No data
             w = 0

        # --- Define Pens and Brushes (optimized) ---
        # Colors defined using RGB tuples (more explicit than letters)
        color_up = (0, 180, 0)       # Green
        color_down = (200, 60, 60)   # Red
        pen_wick_up = mkPen(color=color_up, width=1)
        pen_wick_down = mkPen(color=color_down, width=1)
        pen_body_up = mkPen(color=color_up, width=1) # Outline for hollow candle
        brush_body_down = mkBrush(color_down)        # Solid fill for down candle
        brush_hollow = mkBrush(None)                 # No fill for up candle
        pen_solid_body_down = mkPen(None)            # No outline for filled candle

        # --- Draw Each Candle ---
        for d in self.data:
            # Extract OHLC and timestamp for the current candle
            t, o, h, l, c = d['t'], d['o'], d['h'], d['l'], d['c']

            # Determine candle type (up, down, or flat)
            is_up = c > o
            is_flat = c == o

            # --- Draw Wicks (vertical lines) ---
            wick_pen = pen_wick_up if (is_up or is_flat) else pen_wick_down
            p.setPen(wick_pen)
            body_top = max(o, c)    # Top edge of the candle body
            body_bottom = min(o, c) # Bottom edge of the candle body
            # Draw upper wick: from high to top of body
            p.drawLine(QtCore.QPointF(t, h), QtCore.QPointF(t, body_top))
            # Draw lower wick: from low to bottom of body
            p.drawLine(QtCore.QPointF(t, l), QtCore.QPointF(t, body_bottom))

            # --- Draw Body (rectangle) ---
            rect_left = t - w / 2
            rect_top = o # QRectF draws from top-left; 'o' is the top if c > o
            rect_width = w
            rect_height = c - o # Height = close - open (can be negative)

            if is_up: # Hollow green body
                p.setPen(pen_body_up)
                p.setBrush(brush_hollow)
                p.drawRect(QtCore.QRectF(rect_left, rect_top, rect_width, rect_height))
            elif is_flat: # Draw a horizontal line for flat candles
                 p.setPen(pen_wick_down) # Use a neutral or down color?
                 p.drawLine(QtCore.QPointF(rect_left, o), QtCore.QPointF(rect_left + rect_width, o))
            else: # Solid red body (down candle)
                p.setPen(pen_solid_body_down)
                p.setBrush(brush_body_down)
                # QRectF handles negative height correctly by drawing from 'o' downwards to 'c'
                p.drawRect(QtCore.QRectF(rect_left, rect_top, rect_width, rect_height))

        p.end() # Finish painting the QPicture

    def paint(self, p: QtGui.QPainter, *args):
        """
        Called by pyqtgraph/Qt framework to draw the item.

        Args:
            p (QtGui.QPainter): The painter object provided by the framework.
            *args: Additional arguments from the framework.
        """
        # Check if picture cache is valid, generate if needed (shouldn't normally happen here)
        if self.picture is None:
             self.generatePicture()

        # Draw the pre-rendered QPicture at the item's local origin (0,0)
        # The picture itself contains coordinates relative to the data values.
        if self.picture and not self.picture.isNull():
            p.drawPicture(0, 0, self.picture)


    def boundingRect(self) -> QtCore.QRectF:
        """
        Returns the bounding rectangle of the item in its local coordinate system.

        This is essential for pyqtgraph to determine the item's extent for scaling,
        mouse interactions, and view clipping. It should encompass all parts of the
        drawn candlesticks (highs, lows, and widths).

        Returns:
            QtCore.QRectF: The calculated bounding rectangle. Returns an empty rect if no data.
        """
        if not self.data:
            return QtCore.QRectF() # Empty rectangle if no data

        try:
            # Find overall min/max timestamps, highs, and lows
            all_t = [d['t'] for d in self.data]
            all_h = [d['h'] for d in self.data]
            all_l = [d['l'] for d in self.data]
            min_t, max_t = min(all_t), max(all_t)
            min_l, max_h = min(all_l), max(all_h)

            # Calculate width factor for bounding box adjustment (similar to generatePicture)
            width_factor = 0.7
            if len(self.data) > 1:
                time_diffs = np.diff(np.array(all_t))
                valid_diffs = time_diffs[time_diffs > 0]
                if len(valid_diffs) > 0:
                    median_diff = np.median(valid_diffs)
                    w_factor = median_diff * width_factor
                    w_factor = min(w_factor, 86400 * 5 * width_factor)
            elif len(self.data) == 1:
                 w_factor = 86400 * width_factor # Estimate for single point
            else:
                 w_factor = 0

            # Calculate bounding box coordinates, including half candle width padding
            bounding_min_t = min_t - w_factor / 2
            bounding_max_t = max_t + w_factor / 2
            width = bounding_max_t - bounding_min_t
            height = max_h - min_l

            # Ensure height is non-zero if min_l == max_h
            if height < 1e-9: height = 1.0 # Avoid zero-height bounding box

            return QtCore.QRectF(bounding_min_t, min_l, width, height)
        except Exception as e:
             print(f"Error calculating bounding rect for CandlestickItem: {e}")
             # logging.error("Error calculating candlestick bounding rect", exc_info=True)
             return QtCore.QRectF() # Return empty on error

    def setData(self, data: list):
        """
        Updates the data used by the CandlestickItem and triggers a redraw.

        Args:
            data (list): The new list of candle dictionaries.
        """
        self.data = data
        self.generatePicture() # Regenerate the QPicture cache
        self.prepareGeometryChange() # Inform pyqtgraph the bounds might change
        self.update() # Request a repaint


# --- Chart Manager ---
class ChartManager:
    """
    Manages plotting within a pyqtgraph GraphicsLayoutWidget.

    Handles the creation, clearing, and updating of:
    - A primary price chart (using CandlestickItem).
    - A volume chart (using BarGraphItem).
    - Indicator overlays on the price chart.
    - Indicator subplots below the volume chart.

    Ensures that the X-axes of all plots are linked for synchronized panning/zooming.
    """
    def __init__(self, graphics_widget: pg.GraphicsLayoutWidget):
        """
        Initializes the ChartManager.

        Args:
            graphics_widget (pg.GraphicsLayoutWidget): The pyqtgraph widget that
                                                       this manager will control.
        """
        if not isinstance(graphics_widget, pg.GraphicsLayoutWidget):
            raise TypeError("graphics_widget must be an instance of pg.GraphicsLayoutWidget")

        self.graphics_widget = graphics_widget
        self.ticker_label = ""          # Store the current ticker symbol
        self.price_plot = None          # PlotItem for price chart (row 0)
        self.volume_plot = None         # PlotItem for volume chart (row 1)
        self.indicator_plots = {}       # {indicator_id: PlotItem/PlotDataItem} for subplots/overlays
        self.candlestick_item = None    # The CandlestickItem instance
        self.volume_item = None         # The BarGraphItem instance for volume
        self.main_plot_dates = None     # numpy array of Unix timestamps for the main data

        # Basic pyqtgraph configuration (can be overridden by themes)
        pg.setConfigOption('background', 'w') # Default white background
        pg.setConfigOption('foreground', 'k') # Default black foreground
        pg.setConfigOption('antialias', True) # Enable antialiasing for smoother lines
        print("ChartManager initialized.")
        # logging.info("ChartManager initialized.")

    def clear_chart(self):
        """
        Clears all plots, items, and internal references from the graphics layout.
        Resets the manager to a clean state.
        """
        print("Clearing chart...")
        # logging.info("Clearing chart")
        self.graphics_widget.clear() # This removes all PlotItems and Labels

        # Reset internal references
        self.price_plot = None
        self.volume_plot = None
        self.indicator_plots = {}
        self.candlestick_item = None
        self.volume_item = None
        self.ticker_label = ""
        self.main_plot_dates = None
        # Optionally add a default message back
        # self.graphics_widget.addLabel("Chart cleared.", row=0, col=0)

    def plot_stock_data(self, data: pd.DataFrame, ticker: str):
        """
        Plots the primary stock data: Candlesticks in the top plot (row 0)
        and Volume bars in the plot below (row 1).

        This method creates the necessary PlotItems, prepares the data,
        instantiates CandlestickItem and BarGraphItem, adds them to the plots,
        links the X-axes, and sets basic plot appearance.

        Args:
            data (pd.DataFrame): DataFrame containing stock data. Must have a
                                 DatetimeIndex and columns: 'Open', 'High',
                                 'Low', 'Close', 'Volume'.
            ticker (str): The stock ticker symbol for labeling.
        """
        # --- Pre-checks ---
        # Caller should ensure chart is cleared if necessary before calling this.
        if data is None or data.empty:
            print("ChartManager: No stock data provided to plot.")
            # logging.warning("plot_stock_data skipped: Data is None or empty.")
            self.graphics_widget.addLabel(f"No data available for {ticker}", row=0, col=0)
            return

        print(f"Plotting main stock data for {ticker}...")
        # logging.info(f"Plotting stock data for {ticker}")
        self.ticker_label = ticker

        # --- Data Preparation ---
        required_cols = ["Open", "High", "Low", "Close", "Volume"]
        try:
            # Validate index type
            if not isinstance(data.index, pd.DatetimeIndex):
                 raise ValueError("Data index must be a DatetimeIndex.")
            # Validate required columns
            if not all(col in data.columns for col in required_cols):
                missing = [c for c in required_cols if c not in data.columns]
                raise ValueError(f"Data is missing required columns: {missing}")

            # Convert index to UTC timestamps (seconds since epoch) - consistent internal representation
            if hasattr(data.index, 'tz') and data.index.tz is not None:
                 # If index is timezone-aware, convert to UTC
                 self.main_plot_dates = data.index.tz_convert('UTC').astype(np.int64) // 10**9
            else:
                 # If index is naive, assume UTC (or localize if needed, but UTC is safer)
                 self.main_plot_dates = data.index.tz_localize('UTC').astype(np.int64) // 10**9

            # Prepare data list for CandlestickItem
            candlestick_data = [
                {'t': self.main_plot_dates[i], 'o': data['Open'].iloc[i], 'h': data['High'].iloc[i], 'l': data['Low'].iloc[i], 'c': data['Close'].iloc[i]}
                for i in range(len(data))
            ]
            # Prepare volume data array
            volume_values = data['Volume'].values

        except Exception as e:
            print(f"Error preparing stock data for plotting: {e}")
            # logging.error(f"Error preparing plot data for {ticker}: {e}", exc_info=True)
            # Display error on chart area
            self.graphics_widget.addLabel(f"Error preparing data for {ticker}", row=0, col=0)
            return

        # --- Create Plot Areas (PlotItems) ---
        # Price Plot (Row 0)
        self.price_plot = self.graphics_widget.addPlot(row=0, col=0)
        self.price_plot.setLabel('left', 'Price')
        self.price_plot.showGrid(x=False, y=True, alpha=0.2) # Y grid only for price
        self.price_plot.hideAxis('bottom') # Volume plot will show the shared bottom axis

        # Volume Plot (Row 1)
        date_axis = DateAxisItem(orientation='bottom') # Use DateAxisItem for nice date formatting
        self.volume_plot = self.graphics_widget.addPlot(row=1, col=0, axisItems={'bottom': date_axis})
        self.volume_plot.setLabel('left', 'Volume')
        self.volume_plot.showGrid(x=True, y=True, alpha=0.2) # Show full grid for volume
        self.volume_plot.setMaximumHeight(150) # Limit vertical space for volume

        # --- Link X Axes ---
        # This is crucial for synchronized panning and zooming!
        self.volume_plot.setXLink(self.price_plot)

        # --- Add Candlestick Item ---
        self.candlestick_item = CandlestickItem(candlestick_data)
        self.price_plot.addItem(self.candlestick_item)

        # --- Add Volume Bar Item ---
        # Calculate volume bar width (similar to candlestick width)
        width_factor = 0.7
        bar_width = 0
        if len(self.main_plot_dates) > 1:
            time_diffs = np.diff(self.main_plot_dates)
            valid_diffs = time_diffs[time_diffs > 0]
            if len(valid_diffs) > 0:
                median_diff = np.median(valid_diffs)
                bar_width = median_diff * width_factor
                bar_width = min(bar_width, 86400 * 5 * width_factor)
        elif len(self.main_plot_dates) == 1:
            bar_width = 86400 * width_factor
        else: # No data
            bar_width = 0

        volume_brush = mkBrush(0, 100, 150, 180) # Define volume bar color
        volume_pen = mkPen(None) # No border on volume bars
        self.volume_item = pg.BarGraphItem(
            x=self.main_plot_dates, height=volume_values, width=bar_width,
            brush=volume_brush, pen=volume_pen
        )
        self.volume_plot.addItem(self.volume_item)

        # --- Final Plot Customization ---
        self.price_plot.setTitle(f"{ticker} - Price and Indicators")
        # Enable mouse interaction (zooming/panning)
        self.price_plot.setMouseEnabled(x=True, y=True)
        self.volume_plot.setMouseEnabled(x=True, y=True)

        # Add Legend to Price Plot (for indicator overlays)
        self.price_plot.addLegend(offset=(30, 30)) # Position legend slightly offset

        # --- Set Initial View Range ---
        # Set X range to show all data initially, with slight padding
        if self.main_plot_dates is not None and len(self.main_plot_dates) > 0:
            self.price_plot.setXRange(self.main_plot_dates[0], self.main_plot_dates[-1], padding=0.02)
            # Let pyqtgraph determine the initial Y range based on visible data
            self.price_plot.enableAutoRange(axis='y', enable=True)
            self.volume_plot.enableAutoRange(axis='y', enable=True)
        else:
             # Fallback if no dates available
             self.price_plot.autoRange()

        print("Main stock data plotted successfully (Candlestick & Volume).")
        # logging.info(f"Finished plotting stock data for {ticker}")

    def add_overlay_indicator(self, indicator_id: str, values: pd.Series, name: str, color='r', width=1):
        """
        Adds an indicator line plot as an overlay onto the main price chart (row 0).

        Args:
            indicator_id (str): A unique identifier for this indicator plot.
            values (pd.Series): The indicator data Series, indexed matching the main stock data.
            name (str): The name to display in the legend for this indicator.
            color (str or tuple): Color specification for the line (e.g., 'r', (255,0,0)).
            width (int): The width of the indicator line.
        """
        # --- Pre-checks ---
        if self.price_plot is None:
            print("Warning (Overlay): Cannot add overlay. Main price plot does not exist.")
            # logging.warning(f"Overlay plot skipped ({name}): Main price plot missing.")
            return
        if self.main_plot_dates is None or len(self.main_plot_dates) != len(values):
             # Check if lengths match - crucial for plotting against correct timestamps
             print(f"Warning (Overlay {name}): Mismatched data lengths or missing main plot dates.")
             # logging.warning(f"Overlay plot skipped ({name}): Data length mismatch.")
             return
        if values.isnull().all():
            # Don't plot if the indicator calculation resulted in all NaNs
            print(f"Warning (Overlay {name}): All indicator values are NaN, skipping plot.")
            # logging.warning(f"Overlay plot skipped ({name}): All values NaN.")
            return

        print(f"Adding overlay indicator: {name}")
        # logging.info(f"Adding overlay indicator: {name}")

        # --- Prepare Data for Plotting (handle NaNs) ---
        # Plot only where indicator values are not NaN
        valid_indices = ~values.isnull()
        dates_to_plot = self.main_plot_dates[valid_indices]
        values_to_plot = values.dropna().values # Get corresponding non-NaN values

        # Check if any valid data remains after dropping NaNs
        if len(dates_to_plot) == 0:
             print(f"Warning (Overlay {name}): No valid (non-NaN) data points to plot.")
             # logging.warning(f"Overlay plot skipped ({name}): No valid data points after NaN drop.")
             return

        # --- Add Plot Curve ---
        # Use plot() method of the existing price PlotItem
        indicator_curve = self.price_plot.plot(
            x=dates_to_plot, y=values_to_plot,
            pen=mkPen(color, width=width),
            name=name # Name for the legend item
        )
        # Store a reference to the plotted curve (PlotDataItem)
        self.indicator_plots[indicator_id] = indicator_curve

    def add_subplot_indicator(self, indicator_id: str, values: pd.Series, name: str, y_label: str, row_index: int, color='g', width=1):
        """
        Adds an indicator plot in its own subplot below the volume chart.

        Args:
            indicator_id (str): A unique identifier for this indicator plot.
            values (pd.Series): The indicator data Series, indexed matching the main stock data.
            name (str): The name/title for this indicator subplot.
            y_label (str): The label for the Y-axis of the subplot.
            row_index (int): The row index in the GraphicsLayoutWidget for this subplot.
                             Should start from 2 (row 0 = Price, row 1 = Volume).
            color (str or tuple): Color specification for the line.
            width (int): The width of the indicator line.
        """
         # --- Pre-checks ---
        if self.price_plot is None: # Need price plot to link X-axis
             print("Warning (Subplot): Cannot add subplot. Main price plot does not exist.")
             # logging.warning(f"Subplot skipped ({name}): Main price plot missing.")
             return
        if self.main_plot_dates is None or len(self.main_plot_dates) != len(values):
             print(f"Warning (Subplot {name}): Mismatched data lengths or missing main plot dates.")
             # logging.warning(f"Subplot skipped ({name}): Data length mismatch.")
             return
        if values.isnull().all():
            print(f"Warning (Subplot {name}): All indicator values are NaN, skipping plot.")
            # logging.warning(f"Subplot skipped ({name}): All values NaN.")
            return

        print(f"Adding subplot indicator: {name} at row {row_index}")
        # logging.info(f"Adding subplot indicator: {name} at row {row_index}")

        # --- Prepare Data for Plotting (handle NaNs) ---
        valid_indices = ~values.isnull()
        dates_to_plot = self.main_plot_dates[valid_indices]
        values_to_plot = values.dropna().values

        if len(dates_to_plot) == 0:
             print(f"Warning (Subplot {name}): No valid (non-NaN) data points to plot.")
             # logging.warning(f"Subplot skipped ({name}): No valid data points after NaN drop.")
             return

        # --- Create New PlotItem for the Subplot ---
        date_axis = DateAxisItem(orientation='bottom') # Separate date axis for each subplot
        indicator_plot_item = self.graphics_widget.addPlot(
            row=row_index, col=0,
            axisItems={'bottom': date_axis},
            title=name # Set subplot title directly
        )

        # --- Plot Indicator Data ---
        indicator_curve = indicator_plot_item.plot(
            x=dates_to_plot, y=values_to_plot,
            pen=mkPen(color, width=width)
            # No name needed here as title is set on PlotItem
        )

        # --- Customize Subplot ---
        indicator_plot_item.setLabel('left', y_label)
        indicator_plot_item.showGrid(x=True, y=True, alpha=0.2) # Grid lines
        indicator_plot_item.setMaximumHeight(100) # Constrain height of indicator subplots

        # --- Link X Axis to Main Plot ---
        indicator_plot_item.setXLink(self.price_plot) # Link panning/zooming

        # Store a reference to the created PlotItem
        self.indicator_plots[indicator_id] = indicator_plot_item


    def update_crosshair(self, timestamp: float, price: float):
         """
         (Placeholder) Updates the position of crosshair lines on the chart.

         This would typically involve having pg.InfiniteLine objects added to the
         plots and setting their positions here based on mouse coordinates.

         Args:
            timestamp (float): The X-coordinate (Unix timestamp) of the mouse.
            price (float): The Y-coordinate (price level) of the mouse on the price chart.
         """
         # Example (if self.v_line and self.h_line exist):
         # if self.v_line: self.v_line.setPos(timestamp)
         # if self.h_line: self.h_line.setPos(price)
         pass # Implementation deferred

    def set_view_range(self, start_ts: float, end_ts: float):
         """
         Sets the visible X-axis range for all linked plots.

         Also re-enables Y-axis autoranging for all plots to adjust their
         vertical view based on the data visible in the new X-range.

         Args:
            start_ts (float): The starting Unix timestamp for the view.
            end_ts (float): The ending Unix timestamp for the view.
         """
         if self.price_plot:
             print(f"Setting view range: {start_ts} to {end_ts}")
             # Set X range with a small padding
             self.price_plot.setXRange(start_ts, end_ts, padding=0.01)

             # Re-enable Y auto-ranging for all plots after changing X range
             # This allows the Y axis to adapt to the visible data
             self.price_plot.enableAutoRange(axis='y', enable=True)
             if self.volume_plot:
                 self.volume_plot.enableAutoRange(axis='y', enable=True)
             # Re-enable for all indicator subplots as well
             for plot_ref in self.indicator_plots.values():
                 if isinstance(plot_ref, pg.PlotItem): # Check if it's a subplot PlotItem
                     plot_ref.enableAutoRange(axis='y', enable=True)
                 # Note: Overlay curves (PlotDataItems) don't have their own Y range setting