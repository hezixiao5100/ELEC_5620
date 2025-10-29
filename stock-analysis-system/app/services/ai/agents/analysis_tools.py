"""
Analysis Tools for LangChain Agent
轻量级包装层，调用现有的 Agent 系统来处理分析任务
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
    """投资组合风险分析输入"""
    analysis_depth: str = Field(default="quick", description="分析深度: quick 或 detailed")
    focus_area: str = Field(default="all", description="关注领域: concentration, volatility, sector_exposure, 或 all")


class MarketSentimentInput(BaseModel):
    """市场情绪分析输入"""
    scope: str = Field(default="market", description="分析范围: market, stock, 或 sector")
    symbol: Optional[str] = Field(default=None, description="股票代码（如果分析特定股票）")
    time_range: str = Field(default="today", description="时间范围: today, week, 或 month")


class StockPerformanceInput(BaseModel):
    """股票表现分析输入"""
    symbol: str = Field(..., description="股票代码（例如：AAPL, TSLA, MSFT）")
    analysis_type: str = Field(default="comprehensive", description="分析类型: price_trend, technical_indicators, peer_comparison, 或 comprehensive")
    time_period: str = Field(default="1mo", description="时间周期: 1d, 5d, 1mo(1个月), 3mo(3个月), 6mo, 1y(1年), 2y, 5y, 10y, ytd, max")


class AlertStatusInput(BaseModel):
    """预警状态分析输入"""
    focus: str = Field(default="all", description="关注重点: all, high_risk, 或 near_trigger")


class PortfolioPerformanceInput(BaseModel):
    """投资组合表现分析输入"""
    metric: str = Field(default="overall", description="分析指标: overall, by_stock, profit_loss, 或 ranking")
    time_range: str = Field(default="all_time", description="时间范围: today, week, month, year, 或 all_time")


class MarketTrendInput(BaseModel):
    """市场趋势分析输入"""
    focus: str = Field(default="sectors", description="分析焦点: sectors, market_leaders, emerging_trends, 或 risk_factors")


class StockNewsInput(BaseModel):
    """股票新闻分析输入"""
    symbol: str = Field(..., description="股票代码（例如：AAPL, MSFT, TSLA）")
    days: int = Field(default=7, description="获取最近几天的新闻，默认7天")


class CollectStockDataInput(BaseModel):
    """收集股票数据输入"""
    symbol: str = Field(..., description="股票代码（例如：AAPL, MSFT, TSLA）")
    days: int = Field(default=3, description="收集最近几天的数据，默认3天，最多7天")


class StockRiskInput(BaseModel):
    """单只股票风险分析输入"""
    symbol: str = Field(..., description="股票代码（例如：AAPL, MSFT, TSLA）")
    time_period: str = Field(default="3mo", description="分析时间周期: 1mo, 3mo, 6mo, 1y")


# ==================== Helper Functions ====================

def get_stock_historical_data(db: Session, symbol: str, days: int = 30) -> list:
    """从数据库获取股票历史数据"""
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


# ==================== Tool Functions (调用现有 Agents) ====================

def analyze_portfolio_risk(
    user_id: int,
    analysis_depth: str = "quick",
    focus_area: str = "all"
) -> Dict[str, Any]:
    """
    分析用户投资组合的风险状况（调用现有的 Portfolio 数据）
    """
    try:
        db = SessionLocal()
        
        # 获取用户的所有持仓
        portfolios = db.query(PortfolioModel).filter(
            PortfolioModel.user_id == user_id
        ).all()
        
        if not portfolios:
            db.close()
            return {
                "status": "no_data",
                "message": "您还没有任何持仓",
                "risk_level": "无风险",
                "total_holdings": 0
            }
        
        # 获取股票信息
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
        
        # 计算权重
        for stock in stocks_info:
            stock["weight"] = (stock["current_value"] / total_value * 100) if total_value > 0 else 0
        
        # 计算集中度风险
        max_weight = max([s["weight"] for s in stocks_info]) if stocks_info else 0
        
        # 计算行业分散度
        sectors = {}
        for stock in stocks_info:
            sector = stock["sector"]
            if sector not in sectors:
                sectors[sector] = 0
            sectors[sector] += stock["weight"]
        
        # 风险评估
        if max_weight > 40:
            risk_level = "高风险"
            risk_emoji = "🔴"
        elif max_weight > 25:
            risk_level = "中等风险"
            risk_emoji = "🟡"
        else:
            risk_level = "低风险"
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
                "description": f"最大单只股票占比 {max_weight:.2f}%"
            },
            "sector_distribution": {
                sector: round(weight, 2) for sector, weight in sectors.items()
            },
            "holdings": stocks_info,
            "summary": f"{risk_emoji} 投资组合风险等级: **{risk_level}**，共持有 {len(portfolios)} 只股票，总市值 ${total_value:.2f}"
        }
        
    except Exception as e:
        logger.error(f"Portfolio risk analysis error: {str(e)}")
        return {
            "status": "error",
            "message": f"投资组合风险分析失败: {str(e)}"
        }


def analyze_market_sentiment(
    user_id: int,
    scope: str = "market",
    symbol: Optional[str] = None,
    time_range: str = "today"
) -> Dict[str, Any]:
    """
    分析市场情绪（调用 EmotionalAnalysisAgent）
    """
    try:
        if scope == "stock" and not symbol:
            return {
                "status": "error",
                "message": "分析特定股票情绪时需要提供股票代码"
            }
        
        db = SessionLocal()
        
        # 准备数据
        if symbol:
            stock = db.query(StockModel).filter(StockModel.symbol == symbol.upper()).first()
            if not stock:
                db.close()
                return {
                    "status": "error",
                    "message": f"未找到股票 {symbol}"
                }
            
            # 获取新闻数据
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
        
        # 调用 EmotionalAnalysisAgent
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
            "summary": f"市场情绪分析完成，情绪信号: {result.get('emotional_signal', 'NEUTRAL')}"
        }
        
    except Exception as e:
        logger.error(f"Market sentiment analysis error: {str(e)}")
        return {
            "status": "error",
            "message": f"市场情绪分析失败: {str(e)}"
        }


def analyze_stock_performance(
    user_id: int,
    symbol: str,
    analysis_type: str = "comprehensive",
    time_period: str = "1mo"
) -> Dict[str, Any]:
    """
    分析股票表现（调用 AnalysisAgent）
    """
    try:
        db = SessionLocal()
        
        # 获取股票信息
        stock = db.query(StockModel).filter(StockModel.symbol == symbol.upper()).first()
        if not stock:
            db.close()
            return {
                "status": "error",
                "message": f"未找到股票 {symbol}"
            }
        
        # 获取历史数据
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
                "message": f"没有找到 {symbol} 的历史数据，建议先收集数据"
            }
        
        stock_data = {
            "symbol": symbol.upper(),
            "current_price": stock.current_price or 0,
            "historical_data": historical_data
        }
        
        # 调用 AnalysisAgent
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
        
        # 格式化结果
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
            "summary": f"📊 {symbol} 技术分析完成，交易信号: {result.get('trading_signal', 'HOLD')}"
        }
        
    except Exception as e:
        logger.error(f"Stock performance analysis error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": f"股票表现分析失败: {str(e)}"
        }


def analyze_alert_status(
    user_id: int,
    focus: str = "all"
) -> Dict[str, Any]:
    """
    分析预警状态
    """
    try:
        db = SessionLocal()
        
        # 获取用户的所有预警
        query = db.query(AlertModel).filter(AlertModel.user_id == user_id)
        
        if focus == "high_risk":
            query = query.filter(AlertModel.status == "TRIGGERED")
        elif focus == "near_trigger":
            # 简化：获取 PENDING 状态的预警
            query = query.filter(AlertModel.status == "PENDING")
        
        alerts = query.all()
        
        if not alerts:
            db.close()
            return {
                "status": "no_data",
                "message": "您还没有设置任何预警",
                "total_alerts": 0
            }
        
        # 统计预警状态
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
            "summary": f"共有 {len(alerts)} 个预警，其中 {status_counts.get('TRIGGERED', 0)} 个已触发"
        }
        
    except Exception as e:
        logger.error(f"Alert status analysis error: {str(e)}")
        return {
            "status": "error",
            "message": f"预警状态分析失败: {str(e)}"
        }


def analyze_portfolio_performance(
    user_id: int,
    metric: str = "overall",
    time_range: str = "all_time"
) -> Dict[str, Any]:
    """
    分析投资组合表现
    """
    try:
        db = SessionLocal()
        
        # 获取用户的所有持仓
        portfolios = db.query(PortfolioModel).filter(
            PortfolioModel.user_id == user_id
        ).all()
        
        if not portfolios:
            db.close()
            return {
                "status": "no_data",
                "message": "您还没有任何持仓",
                "total_holdings": 0
            }
        
        # 计算总体表现
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
        
        # 排序（按盈亏百分比）
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
            "summary": f"💰 投资组合总收益: ${total_profit_loss:.2f} ({total_return_pct:+.2f}%)"
        }
        
    except Exception as e:
        logger.error(f"Portfolio performance analysis error: {str(e)}")
        return {
            "status": "error",
            "message": f"投资组合表现分析失败: {str(e)}"
        }


def analyze_market_trend(
    user_id: int,
    focus: str = "sectors"
) -> Dict[str, Any]:
    """
    分析市场趋势（简化版本）
    """
    try:
        db = SessionLocal()
        
        # 获取用户追踪的股票
        tracked_stocks = db.query(TrackedStockModel).filter(
            TrackedStockModel.user_id == user_id,
            TrackedStockModel.is_active == "Y"
        ).all()
        
        if not tracked_stocks:
            db.close()
            return {
                "status": "no_data",
                "message": "您还没有追踪任何股票",
                "total_tracked": 0
            }
        
        # 按行业分组
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
            "summary": f"📈 您追踪的股票覆盖 {len(sectors)} 个行业，共 {len(tracked_stocks)} 只股票"
        }
        
    except Exception as e:
        logger.error(f"Market trend analysis error: {str(e)}")
        return {
            "status": "error",
            "message": f"市场趋势分析失败: {str(e)}"
        }


def analyze_stock_news(
    user_id: int,
    symbol: str,
    days: int = 7
) -> Dict[str, Any]:
    """
    获取并分析股票的最近新闻
    """
    try:
        db = SessionLocal()
        stock = db.query(StockModel).filter(StockModel.symbol == symbol.upper()).first()
        if not stock:
            db.close()
            return {"status": "error", "message": f"未找到股票 {symbol}"}
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        news_items = db.query(NewsModel).filter(
            NewsModel.stock_id == stock.id,
            NewsModel.published_at >= cutoff_date
        ).order_by(NewsModel.published_at.desc()).limit(20).all()
        
        if not news_items:
            db.close()
            return {
                "status": "no_data",
                "message": f"最近 {days} 天内没有找到 {symbol} 的新闻",
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
            sentiment_label = "积极"
            sentiment_emoji = "🟢"
        elif avg_sentiment < -0.3:
            sentiment_label = "消极"
            sentiment_emoji = "🔴"
        else:
            sentiment_label = "中性"
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
                "description": f"基于 {len(sentiment_scores)} 条新闻的情绪评分"
            },
            "categories": categories,
            "news_list": news_list,
            "summary": f"{sentiment_emoji} 最近 {days} 天内有 {len(news_items)} 条关于 {symbol} 的新闻，整体情绪{sentiment_label}（{avg_sentiment:.2f}）"
        }
        db.close()
        return result
    except Exception as e:
        logger.error(f"Stock news analysis error: {str(e)}")
        return {"status": "error", "message": f"分析股票新闻时出现错误: {str(e)}"}


def collect_stock_data(
    user_id: int,
    symbol: str,
    days: int = 3
) -> Dict[str, Any]:
    """
    触发数据收集代理（调用 DataCollectionAgent）
    """
    try:
        days = min(days, 7)  # 限制最多7天
        
        db = SessionLocal()
        
        # 创建数据收集代理
        agent = DataCollectionAgent(db=db)
        
        logger.info(f"🚀 Starting data collection for {symbol}")
        
        # 使用 asyncio 运行异步任务
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(agent.execute_task({"symbol": symbol}))
        finally:
            loop.close()
            db.close()
        
        # 解析结果
        if result and result.get("data_quality") == "valid":
            stock_data = result.get("stock_data", {})
            news_data = result.get("news_data", [])
            
            return {
                "status": "success",
                "symbol": symbol,
                "message": f"✅ 成功收集 {symbol} 的最新数据",
                "data_collected": {
                    "current_price": stock_data.get("current_price"),
                    "price_change_24h": stock_data.get("price_change_24h"),
                    "volume": stock_data.get("volume"),
                    "news_articles": len(news_data),
                    "historical_data_points": len(stock_data.get("historical_data", []))
                },
                "summary": f"收集了价格数据（当前价: ${stock_data.get('current_price', 0):.2f}）和 {len(news_data)} 条新闻",
                "stored_in_db": result.get("stored_in_db", False)
            }
        else:
            return {
                "status": "partial",
                "symbol": symbol,
                "message": f"⚠️ 数据收集完成但质量可能不完整",
                "data_collected": result
            }
        
    except Exception as e:
        logger.error(f"Data collection error for {symbol}: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "symbol": symbol,
            "message": f"数据收集失败: {str(e)}"
        }


def analyze_stock_risk(
    user_id: int,
    symbol: str,
    time_period: str = "3mo"
) -> Dict[str, Any]:
    """
    分析单只股票的风险状况（调用 RiskAnalysisAgent）
    """
    try:
        db = SessionLocal()
        
        # 获取股票信息
        stock = db.query(StockModel).filter(StockModel.symbol == symbol.upper()).first()
        if not stock:
            db.close()
            return {
                "status": "error",
                "message": f"未找到股票 {symbol}"
            }
        
        # 获取历史数据
        period_days_map = {"1mo": 30, "3mo": 90, "6mo": 180, "1y": 365}
        days = period_days_map.get(time_period, 90)
        historical_data = get_stock_historical_data(db, symbol, days)
        
        if not historical_data:
            db.close()
            return {
                "status": "no_data",
                "message": f"没有找到 {symbol} 的历史数据，建议先收集数据"
            }
        
        stock_data = {
            "symbol": symbol.upper(),
            "current_price": stock.current_price or 0,
            "historical_data": historical_data
        }
        
        # 调用 RiskAnalysisAgent
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
        
        # 检查用户是否持有该股票
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
            "summary": f"🔍 {symbol} 风险分析完成，风险等级: {result.get('risk_level', 'Unknown')}"
        }
        
    except Exception as e:
        logger.error(f"Stock risk analysis error for {symbol}: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "symbol": symbol,
            "message": f"股票风险分析失败: {str(e)}"
        }
