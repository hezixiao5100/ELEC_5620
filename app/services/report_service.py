"""
Report Service
Business logic for report operations
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
import logging
import json

from app.agents.agent_manager import AgentManager
from app.schemas.report import Report, ReportRequest, ReportSummary
from app.models.report import Report as ReportModel
from app.models.stock import Stock as StockModel
from app.models.user import User as UserModel

class ReportService:
    """
    Service for report operations
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.agent_manager = AgentManager(db)
        self.logger = logging.getLogger("report_service")
    
    async def generate_report(self, user_id: int, stock_id: int, report_type: str = "COMPREHENSIVE") -> Report:
        """
        Generate a new analysis report
        
        Args:
            user_id: User ID
            stock_id: Stock ID
            report_type: Type of report
            
        Returns:
            Generated report
        """
        try:
            # Get stock information
            stock = self.db.query(StockModel).filter(StockModel.id == stock_id).first()
            if not stock:
                raise ValueError(f"Stock {stock_id} not found")
            
            # Use Agent Manager to generate report
            result = await self.agent_manager.run_stock_analysis_pipeline(
                user_id=user_id,
                stock_symbol=stock.symbol
            )
            
            # Extract data from analysis result
            report_data = result.get("report", {})
            analysis_data = result.get("analysis", {})
            risk_data = result.get("risk_analysis", {})
            emotion_data = result.get("emotional_analysis", {})
            
            # Create report record in database
            report = ReportModel(
                user_id=user_id,
                stock_id=stock_id,
                title=report_data.get("title", f"Analysis Report for {stock.symbol}"),
                summary=report_data.get("executive_summary", "Report summary"),
                risk_level=risk_data.get("risk_level", "MEDIUM"),
                sentiment_score=emotion_data.get("fear_greed_index", {}).get("index", 50),
                technical_signal=analysis_data.get("trading_signal", "HOLD"),
                confidence_score=analysis_data.get("confidence_score", 0.5),
                details_json=result,
                report_type=report_type,
                created_at=datetime.utcnow()
            )
            
            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)
            
            return Report(
                id=report.id,
                user_id=report.user_id,
                stock_id=report.stock_id,
                title=report.title,
                summary=report.summary,
                risk_level=report.risk_level,
                sentiment_score=report.sentiment_score,
                technical_signal=report.technical_signal,
                confidence_score=report.confidence_score,
                details_json=report.details_json,
                report_type=report.report_type,
                created_at=report.created_at.isoformat()
            )
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Failed to generate report: {str(e)}")
            raise Exception(f"Failed to generate report: {str(e)}")
    
    async def get_user_reports(self, user_id: int, limit: int = 10) -> List[Report]:
        """
        Get all reports for current user
        
        Args:
            user_id: User ID
            limit: Maximum number of reports to return
            
        Returns:
            List of reports
        """
        try:
            # Query reports from database
            reports = self.db.query(ReportModel).filter(
                ReportModel.user_id == user_id
            ).order_by(ReportModel.created_at.desc()).limit(limit).all()
            
            result = []
            for report in reports:
                result.append(Report(
                    id=report.id,
                    user_id=report.user_id,
                    stock_id=report.stock_id,
                    title=report.title,
                    summary=report.summary,
                    risk_level=report.risk_level,
                    sentiment_score=report.sentiment_score,
                    technical_signal=report.technical_signal,
                    confidence_score=report.confidence_score,
                    details_json=report.details_json,
                    report_type=report.report_type,
                    created_at=report.created_at.isoformat()
                ))
            
            return result
        except Exception as e:
            self.logger.error(f"Failed to get user reports: {str(e)}")
            raise Exception(f"Failed to get user reports: {str(e)}")
    
    async def get_report_summary(self, user_id: int) -> ReportSummary:
        """
        Get report summary for user
        
        Args:
            user_id: User ID
            
        Returns:
            Report summary
        """
        try:
            # Count different types of reports
            total_reports = self.db.query(ReportModel).filter(ReportModel.user_id == user_id).count()
            
            # Recent reports (last 7 days)
            recent_cutoff = datetime.utcnow() - timedelta(days=7)
            recent_reports = self.db.query(ReportModel).filter(
                and_(
                    ReportModel.user_id == user_id,
                    ReportModel.created_at >= recent_cutoff
                )
            ).count()
            
            # High confidence reports (confidence > 0.7)
            high_confidence_reports = self.db.query(ReportModel).filter(
                and_(
                    ReportModel.user_id == user_id,
                    ReportModel.confidence_score > 0.7
                )
            ).count()
            
            # Count signals
            buy_signals = self.db.query(ReportModel).filter(
                and_(
                    ReportModel.user_id == user_id,
                    ReportModel.technical_signal == "BUY"
                )
            ).count()
            
            sell_signals = self.db.query(ReportModel).filter(
                and_(
                    ReportModel.user_id == user_id,
                    ReportModel.technical_signal == "SELL"
                )
            ).count()
            
            hold_signals = self.db.query(ReportModel).filter(
                and_(
                    ReportModel.user_id == user_id,
                    ReportModel.technical_signal == "HOLD"
                )
            ).count()
            
            # Calculate risk and sentiment distribution
            risk_distribution = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
            sentiment_distribution = {"POSITIVE": 0, "NEUTRAL": 0, "NEGATIVE": 0}
            
            # Get all reports for distribution calculation
            all_reports = self.db.query(ReportModel).filter(ReportModel.user_id == user_id).all()
            
            for report in all_reports:
                # Risk distribution
                if report.risk_level in risk_distribution:
                    risk_distribution[report.risk_level] += 1
                
                # Sentiment distribution (based on sentiment_score)
                if report.sentiment_score > 60:
                    sentiment_distribution["POSITIVE"] += 1
                elif report.sentiment_score < 40:
                    sentiment_distribution["NEGATIVE"] += 1
                else:
                    sentiment_distribution["NEUTRAL"] += 1
            
            return ReportSummary(
                total_reports=total_reports,
                recent_reports=recent_reports,
                high_confidence_reports=high_confidence_reports,
                buy_signals=buy_signals,
                sell_signals=sell_signals,
                hold_signals=hold_signals,
                risk_distribution=risk_distribution,
                sentiment_distribution=sentiment_distribution
            )
        except Exception as e:
            self.logger.error(f"Failed to get report summary: {str(e)}")
            raise Exception(f"Failed to get report summary: {str(e)}")
    
    async def get_report_by_id(self, report_id: int, user_id: int) -> Optional[Report]:
        """
        Get a specific report by ID
        
        Args:
            report_id: Report ID
            user_id: User ID
            
        Returns:
            Report if found, None otherwise
        """
        try:
            report = self.db.query(ReportModel).filter(
                and_(
                    ReportModel.id == report_id,
                    ReportModel.user_id == user_id
                )
            ).first()
            
            if not report:
                return None
            
            return Report(
                id=report.id,
                user_id=report.user_id,
                stock_id=report.stock_id,
                title=report.title,
                summary=report.summary,
                risk_level=report.risk_level,
                sentiment_score=report.sentiment_score,
                technical_signal=report.technical_signal,
                confidence_score=report.confidence_score,
                details_json=report.details_json,
                report_type=report.report_type,
                created_at=report.created_at.isoformat()
            )
        except Exception as e:
            self.logger.error(f"Failed to get report {report_id}: {str(e)}")
            raise Exception(f"Failed to get report: {str(e)}")
    
    async def delete_report(self, report_id: int, user_id: int) -> None:
        """
        Delete a report
        
        Args:
            report_id: Report ID to delete
            user_id: User ID
        """
        try:
            report = self.db.query(ReportModel).filter(
                and_(
                    ReportModel.id == report_id,
                    ReportModel.user_id == user_id
                )
            ).first()
            
            if not report:
                raise ValueError(f"Report {report_id} not found")
            
            self.db.delete(report)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Failed to delete report {report_id}: {str(e)}")
            raise Exception(f"Failed to delete report: {str(e)}")