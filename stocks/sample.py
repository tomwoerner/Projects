# A new sample from scratch.

import requests
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from stocks import load_config

# Alpha Vantage API setup
config = load_config("config.ini", "API", "key", "url", "library")

# Check if all required configuration is present
if not all(key in config for key in ["key", "url", "library"]):
    print("Failed to load complete API configuration. Exiting.")

api_key = config["key"]
api_url = config["url"]
api_lib = config["library"]

def fetch_time_series(symbol):
    """
    Fetch historical time series data for a given stock symbol.
    """
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": symbol,
        "apikey": api_key,
        "outputsize": "compact"
    }
    response = requests.get(api_url, params=params)
    # debug
    print(response.json())
    data = response.json()

    # Ensure the response contains the expected data
    time_series = data.get("Time Series (Daily)", {})
    if not time_series:
        print("Error: 'Time Series (Daily)' key is missing in the response.")
        return pd.DataFrame()  # Return an empty DataFrame
    
    # Build the dataFrame
    df = pd.DataFrame.from_dict(time_series, orient="index", dtype=float)
    df.rename(columns={
        "1. open": "Open",
        "2. high": "High",
        "3. low": "Low",
        "4. close": "Close",
        "5. adjusted close": "Adj Close",
        "6. volume": "Volume"
    }, inplace=True)
    df.index = pd.to_datetime(df.index)
    return df.sort_index()

def fetch_fundamentals(symbol):
    """
    Fetch fundamental data for a given stock symbol.
    """
    params = {
        "function": "OVERVIEW",
        "symbol": symbol,
        "apikey": api_key
    }
    response = requests.get(api_url, params=params)
    return response.json()

def generate_report(symbol, company_name, df, fundamentals):
    """
    Generate a research report in PDF format.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title Page
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"{company_name} ({symbol}) - Research Report", ln=True, align="C")
    pdf.ln(10)
    
    # Overview
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Executive Summary", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 10, f"Sector: {fundamentals.get('Sector', 'N/A')}\n"
                          f"Industry: {fundamentals.get('Industry', 'N/A')}\n"
                          f"Market Cap: ${fundamentals.get('MarketCapitalization', 'N/A')}\n"
                          f"PE Ratio: {fundamentals.get('PERatio', 'N/A')}\n"
                          f"Dividend Yield: {fundamentals.get('DividendYield', 'N/A')}\n")

    # Historical Performance
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Historical Performance", ln=True)
    
    # Plot and add performance chart
    if "Adj Close" in df.columns:
        df["Adj Close"].plot(title=f"{symbol} - Adjusted Close Prices", figsize=(10, 5))
        plt.ylabel("Price ($)")
        plt.savefig("performance.png")
        plt.close()
        pdf.image("performance.png", x=10, y=pdf.get_y(), w=190)
        pdf.ln(60)
    elif "Close" in df.columns:
        df["Close"].plot(title=f"{symbol} - Close Prices", figsize=(10, 5))
        plt.ylabel("Price ($)")
        plt.savefig("performance.png")
        plt.close()
        pdf.image("performance.png", x=10, y=pdf.get_y(), w=190)
        pdf.ln(60)
    else:
        print("Neither 'Adj Close' nor 'Close' columns are available in the data.")
        return

    # Valuation
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Valuation Metrics", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 10, f"Price/Earnings Ratio: {fundamentals.get('PERatio', 'N/A')}\n"
                          f"PEG Ratio: {fundamentals.get('PEGRatio', 'N/A')}\n"
                          f"Price/Book Ratio: {fundamentals.get('PriceToBookRatio', 'N/A')}\n")

    # Risks and Opportunities
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Risks & Opportunities", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 10, "Add qualitative analysis here.")

    # Save Report
    pdf.output(f"{symbol}_research_report.pdf")

# Main script execution
if __name__ == "__main__":
    stock_symbol = "AAPL"  # Example symbol
    company_name = "Apple Inc."
    
    print("Fetching data...")
    stock_data = fetch_time_series(stock_symbol)
    print(stock_data.head())
    print(stock_data.columns)
    fundamentals = fetch_fundamentals(stock_symbol)
    
    print("Generating report...")
    generate_report(stock_symbol, company_name, stock_data, fundamentals)
    print(f"Report generated: {stock_symbol}_research_report.pdf")
