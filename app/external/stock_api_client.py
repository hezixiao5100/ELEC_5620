"""
Stock API Client
Handles external stock data API calls using Yahoo Finance
"""
import httpx
import asyncio
import yfinance as yf
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

class StockAPIClient:
    """
    Client for stock data APIs using Yahoo Finance
    """
    
    def __init__(self):
        self.logger = logging.getLogger("stock_api_client")
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart"
    
    async def get_current_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get current stock price using Yahoo Finance
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Current price data
        """
        try:
            # Use yfinance to get real data
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get current price
            hist = ticker.history(period="1d")
            if hist.empty:
                raise ValueError(f"No data found for symbol {symbol}")
            
            current_price = hist['Close'].iloc[-1]
            volume = hist['Volume'].iloc[-1]
            
            return {
                "symbol": symbol,
                "price": float(current_price),
                "volume": int(volume),
                "market_cap": info.get('marketCap', 0),
                "currency": info.get('currency', 'USD'),
                "exchange": info.get('exchange', 'NASDAQ'),
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to get current price for {symbol}: {str(e)}")
            return {"error": str(e)}
    
    async def get_historical_data(self, symbol: str, period: str = "30d") -> List[Dict[str, Any]]:
        """
        Get historical stock data using Yahoo Finance
        
        Args:
            symbol: Stock symbol
            period: Data period (1d, 1w, 1m, 3m, 1y)
            
        Returns:
            Historical price data
        """
        try:
            # Use yfinance to get real historical data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                raise ValueError(f"No historical data found for symbol {symbol}")
            
            historical_data = []
            for date, row in hist.iterrows():
                historical_data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "open": float(row['Open']),
                    "high": float(row['High']),
                    "low": float(row['Low']),
                    "close": float(row['Close']),
                    "volume": int(row['Volume'])
                })
            
            return historical_data
        except Exception as e:
            self.logger.error(f"Failed to get historical data for {symbol}: {str(e)}")
            return []
    
    async def get_market_indices(self) -> Dict[str, Any]:
        """
        Get market indices data
        
        Returns:
            Market indices data
        """
        try:
            await asyncio.sleep(0.1)
            
            return {
                "sp500": {"value": 4500.25, "change": 1.2},
                "nasdaq": {"value": 14000.50, "change": 0.8},
                "dow": {"value": 35000.75, "change": 0.5}
            }
        except Exception as e:
            self.logger.error(f"Failed to get market indices: {str(e)}")
            return {"error": str(e)}