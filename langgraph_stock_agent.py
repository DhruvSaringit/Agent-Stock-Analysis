
import yfinance as yf
import matplotlib.pyplot as plt

# --- Minimal Implementations for Graph and Node ---
class Node:
    def run(self, *args, **kwargs):
        raise NotImplementedError

class Graph:
    def __init__(self):
        self.nodes = {}
    def add_node(self, key, node):
        self.nodes[key] = node
    def get_node(self, key):
        return self.nodes.get(key)


class YFinanceTool(Node):
    def run(self, ticker: str, period: str = "1mo", interval: str = "1d"):
        """
        Fetch historical stock data for a given ticker.
        :param ticker: Stock ticker symbol (e.g., "AAPL")
        :param period: Data period (default "1mo")
        :param interval: Data interval (default "1d")
        :return: DataFrame with historical data or None if no data found.
        """
        stock = yf.Ticker(ticker)
        data = stock.history(period=period, interval=interval)
        if data.empty:
            return None
        return data

class VisualizationTool(Node):
    def run(self, data, ticker: str):
        """
        Visualize the closing price data for the ticker.
        :param data: DataFrame with stock data.
        :param ticker: Stock ticker symbol.
        :return: A status message.
        """
        if data is None:
            return f"No data available for ticker {ticker}"
        plt.figure(figsize=(10, 5))
        plt.plot(data.index, data['Close'], marker='o', linestyle='-')
        plt.title(f'{ticker} Stock Price')
        plt.xlabel('Date')
        plt.ylabel('Closing Price')
        plt.grid(True)
        plt.tight_layout()
        plt.show()
        return f"Displayed chart for {ticker}"

class StatsTool(Node):
    def run(self, data, ticker: str):
        """
        Return basic statistics for the given stock data.
        """
        if data is None:
            return f"No data available for ticker {ticker}"
        closing_prices = data['Close']
        min_price = closing_prices.min()
        max_price = closing_prices.max()
        avg_price = closing_prices.mean()
        return (f"Statistics for {ticker}:\n"
                f"  - Min: {min_price:.2f}\n"
                f"  - Max: {max_price:.2f}\n"
                f"  - Avg: {avg_price:.2f}")

class ComparisonTool(Node):
    def run(self, tickers: list, period: str = "1mo", interval: str = "1d"):
        """
        Compare closing prices for multiple tickers by plotting them on one chart.
        """
        plt.figure(figsize=(10, 5))
        valid_tickers = []
        for ticker in tickers:
            data = yf.Ticker(ticker).history(period=period, interval=interval)
            if not data.empty:
                plt.plot(data.index, data['Close'], marker='o', linestyle='-', label=ticker)
                valid_tickers.append(ticker)
            else:
                print(f"No data found for {ticker}")
        if not valid_tickers:
            return "No valid ticker data to compare."
        plt.title("Stock Price Comparison")
        plt.xlabel("Date")
        plt.ylabel("Closing Price")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
        return f"Displayed comparison for: {', '.join(valid_tickers)}"



class StockAgent(Node):
    def __init__(self, graph):
        """
        Initialize the agent with access to the overall graph.
        :param graph: The Graph instance.
        """
        self.graph = graph

    def run(self, command: str):
        """
        Process a command.
        Supported commands:
          - get [TICKER] [PERIOD] [INTERVAL]
          - stats [TICKER] [PERIOD] [INTERVAL]
          - compare [TICKER1] [TICKER2] ...
          - help
        :param command: User input command.
        :return: Result message.
        """
        parts = command.strip().split()
        if not parts:
            return "Empty command. Use 'help' to see available commands."

        cmd = parts[0].lower()

        if cmd == "help":
            return (
                "Available commands:\n"
                "  get [TICKER] [PERIOD] [INTERVAL]  - Fetch and plot stock data. (Defaults: PERIOD=1mo, INTERVAL=1d)\n"
                "  stats [TICKER] [PERIOD] [INTERVAL] - Show basic statistics for the stock. (Defaults: PERIOD=1mo, INTERVAL=1d)\n"
                "  compare [TICKER1] [TICKER2] ...    - Compare multiple stocks on a single chart. (Defaults: PERIOD=1mo, INTERVAL=1d)\n"
                "  exit                             - Quit the application.\n"
                "  help                             - Show this help message."
            )

        elif cmd == "get":
            if len(parts) < 2:
                return "Invalid command. Use: get [TICKER] [PERIOD] [INTERVAL]"
            ticker = parts[1].upper()
            period = parts[2] if len(parts) >= 3 else "1mo"
            interval = parts[3] if len(parts) >= 4 else "1d"
            data = self.graph.get_node("yfinance_tool").run(ticker, period, interval)
            if data is None:
                return f"No data found for ticker {ticker}."
            result = self.graph.get_node("visualization_tool").run(data, ticker)
            return result

        elif cmd == "stats":
            if len(parts) < 2:
                return "Invalid command. Use: stats [TICKER] [PERIOD] [INTERVAL]"
            ticker = parts[1].upper()
            period = parts[2] if len(parts) >= 3 else "1mo"
            interval = parts[3] if len(parts) >= 4 else "1d"
            data = self.graph.get_node("yfinance_tool").run(ticker, period, interval)
            result = self.graph.get_node("stats_tool").run(data, ticker)
            return result

        elif cmd == "compare":
            if len(parts) < 2:
                return "Invalid command. Use: compare [TICKER1] [TICKER2] ..."
            tickers = [t.upper() for t in parts[1:]]
            result = self.graph.get_node("comparison_tool").run(tickers)
            return result

        else:
         return "Unknown command. Use 'help' to see available commands."

#Main Function 

def main():

    graph = Graph()
    yfinance_tool = YFinanceTool()
    visualization_tool = VisualizationTool()
    stats_tool = StatsTool()
    comparison_tool = ComparisonTool()
    stock_agent = StockAgent(graph)  
    graph.add_node("yfinance_tool", yfinance_tool)
    graph.add_node("visualization_tool", visualization_tool)
    graph.add_node("stats_tool", stats_tool)
    graph.add_node("comparison_tool", comparison_tool)
    graph.add_node("stock_agent", stock_agent)
    print("Welcome to the Stock Agent powered by yfinance!")
    print("Type 'help' to see available commands or 'exit' to quit.")
    while True:
        user_input = input(">> ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        result = graph.get_node("stock_agent").run(user_input)
        print(result)

if __name__ == "__main__":
    main()
