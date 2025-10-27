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
        
        if not news_data:
            raise ValueError("News data is required for emotional analysis")
        
        # Analyze news sentiment
        sentiment_analysis = await self.analyze_news_sentiment(news_data)
        
        # Analyze market sentiment
        market_sentiment = self.analyze_market_sentiment(stock_data)
        
        # Calculate fear & greed index
        fear_greed_index = await self.calculate_fear_greed_index(sentiment_analysis, market_sentiment)
        
        # Generate emotional signal
        emotional_signal = self.generate_emotional_signal(fear_greed_index)
        
        return {
            "symbol": stock_data.get("symbol", ""),
            "news_sentiment": sentiment_analysis,
            "market_sentiment": market_sentiment,
            "fear_greed_index": fear_greed_index,
            "emotional_signal": emotional_signal,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    async def analyze_news_sentiment(self, news_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment from news articles"""
        try:
            # Use AI service for sentiment analysis
            ai_sentiment = await self.ai_service.analyze_news_sentiment(news_data)
            
            # Fallback to simple keyword analysis if AI fails
            if "error" in ai_sentiment:
                sentiment_analysis = self._analyze_sentiment_fallback(news_data)
            else:
                sentiment_analysis = ai_sentiment
            
            return sentiment_analysis
            
        except Exception as e:
            self.logger.error(f"Failed to analyze news sentiment: {str(e)}")
            return {
                "sentiment_score": 0.5,
                "sentiment": "NEUTRAL",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _analyze_sentiment_fallback(self, news_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback sentiment analysis using keyword matching"""
        if not news_data:
            return {"sentiment_score": 0.5, "sentiment": "NEUTRAL", "confidence": 0.0}
        
        positive_keywords = ["growth", "profit", "gain", "rise", "positive", "bullish", "beat", "exceed"]
        negative_keywords = ["decline", "fall", "drop", "loss", "negative", "bearish", "miss", "plunge"]
        
        sentiment_scores = []
        
        for article in news_data:
            title = article.get("title", "").lower()
            content = article.get("content", "").lower()
            text = f"{title} {content}"
            
            positive_count = sum(1 for keyword in positive_keywords if keyword in text)
            negative_count = sum(1 for keyword in negative_keywords if keyword in text)
            
            if positive_count + negative_count > 0:
                sentiment_score = positive_count / (positive_count + negative_count)
            else:
                sentiment_score = 0.5  # Neutral if no keywords found
            
            sentiment_scores.append(sentiment_score)
        
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        
        if avg_sentiment > 0.6:
            sentiment = "POSITIVE"
        elif avg_sentiment < 0.4:
            sentiment = "NEGATIVE"
        else:
            sentiment = "NEUTRAL"
        
        return {
            "sentiment_score": round(avg_sentiment, 3),
            "sentiment": sentiment,
            "confidence": min(1.0, len(news_data) / 10.0)  # More articles = higher confidence
        }
    
    def analyze_market_sentiment(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market sentiment from stock data"""
        try:
            price_change = stock_data.get("price_change_percent", 0)
            volume = stock_data.get("volume", 0)
            avg_volume = stock_data.get("avg_volume", volume)
            
            # Price sentiment
            if price_change > 2:
                price_sentiment = "BULLISH"
            elif price_change < -2:
                price_sentiment = "BEARISH"
            else:
                price_sentiment = "NEUTRAL"
            
            # Volume sentiment
            if avg_volume > 0:
                volume_ratio = volume / avg_volume
                if volume_ratio > 1.5:
                    volume_sentiment = "HIGH_VOLUME"
                elif volume_ratio < 0.5:
                    volume_sentiment = "LOW_VOLUME"
                else:
                    volume_sentiment = "NORMAL_VOLUME"
            else:
                volume_sentiment = "UNKNOWN"
            
            # Overall market sentiment score
            sentiment_score = 0.5  # Start neutral
            if price_sentiment == "BULLISH":
                sentiment_score += 0.2
            elif price_sentiment == "BEARISH":
                sentiment_score -= 0.2
            
            if volume_sentiment == "HIGH_VOLUME":
                sentiment_score += 0.1
            elif volume_sentiment == "LOW_VOLUME":
                sentiment_score -= 0.1
            
            sentiment_score = max(0.0, min(1.0, sentiment_score))
            
            return {
                "price_sentiment": price_sentiment,
                "volume_sentiment": volume_sentiment,
                "sentiment_score": round(sentiment_score, 3),
                "price_change": price_change,
                "volume": volume,
                "volume_ratio": round(volume_ratio, 2) if avg_volume > 0 else 1.0
            }
            
        except Exception as e:
            self.logger.error(f"Market sentiment analysis failed: {str(e)}")
            return {
                "price_sentiment": "NEUTRAL",
                "volume_sentiment": "UNKNOWN",
                "sentiment_score": 0.5,
                "error": str(e)
            }
    
    async def calculate_fear_greed_index(self, news_sentiment: Dict[str, Any], market_sentiment: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Fear & Greed Index"""
        try:
            # Try to get AI-based Fear & Greed Index
            ai_fgi = await self.ai_service.get_fear_greed_index()
            
            # Calculate our own Fear & Greed Index
            news_score = news_sentiment.get("sentiment_score", 0.5) * 100
            market_score = market_sentiment.get("sentiment_score", 0.5) * 100
            
            # Weighted average (40% news, 60% market)
            calculated_fgi = (news_score * 0.4) + (market_score * 0.6)
            
            # Use AI result if available, otherwise use calculated
            if "error" not in ai_fgi:
                fear_greed_index = ai_fgi.get("index", calculated_fgi)
                category = ai_fgi.get("sentiment", self._get_fear_greed_category(calculated_fgi))
            else:
                fear_greed_index = calculated_fgi
                category = self._get_fear_greed_category(calculated_fgi)
            
            return {
                "index": round(fear_greed_index, 1),
                "category": category,
                "news_component": round(news_score, 1),
                "market_component": round(market_score, 1),
                "calculation_method": "ai" if "error" not in ai_fgi else "calculated"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to calculate Fear & Greed Index: {str(e)}")
            return {
                "index": 50.0,
                "category": "NEUTRAL",
                "news_component": 50.0,
                "market_component": 50.0,
                "error": str(e)
            }
    
    def _get_fear_greed_category(self, index: float) -> str:
        """Get Fear & Greed category based on index"""
        if index >= 80:
            return "EXTREME_GREED"
        elif index >= 60:
            return "GREED"
        elif index >= 40:
            return "NEUTRAL"
        elif index >= 20:
            return "FEAR"
        else:
            return "EXTREME_FEAR"
    
    def generate_emotional_signal(self, fear_greed: Dict[str, Any]) -> str:
        """Generate emotional trading signal based on Fear & Greed Index"""
        category = fear_greed.get("category", "NEUTRAL")
        
        # Contrarian approach: buy when fearful, sell when greedy
        if category in ["EXTREME_FEAR", "FEAR"]:
            return "BUY"
        elif category in ["EXTREME_GREED", "GREED"]:
            return "SELL"
        else:
            return "HOLD"