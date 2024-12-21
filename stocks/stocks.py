import requests # pip install requests
import configparser
import sys
import importlib
import valuation as val

def load_config(file_path, group, *parameters):
    """
    Load specific parameters from a given group in the config file.

    Args:
        file_path (str): Path to the configuration file.
        group (str): The group/section name in the config file.
        *parameters (str): Names of the parameters (keys) to load.

    Returns:
        dict: A dictionary containing the requested parameters and their values.
    """
    config = configparser.ConfigParser()
    try:
        config.read(file_path)
        
        # Access the specified group
        section = config[group]
        
        # Load requested parameters
        loaded_params = {}
        for param in parameters:
            if param in section:
                loaded_params[param] = section[param]
            else:
                print(f"Warning: '{param}' not found in section '{group}'")

        return loaded_params

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except KeyError as e:
        print(f"Error: Missing section or key: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return {}

def get_realtime_stock_price(api_key, api_url, stock_symbol):
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
    # Load API configuration
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
        stock_symbol = sys.argv[1].strip().upper()
    else:
        # Prompt user if no argument is passed
        stock_symbol = input("Enter the stock ticker symbol (e.g., AAPL): ").strip().upper()

    # Fetch and display the stock price
    get_realtime_stock_price(api_key, api_url, stock_symbol)

if __name__ == "__main__":
    main()