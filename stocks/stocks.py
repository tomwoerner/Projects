import requests # pip install requests
import sys
import importlib
from valuation import get_financial_ratios
from utils import load_config


def get_realtime_stock_price(api_key, api_url, ticker):
    """Fetch real-time stock price for a given symbol."""
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": ticker,
        "interval": "1min",
        "apikey": api_key
    }

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()

        if "Time Series (1min)" in data:
            latest_time = list(data["Time Series (1min)"].keys())[0]
            latest_data = data["Time Series (1min)"][latest_time]
            stock_price = latest_data["4. close"]

            print(f"{ticker} Price: ${stock_price} as of {latest_time}")
        elif "Error Message" in data:
            print("Error: Invalid stock symbol or data unavailable.")
        else:
            print("Error: Could not fetch real-time data. Check API limits or symbol.")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    #print(sys.builtin_module_names)
    config = load_config("config.ini", "API", "key", "url", "library")
    
    # Check if all required configuration is present
    if not all(key in config for key in ["key", "url", "library"]):
        print("Failed to load complete API configuration. Exiting.")
        return
    
    api_key = config["key"]
    api_url = config["url"]
    api_lib = config["library"]

    # Check for a stock symbol argument
    if len(sys.argv) > 1:
        ticker = sys.argv[1].strip().upper()
    else:
        # Prompt user if no argument is passed
        ticker = input("Enter the stock ticker symbol (e.g., AAPL): ").strip().upper()

    get_realtime_stock_price(api_key, api_url, ticker)
    print(get_financial_ratios(api_key, api_url, ticker))

if __name__ == "__main__":
    main()