import tkinter as tk
from tkinter import messagebox, filedialog
import requests
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta

# API key and URL for stock data
API_KEY = 'cr0v6shr01qo0i56faugcr0v6shr01qo0i56fav0'
BASE_URL = 'https://finnhub.io/api/v1'

# Define color scheme and fonts
COLOR_SCHEME = {
    'background': '#f4f4f9',
    'button': '#4caf50',
    'button_text': 'white',
    'button_remove': '#f44336',
    'button_update': '#ff9800',
    'button_export': '#673ab7',
    'button_import': '#009688',
    'button_trends': '#9c27b0',
    'button_statistics': '#3f51b5',
    'text': '#333333',
    'highlight_avg': 'blue',
    'highlight_high': 'green',
    'highlight_low': 'red',
}
FONT = ("Helvetica", 14)

class StockPortfolioTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Portfolio Tracker")
        self.root.geometry("1000x700")
        self.root.configure(bg=COLOR_SCHEME['background'])

        # Initialize stock portfolio
        self.portfolio = {}

        # Create UI elements
        self.create_widgets()

    def create_widgets(self):
        # Title label
        tk.Label(self.root, text="Stock Portfolio Tracker", font=("Helvetica", 20, 'bold'), bg=COLOR_SCHEME['background']).pack(pady=10)

        # Stock symbol entry
        tk.Label(self.root, text="Stock Symbol:", font=FONT, bg=COLOR_SCHEME['background']).pack(pady=5)
        self.symbol_entry = tk.Entry(self.root, font=FONT)
        self.symbol_entry.pack(pady=5)

        # Buttons
        self.create_button("Add Stock", self.add_stock, COLOR_SCHEME['button'])
        self.create_button("Remove Stock", self.remove_stock, COLOR_SCHEME['button_remove'])
        self.create_button("Show Portfolio", self.show_portfolio, COLOR_SCHEME['button'])
        self.create_button("Update Prices", self.update_prices, COLOR_SCHEME['button_update'])
        self.create_button("Export Portfolio", self.export_portfolio, COLOR_SCHEME['button_export'])
        self.create_button("Import Portfolio", self.import_portfolio, COLOR_SCHEME['button_import'])
        self.create_button("Show Trends", self.show_trends, COLOR_SCHEME['button_trends'])
        self.create_button("Show Statistics", self.show_statistics, COLOR_SCHEME['button_statistics'])

        # Portfolio list
        self.portfolio_list = tk.Listbox(self.root, font=FONT, width=70, height=15, bg=COLOR_SCHEME['background'])
        self.portfolio_list.pack(pady=10)

        # Status label
        self.status_label = tk.Label(self.root, text="", font=("Helvetica", 12), bg=COLOR_SCHEME['background'])
        self.status_label.pack(pady=5)

    def create_button(self, text, command, color):
        tk.Button(self.root, text=text, font=FONT, command=command, bg=color, fg=COLOR_SCHEME['button_text']).pack(pady=5)

    def add_stock(self):
        symbol = self.symbol_entry.get().upper()
        if not symbol:
            messagebox.showwarning("Input Error", "Please enter a stock symbol.")
            return

        if symbol in self.portfolio:
            messagebox.showinfo("Info", f"Stock '{symbol}' already in portfolio.")
            return

        # Fetch stock data
        stock_data = self.get_stock_data(symbol)
        if stock_data:
            self.portfolio[symbol] = stock_data
            self.symbol_entry.delete(0, tk.END)
            self.status_label.config(text=f"Stock '{symbol}' added to portfolio.")
            self.show_portfolio()
        else:
            messagebox.showerror("Error", f"Failed to fetch data for stock symbol '{symbol}'.")

    def remove_stock(self):
        symbol = self.symbol_entry.get().upper()
        if not symbol:
            messagebox.showwarning("Input Error", "Please enter a stock symbol.")
            return

        if symbol not in self.portfolio:
            messagebox.showinfo("Info", f"Stock '{symbol}' not found in portfolio.")
            return

        del self.portfolio[symbol]
        self.symbol_entry.delete(0, tk.END)
        self.status_label.config(text=f"Stock '{symbol}' removed from portfolio.")
        self.show_portfolio()

    def show_portfolio(self):
        self.portfolio_list.delete(0, tk.END)
        for symbol, data in self.portfolio.items():
            self.portfolio_list.insert(tk.END, f"{symbol}: ${data['price']} (Change: {data['change']}%)")

    def update_prices(self):
        for symbol in self.portfolio.keys():
            stock_data = self.get_stock_data(symbol)
            if stock_data:
                self.portfolio[symbol] = stock_data
        self.show_portfolio()
        self.status_label.config(text="Stock prices updated.")

    def get_stock_data(self, symbol):
        try:
            url = f"{BASE_URL}/quote?symbol={symbol}&token={API_KEY}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if 'c' in data:
                return {
                    'price': data['c'],
                    'change': ((data['c'] - data['pc']) / data['pc']) * 100 if 'pc' in data else 'N/A'
                }
            else:
                print("Unexpected data format:", data)
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request exception: {e}")
        except ValueError as e:
            print(f"JSON decode error: {e}")
        return None

    def get_historical_data(self, symbol):
        try:
            end_time = int(datetime.now().timestamp())
            start_time = int((datetime.now() - timedelta(days=30)).timestamp())
            url = f"{BASE_URL}/stock/candle?symbol={symbol}&resolution=D&from={start_time}&to={end_time}&token={API_KEY}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if 'c' in data:
                return {i: {'1. open': price} for i, price in enumerate(data['c'])}
            else:
                print(f"No 'c' in data: {data}")
                return {}
        except requests.exceptions.RequestException as e:
            print(f"Request exception: {e}")
        except ValueError as e:
            print(f"JSON decode error: {e}")
        return {}


    def show_trends(self):
        if not self.portfolio:
            messagebox.showwarning("No Stocks", "Your portfolio is empty.")
            return

        # Create a new window for the chart
        trends_window = tk.Toplevel(self.root)
        trends_window.title("Stock Price Trends")
        trends_window.geometry("800x600")

        # Create a figure for the chart
        fig, ax = plt.subplots(figsize=(8, 6))
        colors = ['blue', 'green', 'red', 'purple', 'orange', 'brown', 'pink', 'gray']

        for idx, symbol in enumerate(self.portfolio.keys()):
            stock_data = self.get_historical_data(symbol)
            if stock_data:
                times = list(stock_data.keys())
                prices = [float(stock_data[time]['1. open']) for time in times]
                if times and prices:
                    color = colors[idx % len(colors)]
                    ax.plot(times, prices, label=symbol, color=color)
                else:
                    print(f"No valid data for symbol {symbol}.")
            else:
                print(f"Failed to fetch historical data for symbol {symbol}.")

        ax.set_xlabel('Time')
        ax.set_ylabel('Price')
        ax.set_title('Stock Price Trends')
        ax.legend()

        # Add the chart to the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=trends_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show_statistics(self):
        if not self.portfolio:
            messagebox.showwarning("No Stocks", "Your portfolio is empty.")
            return

        # Create a new window for the statistics
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Stock Statistics")
        stats_window.geometry("800x600")

        tk.Label(stats_window, text="Stock Statistics", font=("Helvetica", 20, 'bold')).pack(pady=10)

        stats_text = tk.Text(stats_window, wrap=tk.WORD, height=20, width=80, font=("Helvetica", 12))
        stats_text.pack(padx=10, pady=10)

        stats_text.tag_configure('bold', font=("Helvetica", 12, 'bold'))
        stats_text.tag_configure('highlight_avg', foreground=COLOR_SCHEME['highlight_avg'])
        stats_text.tag_configure('highlight_high', foreground=COLOR_SCHEME['highlight_high'])
        stats_text.tag_configure('highlight_low', foreground=COLOR_SCHEME['highlight_low'])

        for symbol in self.portfolio.keys():
            stock_data = self.get_historical_data(symbol)
            if stock_data:
                prices = [float(data['1. open']) for data in stock_data.values()]
                if prices:
                    avg_price = sum(prices) / len(prices)
                    highest_price = max(prices)
                    lowest_price = min(prices)
                    stats_text.insert(tk.END, f"Statistics for {symbol}:\n", 'bold')
                    stats_text.insert(tk.END, f"  Average Price: ", 'bold')
                    stats_text.insert(tk.END, f"${avg_price:.2f}\n", 'highlight_avg')
                    stats_text.insert(tk.END, f"  Highest Price: ", 'bold')
                    stats_text.insert(tk.END, f"${highest_price:.2f}\n", 'highlight_high')
                    stats_text.insert(tk.END, f"  Lowest Price: ", 'bold')
                    stats_text.insert(tk.END, f"${lowest_price:.2f}\n\n", 'highlight_low')
                else:
                    stats_text.insert(tk.END, f"No valid prices for symbol {symbol}.\n", 'bold')

    def export_portfolio(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as file:
                json.dump(self.portfolio, file)
            self.status_label.config(text="Portfolio exported successfully.")

    def import_portfolio(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as file:
                self.portfolio = json.load(file)
            self.show_portfolio()
            self.status_label.config(text="Portfolio imported successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    app = StockPortfolioTracker(root)
    root.mainloop()
