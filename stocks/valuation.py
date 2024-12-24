import requests # pip install requests
import configparser
import sys

def get_financial_ratios(api_key, api_url, ticker):
    """
    Fetch key financial ratios for the given stock ticker using Alpha Vantage API.
    
    Args:
        ticker (str): Stock ticker symbol (e.g., "AAPL").
    
    Returns:
        dict: A dictionary with the requested financial ratios.
    """
    params = {
        "function": "OVERVIEW",
        "symbol": ticker,
        "apikey": api_key
    }
    
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data or "Symbol" not in data:
            return {"error": "Invalid ticker symbol or data unavailable"}
        
        # Extract required ratios
        result = {
            "PE Ratio": data.get("PERatio", "N/A"),
            "PB Ratio": data.get("PriceToBookRatio", "N/A"),
            "PCF Ratio": data.get("PriceToCashFlowRatio", "N/A"),
            "PS Ratio": data.get("PriceToSalesRatioTTM", "N/A"),
            "Dividend Yield": data.get("DividendYield", "N/A"),
            "DCF Value": data.get("TrailingPE", "N/A"),  # Substitute if Alpha Vantage doesn't provide DCF
            "DCM Value": data.get("ForwardPE", "N/A"),   # Substitute if Alpha Vantage doesn't provide DCM
        }
        return result
    
    except Exception as e:
        return {"error": f"An error occurred: {e}"}