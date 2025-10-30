"""
Analysis Tools for LangChain Agent
Lightweight wrapper layer that calls existing Agent system to handle analysis tasks
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.portfolio import Portfolio as PortfolioModel
from app.models.alert import Alert as AlertModel
from app.models.tracked_stock import TrackedStock as TrackedStockModel
from app.models.stock import Stock as StockModel
from app.models.news import News as NewsModel
from app.models.stock_data import StockData as StockDataModel
import logging
from datetime import datetime, timedelta
import asyncio

# Import existing agents
from app.agents.data_collection_agent import DataCollectionAgent
from app.agents.analysis_agent import AnalysisAgent
from app.agents.risk_analysis_agent import RiskAnalysisAgent
from app.agents.emotional_analysis_agent import EmotionalAnalysisAgent

logger = logging.getLogger(__name__)


# ==================== Tool Input Schemas ====================

class PortfolioRiskInput(BaseModel):
    """Portfolio risk analysis input"""
    analysis_depth: str = Field(default="quick", description="Analysis depth: quick or detailed")
    focus_area: str = Field(default="all", description="Focus area: concentration, volatility, sector_exposure, or all")


class MarketSentimentInput(BaseModel):
    """Market sentiment analysis input"""
    scope: str = Field(default="market", description="Analysis scope: market, stock, or sector")
    symbol: Optional[str] = Field(default=None, description="Stock symbol (if analyzing specific stock)")
    time_range: str = Field(default="today", description="Time range: today, week, or month")


class StockPerformanceInput(BaseModel):
    """Stock performance analysis input"""
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL, TSLA, MSFT)")
    analysis_type: str = Field(default="comprehensive", description="Analysis type: price_trend, technical_indicators, peer_comparison, or comprehensive")
    time_period: str = Field(default="1mo", description="Time period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max")


class AlertStatusInput(BaseModel):
    """Alert status analysis input"""
    focus: str = Field(default="all", description="Focus area: all, high_risk, or near_trigger")


class PortfolioPerformanceInput(BaseModel):
    """Portfolio performance analysis input"""
    metric: str = Field(default="overall", description="Analysis metric: overall, by_stock, profit_loss, or ranking")
    time_range: str = Field(default="all_time", description="Time range: today, week, month, year, or all_time")


class MarketTrendInput(BaseModel):
    """Market trend analysis input"""
    focus: str = Field(default="sectors", description="Analysis focus: sectors, market_leaders, emerging_trends, or risk_factors")


class StockNewsInput(BaseModel):
    """Stock news analysis input"""
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL, MSFT, TSLA)")
    days: int = Field(default=7, description="Get news for recent days, default 7 days")


class CollectStockDataInput(BaseModel):
    """Collect stock data input"""
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL, MSFT, TSLA)")
    days: int = Field(default=3, description="Collect data for recent days, default 3 days, max 7 days")


class StockRiskInput(BaseModel):
    """Individual stock risk analysis input"""
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL, MSFT, TSLA)")
    time_period: str = Field(default="3mo", description="Analysis time period: 1mo, 3mo, 6mo, 1y")


# ==================== Helper Functions ====================

def get_stock_historical_data(db: Session, symbol: str, days: int = 30) -> list:
    """Get stock historical data from database"""
    try:
        stock = db.query(StockModel).filter(StockModel.symbol == symbol.upper()).first()
        if not stock:
            return []
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        stock_data = db.query(StockDataModel).filter(
            StockDataModel.stock_id == stock.id,
            StockDataModel.date >= cutoff_date
        ).order_by(StockDataModel.date.asc()).all()
        
        return [
            {
                "date": sd.date.strftime("%Y-%m-%d"),
                "open": float(sd.open_price) if sd.open_price else 0,
                "high": float(sd.high_price) if sd.high_price else 0,
                "low": float(sd.low_price) if sd.low_price else 0,
                "close": float(sd.close_price) if sd.close_price else 0,
                "volume": int(sd.volume) if sd.volume else 0
            }
            for sd in stock_data
        ]
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
        return []


# ==================== Tool Functions (call existing Agents) ====================

def analyze_portfolio_risk(
    user_id: int,
    analysis_depth: str = "quick",
    focus_area: str = "all"
) -> Dict[str, Any]:
    """
    Analyze user portfolio risk (using existing Portfolio data)
    """
    try:
        db = SessionLocal()
        
        # Get all user holdings
        portfolios = db.query(PortfolioModel).filter(
            PortfolioModel.user_id == user_id
        ).all()
        
        if not portfolios:
            db.close()
            return {
                "status": "no_data",
                "message": "You don't have any holdings yet",
                "risk_level": "NO_RISK",
                "total_holdings": 0
            }
        
        # Get stock info
        stocks_info = []
        total_value = 0
        
        for p in portfolios:
            stock = db.query(StockModel).filter(StockModel.id == p.stock_id).first()
            if stock:
                current_price = stock.current_price or 0
                current_value = p.calculate_current_value(current_price)
                total_value += current_value
                
                stocks_info.append({
                    "symbol": stock.symbol,
                    "name": stock.name,
                    "sector": stock.sector or "Unknown",
                    "industry": stock.industry or "Unknown",
                    "quantity": p.quantity,
                    "purchase_price": p.purchase_price,
                    "current_price": current_price,
                    "current_value": current_value,
                    "weight": 0  # Will calculate after
                })
        
        # Compute weights
        for stock in stocks_info:
            stock["weight"] = (stock["current_value"] / total_value * 100) if total_value > 0 else 0
        
        # Concentration risk
        max_weight = max([s["weight"] for s in stocks_info]) if stocks_info else 0
        
        # Sector diversification
        sectors = {}
        for stock in stocks_info:
            sector = stock["sector"]
            if sector not in sectors:
                sectors[sector] = 0
            sectors[sector] += stock["weight"]
        
        # Risk assessment
        if max_weight > 40:
            risk_level = "HIGH"
            risk_emoji = "🔴"
        elif max_weight > 25:
            risk_level = "MEDIUM"
            risk_emoji = "🟡"
        else:
            risk_level = "LOW"
            risk_emoji = "🟢"
        
        db.close()
        
        return {
            "status": "success",
            "risk_level": risk_level,
            "risk_emoji": risk_emoji,
            "total_holdings": len(portfolios),
            "total_value": round(total_value, 2),
            "concentration_risk": {
                "max_weight": round(max_weight, 2),
                "description": f"Max single-stock weight {max_weight:.2f}%"
            },
            "sector_distribution": {
                sector: round(weight, 2) for sector, weight in sectors.items()
            },
            "holdings": stocks_info,
            "summary": f"{risk_emoji} Portfolio risk level: **{risk_level}** with {len(portfolios)} holdings, total value ${total_value:.2f}"
        }
        
    except Exception as e:
        logger.error(f"Portfolio risk analysis error: {str(e)}")
        return {
            "status": "error",
            "message": f"Portfolio risk analysis failed: {str(e)}"
        }


def analyze_market_sentiment(
    user_id: int,
    scope: str = "market",
    symbol: Optional[str] = None,
    time_range: str = "today"
) -> Dict[str, Any]:
    """
    Analyze market sentiment (calls EmotionalAnalysisAgent)
    """
    try:
        if scope == "stock" and not symbol:
            return {
                "status": "error",
                "message": "Stock symbol is required when analyzing a specific stock's sentiment"
            }
        
        db = SessionLocal()
        
        # Prepare data
        if symbol:
            stock = db.query(StockModel).filter(StockModel.symbol == symbol.upper()).first()
            if not stock:
                db.close()
                return {
                    "status": "error",
                    "message": f"Stock {symbol} not found"
                }
            
            # Fetch news data
            days_map = {"today": 1, "week": 7, "month": 30}
            days = days_map.get(time_range, 7)
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            news_items = db.query(NewsModel).filter(
                NewsModel.stock_id == stock.id,
                NewsModel.published_at >= cutoff_date
            ).order_by(NewsModel.published_at.desc()).all()
            
            news_data = [
                {
                    "title": n.title,
                    "content": n.content or "",
                    "sentiment": "positive" if n.sentiment_score and n.sentiment_score > 0.3 else ("negative" if n.sentiment_score and n.sentiment_score < -0.3 else "neutral"),
                    "published_at": n.published_at.isoformat()
                }
                for n in news_items
            ]
            
            stock_data = {
                "symbol": stock.symbol,
                "current_price": stock.current_price or 0,
                "price_change_percent": 0  # Simplified
            }
        else:
            news_data = []
            stock_data = {}
        
        # Call EmotionalAnalysisAgent
        agent = EmotionalAnalysisAgent()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(agent.execute_task({
                "news_data": news_data,
                "stock_data": stock_data
            }))
        finally:
            loop.close()
            db.close()
        
        return {
            "status": "success",
            "scope": scope,
            "symbol": symbol,
            "time_range": time_range,
            "sentiment": result.get("news_sentiment", {}),
            "market_sentiment": result.get("market_sentiment", {}),
            "fear_greed_index": result.get("fear_greed_index", {}),
            "summary": f"Market sentiment analysis completed. Signal: {result.get('emotional_signal', 'NEUTRAL')}"
        }
        
    except Exception as e:
        logger.error(f"Market sentiment analysis error: {str(e)}")
        return {
            "status": "error",
            "message": f"Market sentiment analysis failed: {str(e)}"
        }


def analyze_stock_performance(
    user_id: int,
    symbol: str,
    analysis_type: str = "comprehensive",
    time_period: str = "1mo"
) -> Dict[str, Any]:
    """
    Analyze stock performance (calls AnalysisAgent)
    """
    try:
        db = SessionLocal()
        
        # Get stock info
        stock = db.query(StockModel).filter(StockModel.symbol == symbol.upper()).first()
        if not stock:
            db.close()
            return {
                "status": "error",
                "message": f"Stock {symbol} not found"
            }
        
        # Get historical data
        period_days_map = {
            "1d": 1, "5d": 5, "1mo": 30, "3mo": 90,
            "6mo": 180, "1y": 365, "2y": 730, "5y": 1825
        }
        days = period_days_map.get(time_period, 30)
        historical_data = get_stock_historical_data(db, symbol, days)
        
        if not historical_data:
            db.close()
            return {
                "status": "no_data",
                "message": f"No historical data found for {symbol}. Consider collecting data first"
            }
        
        stock_data = {
            "symbol": symbol.upper(),
            "current_price": stock.current_price or 0,
            "historical_data": historical_data
        }
        
        # Call AnalysisAgent
        agent = AnalysisAgent()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(agent.execute_task({
                "stock_data": stock_data
            }))
        finally:
            loop.close()
            db.close()
        
        # Format result
        technical = result.get("technical_analysis", {})
        
        return {
            "status": "success",
            "symbol": symbol.upper(),
            "stock_name": stock.name,
            "time_period": time_period,
            "current_price": stock.current_price or 0,
            "technical_analysis": technical,
            "trading_signal": result.get("trading_signal", "HOLD"),
            "confidence_score": result.get("confidence_score", 0),
            "summary": f"📊 {symbol} technical analysis complete. Signal: {result.get('trading_signal', 'HOLD')}"
        }
        
    except Exception as e:
        logger.error(f"Stock performance analysis error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": f"Stock performance analysis failed: {str(e)}"
        }


def analyze_alert_status(
    user_id: int,
    focus: str = "all"
) -> Dict[str, Any]:
    """
    Analyze alert status
    """
    try:
        db = SessionLocal()
        
        # Get all user alerts
        query = db.query(AlertModel).filter(AlertModel.user_id == user_id)
        
        if focus == "high_risk":
            query = query.filter(AlertModel.status == "TRIGGERED")
        elif focus == "near_trigger":
            # Simplified: get PENDING alerts
            query = query.filter(AlertModel.status == "PENDING")
        
        alerts = query.all()
        
        if not alerts:
            db.close()
            return {
                "status": "no_data",
                "message": "You have not set any alerts yet",
                "total_alerts": 0
            }
        
        # Aggregate alert status
        status_counts = {}
        alert_list = []
        
        for alert in alerts:
            status = alert.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            
            stock = db.query(StockModel).filter(StockModel.id == alert.stock_id).first()
            
            alert_list.append({
                "id": alert.id,
                "symbol": stock.symbol if stock else "Unknown",
                "stock_name": stock.name if stock else "Unknown",
                "alert_type": alert.alert_type.value,
                "threshold": alert.threshold_value,
                "current_value": alert.current_value,
                "status": status,
                "trigger_count": alert.trigger_count,
                "message": alert.message
            })
        
        db.close()
        
        return {
            "status": "success",
            "total_alerts": len(alerts),
            "status_counts": status_counts,
            "alerts": alert_list,
            "summary": f"There are {len(alerts)} alerts, {status_counts.get('TRIGGERED', 0)} triggered"
        }
        
    except Exception as e:
        logger.error(f"Alert status analysis error: {str(e)}")
        return {
            "status": "error",
            "message": f"Alert status analysis failed: {str(e)}"
        }


def analyze_portfolio_performance(
    user_id: int,
    metric: str = "overall",
    time_range: str = "all_time"
) -> Dict[str, Any]:
    """
    Analyze portfolio performance
    """
    try:
        db = SessionLocal()
        
        # Get all user holdings
        portfolios = db.query(PortfolioModel).filter(
            PortfolioModel.user_id == user_id
        ).all()
        
        if not portfolios:
            db.close()
            return {
                "status": "no_data",
                "message": "You don't have any holdings yet",
                "total_holdings": 0
            }
        
        # Compute overall performance
        total_cost = 0
        total_value = 0
        holdings = []
        
        for p in portfolios:
            stock = db.query(StockModel).filter(StockModel.id == p.stock_id).first()
            if stock:
                current_price = stock.current_price or 0
                cost_basis = p.calculate_cost_basis()
                current_value = p.calculate_current_value(current_price)
                profit_loss = p.calculate_profit_loss(current_price)
                profit_loss_pct = p.calculate_profit_loss_pct(current_price)
                
                total_cost += cost_basis
                total_value += current_value
                
                holdings.append({
                    "symbol": stock.symbol,
                    "name": stock.name,
                    "quantity": p.quantity,
                    "purchase_price": p.purchase_price,
                    "current_price": current_price,
                    "cost_basis": cost_basis,
                    "current_value": current_value,
                    "profit_loss": profit_loss,
                    "profit_loss_pct": profit_loss_pct
                })
        
        total_profit_loss = total_value - total_cost
        total_return_pct = (total_profit_loss / total_cost * 100) if total_cost > 0 else 0
        
        # Sort by profit/loss percentage
        holdings_sorted = sorted(holdings, key=lambda x: x["profit_loss_pct"], reverse=True)
        
        db.close()
        
        return {
            "status": "success",
            "metric": metric,
            "time_range": time_range,
            "total_cost": round(total_cost, 2),
            "total_value": round(total_value, 2),
            "total_profit_loss": round(total_profit_loss, 2),
            "total_return_pct": round(total_return_pct, 2),
            "holdings": holdings_sorted,
            "summary": f"💰 Portfolio total P/L: ${total_profit_loss:.2f} ({total_return_pct:+.2f}%)"
        }
        
    except Exception as e:
        logger.error(f"Portfolio performance analysis error: {str(e)}")
        return {
            "status": "error",
            "message": f"Portfolio performance analysis failed: {str(e)}"
        }


def analyze_market_trend(
    user_id: int,
    focus: str = "sectors"
) -> Dict[str, Any]:
    """
    Analyze market trends (simplified)
    """
    try:
        db = SessionLocal()
        
        # Get user-tracked stocks
        tracked_stocks = db.query(TrackedStockModel).filter(
            TrackedStockModel.user_id == user_id,
            TrackedStockModel.is_active == "Y"
        ).all()
        
        if not tracked_stocks:
            db.close()
            return {
                "status": "no_data",
                "message": "You are not tracking any stocks yet",
                "total_tracked": 0
            }
        
        # Group by sector
        sectors = {}
        for ts in tracked_stocks:
            stock = db.query(StockModel).filter(StockModel.id == ts.stock_id).first()
            if stock:
                sector = stock.sector or "Unknown"
                if sector not in sectors:
                    sectors[sector] = []
                sectors[sector].append({
                    "symbol": stock.symbol,
                    "name": stock.name,
                    "current_price": stock.current_price or 0
                })
        
        db.close()
        
        return {
            "status": "success",
            "focus": focus,
            "sectors": sectors,
            "sector_count": len(sectors),
            "total_tracked": len(tracked_stocks),
            "summary": f"📈 Your tracked stocks span {len(sectors)} sectors, total {len(tracked_stocks)} stocks"
        }
        
    except Exception as e:
        logger.error(f"Market trend analysis error: {str(e)}")
        return {
            "status": "error",
            "message": f"Market trend analysis failed: {str(e)}"
        }


def analyze_stock_news(
    user_id: int,
    symbol: str,
    days: int = 7
) -> Dict[str, Any]:
    """
    Get and analyze recent news for a stock
    """
    try:
        db = SessionLocal()
        stock = db.query(StockModel).filter(StockModel.symbol == symbol.upper()).first()
        if not stock:
            db.close()
            return {"status": "error", "message": f"Stock {symbol} not found"}
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        news_items = db.query(NewsModel).filter(
            NewsModel.stock_id == stock.id,
            NewsModel.published_at >= cutoff_date
        ).order_by(NewsModel.published_at.desc()).limit(20).all()
        
        if not news_items:
            db.close()
            return {
                "status": "no_data",
                "message": f"No news found for {symbol} in the last {days} days",
                "symbol": symbol,
                "news_count": 0
            }
        
        sentiment_scores = [n.sentiment_score for n in news_items if n.sentiment_score is not None]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        
        categories = {}
        for news in news_items:
            cat = news.category or "general"
            categories[cat] = categories.get(cat, 0) + 1
        
        if avg_sentiment > 0.3:
            sentiment_label = "POSITIVE"
            sentiment_emoji = "🟢"
        elif avg_sentiment < -0.3:
            sentiment_label = "NEGATIVE"
            sentiment_emoji = "🔴"
        else:
            sentiment_label = "NEUTRAL"
            sentiment_emoji = "🟡"
        
        news_list = []
        for news in news_items[:10]:
            news_list.append({
                "title": news.title,
                "source": news.source,
                "published_at": news.published_at.strftime("%Y-%m-%d %H:%M"),
                "sentiment_score": news.sentiment_score,
                "url": news.url,
                "category": news.category
            })
        
        result = {
            "status": "success",
            "symbol": symbol,
            "stock_name": stock.name,
            "days": days,
            "news_count": len(news_items),
            "sentiment": {
                "average_score": round(avg_sentiment, 2),
                "label": sentiment_label,
                "emoji": sentiment_emoji,
                "description": f"Sentiment score based on {len(sentiment_scores)} news items"
            },
            "categories": categories,
            "news_list": news_list,
            "summary": f"{sentiment_emoji} There were {len(news_items)} news items about {symbol} in the last {days} days, overall sentiment {sentiment_label} ({avg_sentiment:.2f})"
        }
        db.close()
        return result
    except Exception as e:
        logger.error(f"Stock news analysis error: {str(e)}")
        return {"status": "error", "message": f"Error analyzing stock news: {str(e)}"}


def collect_stock_data(
    user_id: int,
    symbol: str,
    days: int = 3
) -> Dict[str, Any]:
    """
    Trigger data collection agent (calls DataCollectionAgent)
    """
    try:
        days = min(days, 7)  # limit to 7 days max
        
        db = SessionLocal()
        
        # Create data collection agent
        agent = DataCollectionAgent(db=db)
        
        logger.info(f"🚀 Starting data collection for {symbol}")
        
        # Run async task using asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(agent.execute_task({"symbol": symbol}))
        finally:
            loop.close()
            db.close()
        
        # Parse result
        if result and result.get("data_quality") == "valid":
            stock_data = result.get("stock_data", {})
            news_data = result.get("news_data", [])
            
            return {
                "status": "success",
                "symbol": symbol,
                "message": f"✅ Successfully collected latest data for {symbol}",
                "data_collected": {
                    "current_price": stock_data.get("current_price"),
                    "price_change_24h": stock_data.get("price_change_24h"),
                    "volume": stock_data.get("volume"),
                    "news_articles": len(news_data),
                    "historical_data_points": len(stock_data.get("historical_data", []))
                },
                "summary": f"Collected price data (current: ${stock_data.get('current_price', 0):.2f}) and {len(news_data)} news articles",
                "stored_in_db": result.get("stored_in_db", False)
            }
        else:
            return {
                "status": "partial",
                "symbol": symbol,
                "message": f"⚠️ Data collection completed but quality may be incomplete",
                "data_collected": result
            }
        
    except Exception as e:
        logger.error(f"Data collection error for {symbol}: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "symbol": symbol,
            "message": f"Data collection failed: {str(e)}"
        }


def analyze_stock_risk(
    user_id: int,
    symbol: str,
    time_period: str = "3mo"
) -> Dict[str, Any]:
    """
    Analyze an individual stock's risk (calls RiskAnalysisAgent)
    """
    try:
        db = SessionLocal()
        
        # Get stock info
        stock = db.query(StockModel).filter(StockModel.symbol == symbol.upper()).first()
        if not stock:
            db.close()
            return {
                "status": "error",
                "message": f"Stock {symbol} not found"
            }
        
        # Get historical data
        period_days_map = {"1mo": 30, "3mo": 90, "6mo": 180, "1y": 365}
        days = period_days_map.get(time_period, 90)
        historical_data = get_stock_historical_data(db, symbol, days)
        
        if not historical_data:
            db.close()
            return {
                "status": "no_data",
                "message": f"No historical data found for {symbol}. Consider collecting data first"
            }
        
        stock_data = {
            "symbol": symbol.upper(),
            "current_price": stock.current_price or 0,
            "historical_data": historical_data
        }
        
        # Call RiskAnalysisAgent
        agent = RiskAnalysisAgent()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(agent.execute_task({
                "stock_data": stock_data,
                "market_data": {}
            }))
        finally:
            loop.close()
        
        # Check whether user holds this stock
        portfolio = db.query(PortfolioModel).filter(
            PortfolioModel.user_id == user_id,
            PortfolioModel.stock_id == stock.id
        ).first()
        
        portfolio_context = None
        if portfolio:
            current_price = stock.current_price or 0
            portfolio_context = {
                "quantity": portfolio.quantity,
                "purchase_price": portfolio.purchase_price,
                "current_value": portfolio.calculate_current_value(current_price),
                "profit_loss": portfolio.calculate_profit_loss(current_price),
                "profit_loss_pct": portfolio.calculate_profit_loss_pct(current_price)
            }
        
        db.close()
        
        return {
            "status": "success",
            "symbol": symbol.upper(),
            "stock_name": stock.name,
            "time_period": time_period,
            "risk_analysis": result,
            "portfolio_context": portfolio_context,
            "summary": f"🔍 {symbol} risk analysis completed. Risk level: {result.get('risk_level', 'Unknown')}"
        }
        
    except Exception as e:
        logger.error(f"Stock risk analysis error for {symbol}: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "symbol": symbol,
            "message": f"Stock risk analysis failed: {str(e)}"
        }
