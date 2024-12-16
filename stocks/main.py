import requests # pip install requests
import sys

def load_api_config(file_path):
    """Load API key and URL from a file."""
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            if len(lines) < 2:
                print("Error: The file must contain at least two lines: API key and URL.")
                return None, None
            api_key = lines[0].strip()
            api_url = lines[1].strip()
            return api_key, api_url
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
    return None, None

def get_real_time_stock_price(api_key, api_url, stock_symbol):
    """Fetch real-time stock price for a given symbol."""
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": stock_symbol,
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

            print(f"{stock_symbol} Price: ${stock_price} as of {latest_time}")
        elif "Error Message" in data:
            print("Error: Invalid stock symbol or data unavailable.")
        else:
            print("Error: Could not fetch real-time data. Check API limits or symbol.")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    # Load API key from file
    api_key, api_url = load_api_config("API.txt")
    
    if not api_key:
        print("Failed to load API config. Exiting.")
        return

    # Check for a stock symbol argument
    if len(sys.argv) > 1:
        stock_symbol = sys.argv[1].strip().upper()
    else:
        # Prompt user if no argument is passed
        stock_symbol = input("Enter the stock ticker symbol (e.g., AAPL): ").strip().upper()

    # Fetch and display the stock price
    get_real_time_stock_price(api_key, api_url, stock_symbol)

if __name__ == "__main__":
    main()