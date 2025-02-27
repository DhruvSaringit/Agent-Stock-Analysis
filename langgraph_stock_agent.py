
import yfinance as yf
import matplotlib.pyplot as plt
from typing import Dict, Any, TypedDict, Optional

from langgraph.graph import StateGraph

class StockAgentState(TypedDict):
    command: str
    result: Optional[str]

def fetch_stock_data(ticker: str, period: str = "1mo", interval: str = "1d"):
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

def visualize_stock(data, ticker: str):
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

def get_stats(data, ticker: str):
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

def compare_stocks(tickers: list, period: str = "1mo", interval: str = "1d"):
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

def process_command(state: StockAgentState) -> StockAgentState:
    """
    Process a command from the user.
    Supported commands:
      - get [TICKER] [PERIOD] [INTERVAL]
      - stats [TICKER] [PERIOD] [INTERVAL]
      - compare [TICKER1] [TICKER2] ...
      - help
    :param state: The current state containing the command.
    :return: Updated state with result.
    """
    command = state.get("command", "")
    parts = command.strip().split()
    
    if not parts:
        state["result"] = "Empty command. Use 'help' to see available commands."
        return state

    cmd = parts[0].lower()

    if cmd == "help":
        state["result"] = (
            "Available commands:\n"
            "  get [TICKER] [PERIOD] [INTERVAL]  - Fetch and plot stock data. (Defaults: PERIOD=1mo, INTERVAL=1d)\n"
            "  stats [TICKER] [PERIOD] [INTERVAL] - Show basic statistics for the stock. (Defaults: PERIOD=1mo, INTERVAL=1d)\n"
            "  compare [TICKER1] [TICKER2] ...    - Compare multiple stocks on a single chart. (Defaults: PERIOD=1mo, INTERVAL=1d)\n"
            "  exit                             - Quit the application.\n"
            "  help                             - Show this help message."
        )
    
    elif cmd == "get":
        if len(parts) < 2:
            state["result"] = "Invalid command. Use: get [TICKER] [PERIOD] [INTERVAL]"
            return state
            
        ticker = parts[1].upper()
        period = parts[2] if len(parts) >= 3 else "1mo"
        interval = parts[3] if len(parts) >= 4 else "1d"
        
        data = fetch_stock_data(ticker, period, interval)
        if data is None:
            state["result"] = f"No data found for ticker {ticker}."
            return state
            
        result = visualize_stock(data, ticker)
        state["result"] = result
    
    elif cmd == "stats":
        if len(parts) < 2:
            state["result"] = "Invalid command. Use: stats [TICKER] [PERIOD] [INTERVAL]"
            return state
            
        ticker = parts[1].upper()
        period = parts[2] if len(parts) >= 3 else "1mo"
        interval = parts[3] if len(parts) >= 4 else "1d"
        
        data = fetch_stock_data(ticker, period, interval)
        result = get_stats(data, ticker)
        state["result"] = result
    
    elif cmd == "compare":
        if len(parts) < 2:
            state["result"] = "Invalid command. Use: compare [TICKER1] [TICKER2] ..."
            return state
            
        tickers = [t.upper() for t in parts[1:]]
        result = compare_stocks(tickers)
        state["result"] = result
    
    else:
        state["result"] = "Unknown command. Use 'help' to see available commands."
    
    return state

def main():
  
    workflow = StateGraph(state_schema=StockAgentState)
    
    workflow.add_node("command_processor", process_command)
    
    workflow.set_entry_point("command_processor")

    app = workflow.compile()
    
    print("Welcome to the Stock Agent powered by yfinance!")
    print("Type 'help' to see available commands or 'exit' to quit.")
    
    while True:
        user_input = input(">> ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
       
        state = {"command": user_input, "result": None}
        
        
        result = app.invoke(state)
    
        print(result["result"])

if __name__ == "__main__":
    main()
