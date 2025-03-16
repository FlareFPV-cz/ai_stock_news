import logging
import json
from typing import Dict, List, Any, Optional
import requests
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StockPriceFetcher:
    def __init__(self, config_file: str = 'config/config.json'):
        """
        Initialize the StockPriceFetcher with the user configuration file.
        
        Args:
            config_file: Path to the user configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
        self.api_key = self.config.get('stock_prices', {}).get('api_key', '')
        self.provider = self.config.get('stock_prices', {}).get('provider', 'alphavantage')
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Load user configuration from the configuration file.
        
        Returns:
            Dictionary containing user configuration
        """
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading configuration: {e}")
            return {}
    
    def fetch_stock_prices(self) -> Dict[str, Dict[str, Any]]:
        """
        Fetch current stock prices for the tickers specified in the configuration.
        
        Returns:
            Dictionary with stock price data by ticker
        """
        tickers = self.config.get('tickers', [])
        if not tickers:
            logger.warning("No tickers specified in configuration for stock price fetching")
            return {}
        
        if not self.api_key:
            logger.warning("No API key configured for stock price fetching")
            return {}
        
        stock_prices = {}
        
        for ticker in tickers:
            try:
                price_data = self._fetch_ticker_price(ticker)
                if price_data:
                    stock_prices[ticker] = price_data
            except Exception as e:
                logger.error(f"Error fetching price for {ticker}: {e}")
        
        return stock_prices
    
    def _fetch_ticker_price(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch price data for a specific ticker.
        
        Args:
            ticker: The stock ticker symbol
            
        Returns:
            Dictionary with price data
        """
        if self.provider == 'alphavantage':
            return self._fetch_from_alphavantage(ticker)
        elif self.provider == 'finnhub':
            return self._fetch_from_finnhub(ticker)
        else:
            logger.error(f"Unsupported stock price provider: {self.provider}")
            return {}
    
    def _fetch_from_alphavantage(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch stock price from Alpha Vantage API.
        
        Args:
            ticker: The stock ticker symbol
            
        Returns:
            Dictionary with price data
        """
        try:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={self.api_key}"
            response = requests.get(url)
            data = response.json()
            
            if 'Global Quote' in data and data['Global Quote']:
                quote = data['Global Quote']
                return {
                    'price': quote.get('05. price', 'N/A'),
                    'change': quote.get('09. change', 'N/A'),
                    'percent_change': quote.get('10. change percent', 'N/A').replace('%', ''),
                    'volume': quote.get('06. volume', 'N/A'),
                    'latest_trading_day': quote.get('07. latest trading day', 'N/A')
                }
            else:
                logger.warning(f"No price data returned for {ticker} from Alpha Vantage")
                return {}
                
        except Exception as e:
            logger.error(f"Error fetching from Alpha Vantage for {ticker}: {e}")
            return {}
    
    def _fetch_from_finnhub(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch stock price from Finnhub API.
        
        Args:
            ticker: The stock ticker symbol
            
        Returns:
            Dictionary with price data
        """
        try:
            url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={self.api_key}"
            response = requests.get(url)
            data = response.json()
            
            if 'c' in data:  # Current price
                current_price = data['c']
                previous_close = data['pc']
                change = current_price - previous_close
                percent_change = (change / previous_close) * 100 if previous_close != 0 else 0
                
                return {
                    'price': f"{current_price:.2f}",
                    'change': f"{change:.2f}",
                    'percent_change': f"{percent_change:.2f}",
                    'volume': str(data.get('v', 'N/A')),
                    'latest_trading_day': datetime.now().strftime('%Y-%m-%d')
                }
            else:
                logger.warning(f"No price data returned for {ticker} from Finnhub")
                return {}
                
        except Exception as e:
            logger.error(f"Error fetching from Finnhub for {ticker}: {e}")
            return {}