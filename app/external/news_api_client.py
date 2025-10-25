"""
News API Client
Handles external news API calls using NewsAPI
"""
import httpx
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging
import os

class NewsAPIClient:
    """
    Client for news data APIs using NewsAPI
    """
    
    def __init__(self):
        self.logger = logging.getLogger("news_api_client")
        self.base_url = "https://newsapi.org/v2"
        self.api_key = os.getenv("NEWS_API_KEY", "your_news_api_key_here")
    
    async def get_stock_news(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get news articles for a stock using NewsAPI
        
        Args:
            symbol: Stock symbol
            limit: Maximum number of articles
            
        Returns:
            List of news articles
        """
        try:
            async with httpx.AsyncClient() as client:
                # Search for news about the stock
                params = {
                    "q": f"{symbol} stock",
                    "apiKey": self.api_key,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": limit
                }
                
                response = await client.get(f"{self.base_url}/everything", params=params)
                response.raise_for_status()
                
                data = response.json()
                articles = data.get("articles", [])
                
                news_articles = []
                for article in articles:
                    # Simple sentiment analysis based on title keywords
                    sentiment = self._analyze_sentiment(article.get("title", ""))
                    
                    news_articles.append({
                        "title": article.get("title", ""),
                        "content": article.get("description", ""),
                        "url": article.get("url", ""),
                        "published_at": article.get("publishedAt", ""),
                        "source": article.get("source", {}).get("name", "Unknown"),
                        "sentiment": sentiment,
                        "relevance_score": 0.8  # High relevance for stock-specific news
                    })
                
                return news_articles
        except Exception as e:
            self.logger.error(f"Failed to get news for {symbol}: {str(e)}")
            return []
    
    def _analyze_sentiment(self, text: str) -> str:
        """
        Simple sentiment analysis based on keywords
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment: positive, negative, or neutral
        """
        positive_words = ["up", "rise", "gain", "profit", "growth", "positive", "bullish", "strong"]
        negative_words = ["down", "fall", "loss", "decline", "negative", "bearish", "weak", "drop"]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    async def get_market_sentiment(self) -> Dict[str, Any]:
        """
        Get overall market sentiment
        
        Returns:
            Market sentiment data
        """
        try:
            await asyncio.sleep(0.1)
            
            return {
                "overall_sentiment": "NEUTRAL",
                "sentiment_score": 0.5,
                "fear_greed_index": 50,
                "market_news_count": 25
            }
        except Exception as e:
            self.logger.error(f"Failed to get market sentiment: {str(e)}")
            return {"error": str(e)}