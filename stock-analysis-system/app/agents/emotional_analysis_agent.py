"""
Emotional Analysis Agent
Analyzes market sentiment and emotional factors
"""
from typing import Dict, Any, List
from datetime import datetime

from app.agents.base_agent import BaseAgent

class EmotionalAnalysisAgent(BaseAgent):
    """
    Agent responsible for emotional and sentiment analysis
    """
    
    def __init__(self, agent_id: str = "emotional_analysis"):
        """
        Initialize Emotional Analysis Agent
        
        Args:
            agent_id: Agent identifier
        """
        super().__init__(agent_id, "Emotional Analysis Agent")
        from app.services.ai_analysis_service import AIAnalysisService
        self.ai_service = AIAnalysisService()
    
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute emotional analysis task
        
        Args:
            task_data: Task parameters including news data
            
        Returns:
            Emotional analysis results
        """
        news_data = task_data.get("news_data", [])
        stock_data = task_data.get("stock_data", {})
        
        # Analyze news sentiment
        sentiment_analysis = await self.analyze_news_sentiment(news_data)
        
        # Analyze market sentiment
        market_sentiment = self.analyze_market_sentiment(stock_data)
        
        # Calculate fear & greed index
        fear_greed_index = await self.calculate_fear_greed_index(sentiment_analysis, market_sentiment)
        
        return {
            "symbol": stock_data.get("symbol", ""),
            "news_sentiment": sentiment_analysis,
            "market_sentiment": market_sentiment,
            "fear_greed_index": fear_greed_index,
            "emotional_signal": self.generate_emotional_signal(fear_greed_index),
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    async def analyze_news_sentiment(self, news_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment from news articles using AI"""
        try:
            # Use AI service for sentiment analysis
            sentiment_results = await self.ai_service.analyze_news_sentiment(news_data)
            return sentiment_results
        except Exception as e:
            self.logger.error(f"Failed to analyze news sentiment with AI: {str(e)}")
            # Fallback to simple sentiment analysis
            if not news_data:
                return {"sentiment_score": 0.5, "sentiment": "NEUTRAL", "confidence": 0.0}
            
            # Calculate average sentiment
            sentiments = [article.get("sentiment", "neutral") for article in news_data]
            sentiment_scores = []
            
            for sentiment in sentiments:
                if sentiment == "positive":
                    sentiment_scores.append(0.8)
                elif sentiment == "negative":
                    sentiment_scores.append(0.2)
                else:
                    sentiment_scores.append(0.5)
            
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            
            # Determine sentiment category
            if avg_sentiment > 0.6:
                sentiment = "POSITIVE"
            elif avg_sentiment < 0.4:
                sentiment = "NEGATIVE"
            else:
                sentiment = "NEUTRAL"
            
            return {
                "sentiment_score": round(avg_sentiment, 2),
                "sentiment": sentiment,
                "confidence": min(1.0, len(news_data) / 10.0),  # More news = higher confidence
                "article_count": len(news_data)
            }
    
    def analyze_market_sentiment(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market sentiment indicators"""
        price_change_percent = stock_data.get("price_change_percent", 0)
        volume = stock_data.get("volume", 0)
        
        # Price momentum sentiment
        if price_change_percent > 2:
            price_sentiment = "BULLISH"
        elif price_change_percent < -2:
            price_sentiment = "BEARISH"
        else:
            price_sentiment = "NEUTRAL"
        
        # Volume sentiment
        if volume > 1000000:  # High volume threshold
            volume_sentiment = "HIGH_INTEREST"
        else:
            volume_sentiment = "NORMAL"
        
        return {
            "price_sentiment": price_sentiment,
            "volume_sentiment": volume_sentiment,
            "price_change": price_change_percent,
            "volume": volume
        }
    
    async def calculate_fear_greed_index(self, news_sentiment: Dict[str, Any], market_sentiment: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Fear & Greed Index using AI"""
        try:
            # Use AI service for Fear & Greed Index
            fgi = await self.ai_service.get_fear_greed_index()
            return fgi
        except Exception as e:
            self.logger.error(f"Failed to get Fear & Greed Index with AI: {str(e)}")
            # Fallback to calculated index
            # News sentiment component (40%)
            news_score = news_sentiment.get("sentiment_score", 0.5) * 100
            
            # Market sentiment component (60%)
            price_change = market_sentiment.get("price_change", 0)
            if price_change > 0:
                market_score = min(100, 50 + (price_change * 10))
            else:
                market_score = max(0, 50 + (price_change * 10))
            
            # Weighted average
            fear_greed = (news_score * 0.4) + (market_score * 0.6)
            
            # Determine category
            if fear_greed >= 75:
                category = "EXTREME_GREED"
            elif fear_greed >= 55:
                category = "GREED"
            elif fear_greed >= 45:
                category = "NEUTRAL"
            elif fear_greed >= 25:
                category = "FEAR"
            else:
                category = "EXTREME_FEAR"
            
            return {
                "index": round(fear_greed, 1),
                "category": category,
                "news_component": round(news_score, 1),
                "market_component": round(market_score, 1)
            }
    
    def generate_emotional_signal(self, fear_greed: Dict[str, Any]) -> str:
        """Generate emotional trading signal"""
        index = fear_greed.get("index", 50)
        category = fear_greed.get("category", "NEUTRAL")
        
        # Contrarian signals
        if category in ["EXTREME_FEAR", "FEAR"]:
            return "BUY"  # Buy when there's fear
        elif category in ["EXTREME_GREED", "GREED"]:
            return "SELL"  # Sell when there's greed
        else:
            return "HOLD"