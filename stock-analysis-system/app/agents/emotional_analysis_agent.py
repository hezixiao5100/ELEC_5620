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
        Execute emotional analysis task (Enhanced version)
        
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
        
        # Generate emotional signal
        emotional_signal = self.generate_emotional_signal(fear_greed_index)
        
        # Enhanced analysis
        sentiment_trend = self.analyze_sentiment_trend(news_data)
        categorized_sentiment = self.categorize_news_sentiment(news_data)
        key_topics = self.extract_key_topics(news_data)
        
        return {
            "symbol": stock_data.get("symbol", ""),
            "news_sentiment": sentiment_analysis,
            "market_sentiment": market_sentiment,
            "fear_greed_index": fear_greed_index,
            "emotional_signal": emotional_signal,
            "sentiment_trend": sentiment_trend,
            "categorized_sentiment": categorized_sentiment,
            "key_topics": key_topics,
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
    
    def analyze_sentiment_trend(self, news_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze sentiment trend over time
        
        Args:
            news_data: List of news articles with timestamps
            
        Returns:
            Sentiment trend analysis
        """
        if not news_data:
            return {"trend": "STABLE", "change": 0, "description": "没有足够的数据"}
        
        # Sort by date
        try:
            sorted_news = sorted(news_data, key=lambda x: x.get("published_at", ""))
        except:
            # If sorting fails, assume no trend
            return {"trend": "STABLE", "change": 0, "description": "无法分析趋势"}
        
        # Split into two halves
        mid = len(sorted_news) // 2
        if mid < 1:
            return {"trend": "STABLE", "change": 0, "description": "数据量不足"}
        
        first_half = sorted_news[:mid]
        second_half = sorted_news[mid:]
        
        # Calculate average sentiment for each half
        def avg_sentiment(news_list):
            scores = []
            for news in news_list:
                sentiment = news.get("sentiment", "neutral")
                if sentiment == "positive":
                    scores.append(0.8)
                elif sentiment == "negative":
                    scores.append(0.2)
                else:
                    scores.append(0.5)
            return sum(scores) / len(scores) if scores else 0.5
        
        first_avg = avg_sentiment(first_half)
        second_avg = avg_sentiment(second_half)
        
        # Calculate change
        change = second_avg - first_avg
        
        # Determine trend
        if change > 0.1:
            trend = "IMPROVING"
            trend_emoji = "📈"
        elif change < -0.1:
            trend = "DETERIORATING"
            trend_emoji = "📉"
        else:
            trend = "STABLE"
            trend_emoji = "➡️"
        
        return {
            "trend": trend,
            "trend_emoji": trend_emoji,
            "change": round(change, 2),
            "first_half_sentiment": round(first_avg, 2),
            "second_half_sentiment": round(second_avg, 2),
            "description": f"{trend_emoji} 情绪 {'改善' if change > 0 else '恶化' if change < 0 else '稳定'}，变化 {abs(change):.2f}"
        }
    
    def categorize_news_sentiment(self, news_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Categorize news sentiment by category
        
        Args:
            news_data: List of news articles
            
        Returns:
            Categorized sentiment analysis
        """
        if not news_data:
            return {}
        
        categories = {}
        
        for news in news_data:
            category = news.get("category", "general")
            sentiment = news.get("sentiment", "neutral")
            
            if category not in categories:
                categories[category] = {
                    "positive": 0,
                    "negative": 0,
                    "neutral": 0,
                    "total": 0
                }
            
            categories[category][sentiment] += 1
            categories[category]["total"] += 1
        
        # Calculate average sentiment for each category
        for category, data in categories.items():
            total = data["total"]
            if total > 0:
                avg_score = (data["positive"] * 0.8 + data["negative"] * 0.2 + data["neutral"] * 0.5) / total
                if avg_score > 0.6:
                    data["overall_sentiment"] = "POSITIVE"
                    data["sentiment_emoji"] = "🟢"
                elif avg_score < 0.4:
                    data["overall_sentiment"] = "NEGATIVE"
                    data["sentiment_emoji"] = "🔴"
                else:
                    data["overall_sentiment"] = "NEUTRAL"
                    data["sentiment_emoji"] = "🟡"
                data["sentiment_score"] = round(avg_score, 2)
        
        return categories
    
    def extract_key_topics(self, news_data: List[Dict[str, Any]]) -> List[str]:
        """
        Extract key topics from news
        
        Args:
            news_data: List of news articles
            
        Returns:
            List of key topics
        """
        from collections import Counter
        
        if not news_data:
            return []
        
        # Stop words to filter out
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by",
            "is", "was", "are", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did",
            "will", "would", "could", "should", "may", "might", "must", "can", "that", "this", "these", "those"
        }
        
        all_words = []
        
        for news in news_data:
            title = news.get("title", "")
            # Simple word extraction
            words = title.lower().split()
            # Filter stop words and short words
            filtered_words = [
                w.strip('.,!?:;') for w in words 
                if w.lower() not in stop_words and len(w) > 3
            ]
            all_words.extend(filtered_words)
        
        # Count word frequency
        if not all_words:
            return []
        
        word_counts = Counter(all_words)
        # Get top 5 topics
        top_topics = [word.capitalize() for word, count in word_counts.most_common(5)]
        
        return top_topics