"""
Stock Service
Business logic for stock operations
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
import logging

from app.agents.agent_manager import AgentManager
from app.schemas.stock import Stock, StockCreate, StockData, TrackStockRequest, TrackedStock
from app.models.stock import Stock as StockModel
from app.models.tracked_stock import TrackedStock as TrackedStockModel
from app.models.stock_data import StockData as StockDataModel
from app.models.user import User as UserModel
from app.external.stock_api_client import StockAPIClient

class StockService:
    """
    Service for stock-related operations
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.agent_manager = AgentManager(db)
        self.stock_api_client = StockAPIClient()
        self.logger = logging.getLogger("stock_service")
    
    def add_stock(self, symbol: str, name: str, sector: str = None, industry: str = None, 
                  market_cap: float = None, current_price: float = None, 
                  currency: str = "USD", exchange: str = None) -> StockModel:
        """
        Add a new stock to the database
        
        Args:
            symbol: Stock symbol
            name: Company name
            sector: Business sector
            industry: Industry
            market_cap: Market capitalization
            current_price: Current stock price
            currency: Currency code
            exchange: Stock exchange
            
        Returns:
            Created stock model
        """
        # Check if stock already exists
        existing_stock = self.db.query(StockModel).filter(StockModel.symbol == symbol.upper()).first()
        if existing_stock:
            raise ValueError(f"Stock {symbol} already exists")
        
        # Create new stock
        stock = StockModel(
            symbol=symbol.upper(),
            name=name,
            sector=sector,
            industry=industry,
            market_cap=market_cap,
            current_price=current_price,
            currency=currency,
            exchange=exchange,
            is_active=True
        )
        
        self.db.add(stock)
        self.db.commit()
        self.db.refresh(stock)
        
        self.logger.info(f"Added new stock: {symbol} - {name}")
        return stock
    
    def get_stock(self, stock_id: int) -> Optional[StockModel]:
        """
        Get stock by ID
        
        Args:
            stock_id: Stock ID
            
        Returns:
            Stock model or None
        """
        return self.db.query(StockModel).filter(StockModel.id == stock_id).first()
    
    def get_stock_by_symbol_sync(self, symbol: str) -> Optional[StockModel]:
        """
        Get stock by symbol (synchronous version)
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Stock model or None
        """
        return self.db.query(StockModel).filter(StockModel.symbol == symbol.upper()).first()
    
    def update_stock(self, stock_id: int, **kwargs) -> Optional[StockModel]:
        """
        Update stock information
        
        Args:
            stock_id: Stock ID
            **kwargs: Fields to update
            
        Returns:
            Updated stock model or None
        """
        stock = self.get_stock(stock_id)
        if not stock:
            return None
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(stock, key):
                setattr(stock, key, value)
        
        stock.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(stock)
        
        self.logger.info(f"Updated stock: {stock.symbol}")
        return stock
    
    def delete_stock(self, stock_id: int) -> bool:
        """
        Delete stock (soft delete)
        
        Args:
            stock_id: Stock ID
            
        Returns:
            True if deleted, False if not found
        """
        stock = self.get_stock(stock_id)
        if not stock:
            return False
        
        # Soft delete
        stock.is_active = False
        stock.updated_at = datetime.utcnow()
        self.db.commit()
        
        self.logger.info(f"Deleted stock: {stock.symbol}")
        return True
    
    def list_stocks(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[StockModel]:
        """
        List stocks with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            active_only: Only return active stocks
            
        Returns:
            List of stock models
        """
        query = self.db.query(StockModel)
        
        if active_only:
            query = query.filter(StockModel.is_active == True)
        
        return query.offset(skip).limit(limit).all()
    
    def search_stocks_by_name(self, name: str, limit: int = 10) -> List[StockModel]:
        """
        Search stocks by name
        
        Args:
            name: Name to search for
            limit: Maximum number of results
            
        Returns:
            List of matching stocks
        """
        return self.db.query(StockModel).filter(
            and_(
                StockModel.is_active == True,
                StockModel.name.ilike(f"%{name}%")
            )
        ).limit(limit).all()
    
    def search_stocks_by_sector(self, sector: str, limit: int = 10) -> List[StockModel]:
        """
        Search stocks by sector
        
        Args:
            sector: Sector to search for
            limit: Maximum number of results
            
        Returns:
            List of matching stocks
        """
        return self.db.query(StockModel).filter(
            and_(
                StockModel.is_active == True,
                StockModel.sector.ilike(f"%{sector}%")
            )
        ).limit(limit).all()
    
    async def track_stock(self, symbol: str, user_id: int, custom_alert_threshold: Optional[float] = None) -> Dict[str, Any]:
        """
        Track a stock for a user
        
        Args:
            symbol: Stock symbol to track
            user_id: User ID
            custom_alert_threshold: Custom alert threshold
            
        Returns:
            Tracking result
        """
        try:
            # Check if stock exists in database
            stock = self.db.query(StockModel).filter(StockModel.symbol == symbol.upper()).first()
            
            if not stock:
                # Get stock info from API and create in database
                stock_data = await self.stock_api_client.get_current_price(symbol)
                if "error" in stock_data:
                    raise ValueError(f"Stock {symbol} not found: {stock_data['error']}")
                
                # Create new stock record
                stock = StockModel(
                    symbol=symbol.upper(),
                    name=stock_data.get("name", f"{symbol} Company"),
                    current_price=stock_data.get("price", 0),
                    currency=stock_data.get("currency", "USD"),
                    exchange=stock_data.get("exchange", "NASDAQ"),
                    market_cap=stock_data.get("market_cap", 0),
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                self.db.add(stock)
                self.db.commit()
                self.db.refresh(stock)
            
            # Check if user is already tracking this stock
            existing_track = self.db.query(TrackedStockModel).filter(
                and_(
                    TrackedStockModel.user_id == user_id,
                    TrackedStockModel.stock_id == stock.id
                )
            ).first()
            
            if existing_track:
                if existing_track.is_active:
                    raise ValueError(f"Stock {symbol} is already being tracked")
                else:
                    # Reactivate tracking
                    existing_track.is_active = True
                    existing_track.custom_alert_threshold = custom_alert_threshold
                    existing_track.updated_at = datetime.utcnow()
            else:
                # Create new tracking record
                tracked_stock = TrackedStockModel(
                    user_id=user_id,
                    stock_id=stock.id,
                    custom_alert_threshold=custom_alert_threshold,
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                self.db.add(tracked_stock)
            
            self.db.commit()
            
            return {
                "symbol": symbol,
                "stock_id": stock.id,
                "custom_alert_threshold": custom_alert_threshold,
                "tracked_at": datetime.utcnow().isoformat(),
                "status": "tracking"
            }
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Failed to track stock {symbol}: {str(e)}")
            raise Exception(f"Failed to track stock: {str(e)}")
    
    async def untrack_stock(self, symbol: str, user_id: int) -> None:
        """
        Stop tracking a stock
        
        Args:
            symbol: Stock symbol to untrack
            user_id: User ID
        """
        try:
            # Find the stock
            stock = self.db.query(StockModel).filter(StockModel.symbol == symbol.upper()).first()
            if not stock:
                raise ValueError(f"Stock {symbol} not found")
            
            # Find the tracking record
            tracked_stock = self.db.query(TrackedStockModel).filter(
                and_(
                    TrackedStockModel.user_id == user_id,
                    TrackedStockModel.stock_id == stock.id
                )
            ).first()
            
            if not tracked_stock:
                raise ValueError(f"Stock {symbol} is not being tracked")
            
            # Deactivate tracking
            tracked_stock.is_active = False
            tracked_stock.updated_at = datetime.utcnow()
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Failed to untrack stock {symbol}: {str(e)}")
            raise Exception(f"Failed to untrack stock: {str(e)}")
    
    async def get_tracked_stocks(self, user_id: int) -> List[TrackedStock]:
        """
        Get all tracked stocks for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List of tracked stocks
        """
        try:
            # Query tracked stocks with stock information
            tracked_stocks = self.db.query(TrackedStockModel).join(StockModel).filter(
                and_(
                    TrackedStockModel.user_id == user_id,
                    TrackedStockModel.is_active == True
                )
            ).all()
            
            result = []
            for tracked in tracked_stocks:
                result.append(TrackedStock(
                    id=tracked.id,
                    user_id=tracked.user_id,
                    stock_id=tracked.stock_id,
                    custom_alert_threshold=tracked.custom_alert_threshold,
                    is_active=tracked.is_active,
                    created_at=tracked.created_at.isoformat(),
                    updated_at=tracked.updated_at.isoformat()
                ))
            
            return result
        except Exception as e:
            self.logger.error(f"Failed to get tracked stocks for user {user_id}: {str(e)}")
            raise Exception(f"Failed to get tracked stocks: {str(e)}")
    
    async def get_stock_by_symbol(self, symbol: str) -> Optional[Stock]:
        """
        Get stock information by symbol
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Stock information
        """
        try:
            # Check database first
            stock = self.db.query(StockModel).filter(StockModel.symbol == symbol.upper()).first()
            
            if stock:
                # Update price from API if data is older than 1 hour
                if (datetime.utcnow() - stock.updated_at).seconds > 3600:
                    try:
                        current_data = await self.stock_api_client.get_current_price(symbol)
                        if "error" not in current_data:
                            stock.current_price = current_data.get("price", stock.current_price)
                            stock.updated_at = datetime.utcnow()
                            self.db.commit()
                    except Exception as e:
                        self.logger.warning(f"Failed to update price for {symbol}: {str(e)}")
                
                return Stock(
                    id=stock.id,
                    symbol=stock.symbol,
                    name=stock.name,
                    sector=stock.sector,
                    industry=stock.industry,
                    market_cap=stock.market_cap,
                    current_price=stock.current_price,
                    currency=stock.currency,
                    exchange=stock.exchange,
                    is_active=stock.is_active,
                    created_at=stock.created_at.isoformat(),
                    updated_at=stock.updated_at.isoformat()
                )
            else:
                # Get from API and create in database
                stock_data = await self.stock_api_client.get_current_price(symbol)
                if "error" in stock_data:
                    return None
                
                # Create new stock record
                new_stock = StockModel(
                    symbol=symbol.upper(),
                    name=stock_data.get("name", f"{symbol} Company"),
                    current_price=stock_data.get("price", 0),
                    currency=stock_data.get("currency", "USD"),
                    exchange=stock_data.get("exchange", "NASDAQ"),
                    market_cap=stock_data.get("market_cap", 0),
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                self.db.add(new_stock)
                self.db.commit()
                self.db.refresh(new_stock)
                
                return Stock(
                    id=new_stock.id,
                    symbol=new_stock.symbol,
                    name=new_stock.name,
                    sector=new_stock.sector,
                    industry=new_stock.industry,
                    market_cap=new_stock.market_cap,
                    current_price=new_stock.current_price,
                    currency=new_stock.currency,
                    exchange=new_stock.exchange,
                    is_active=new_stock.is_active,
                    created_at=new_stock.created_at.isoformat(),
                    updated_at=new_stock.updated_at.isoformat()
                )
        except Exception as e:
            self.logger.error(f"Failed to get stock {symbol}: {str(e)}")
            raise Exception(f"Failed to get stock: {str(e)}")
    
    async def get_stock_data(self, symbol: str, period: str = "1d") -> List[StockData]:
        """
        Get historical stock data
        
        Args:
            symbol: Stock symbol
            period: Data period
            
        Returns:
            Historical stock data
        """
        try:
            # Get stock from database
            stock = self.db.query(StockModel).filter(StockModel.symbol == symbol.upper()).first()
            if not stock:
                raise ValueError(f"Stock {symbol} not found")
            
            # Get historical data from API
            historical_data = await self.stock_api_client.get_historical_data(symbol, period)
            
            result = []
            for i, data_point in enumerate(historical_data):
                # Store in database for caching
                stock_data = StockDataModel(
                    stock_id=stock.id,
                    timestamp=datetime.fromisoformat(data_point["date"]),
                    open_price=data_point["open"],
                    high_price=data_point["high"],
                    low_price=data_point["low"],
                    close_price=data_point["close"],
                    volume=data_point["volume"],
                    adjusted_close=data_point["close"],
                    data_source="yahoo_finance"
                )
                self.db.add(stock_data)
                result.append(StockData(
                    id=i + 1,
                    stock_id=stock.id,
                    timestamp=stock_data.timestamp.isoformat(),
                    open_price=stock_data.open_price,
                    high_price=stock_data.high_price,
                    low_price=stock_data.low_price,
                    close_price=stock_data.close_price,
                    volume=stock_data.volume,
                    adjusted_close=stock_data.adjusted_close,
                    data_source=stock_data.data_source
                ))
            
            self.db.commit()
            return result
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Failed to get stock data for {symbol}: {str(e)}")
            raise Exception(f"Failed to get stock data: {str(e)}")
    
    async def search_stocks(self, query: str) -> List[Stock]:
        """
        Search for stocks
        
        Args:
            query: Search query
            
        Returns:
            List of matching stocks
        """
        try:
            # Search in database first
            stocks = self.db.query(StockModel).filter(
                or_(
                    StockModel.symbol.ilike(f"%{query}%"),
                    StockModel.name.ilike(f"%{query}%")
                )
            ).limit(10).all()
            
            result = []
            for stock in stocks:
                result.append(Stock(
                    id=stock.id,
                    symbol=stock.symbol,
                    name=stock.name,
                    sector=stock.sector,
                    industry=stock.industry,
                    market_cap=stock.market_cap,
                    current_price=stock.current_price,
                    currency=stock.currency,
                    exchange=stock.exchange,
                    is_active=stock.is_active,
                    created_at=stock.created_at.isoformat(),
                    updated_at=stock.updated_at.isoformat()
                ))
            
            return result
        except Exception as e:
            self.logger.error(f"Failed to search stocks: {str(e)}")
            raise Exception(f"Failed to search stocks: {str(e)}")
    
    async def get_portfolio_summary(self, user_id: int) -> Dict[str, Any]:
        """
        Get portfolio summary for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Portfolio summary
        """
        try:
            # Get tracked stocks for user
            tracked_stocks = self.db.query(TrackedStockModel).join(StockModel).filter(
                and_(
                    TrackedStockModel.user_id == user_id,
                    TrackedStockModel.is_active == True
                )
            ).all()
            
            if not tracked_stocks:
                return {
                    "total_stocks": 0,
                    "total_value": 0.0,
                    "daily_change": 0.0,
                    "daily_change_percent": 0.0,
                    "top_performer": None,
                    "worst_performer": None
                }
            
            # Calculate portfolio metrics
            total_value = 0.0
            daily_changes = []
            stock_performances = []
            
            for tracked in tracked_stocks:
                stock = tracked.stock
                # Mock calculation - in real system, you'd calculate based on user's holdings
                stock_value = stock.current_price * 100  # Assume 100 shares
                total_value += stock_value
                
                # Get daily change (mock calculation)
                daily_change = stock.current_price * 0.01  # 1% change
                daily_changes.append(daily_change)
                stock_performances.append({
                    "symbol": stock.symbol,
                    "change": daily_change,
                    "change_percent": 1.0
                })
            
            # Find top and worst performers
            stock_performances.sort(key=lambda x: x["change"], reverse=True)
            top_performer = stock_performances[0]["symbol"] if stock_performances else None
            worst_performer = stock_performances[-1]["symbol"] if stock_performances else None
            
            total_daily_change = sum(daily_changes)
            daily_change_percent = (total_daily_change / total_value * 100) if total_value > 0 else 0
            
            return {
                "total_stocks": len(tracked_stocks),
                "total_value": total_value,
                "daily_change": total_daily_change,
                "daily_change_percent": daily_change_percent,
                "top_performer": top_performer,
                "worst_performer": worst_performer
            }
        except Exception as e:
            self.logger.error(f"Failed to get portfolio summary: {str(e)}")
            raise Exception(f"Failed to get portfolio summary: {str(e)}")