"""
Risk Analysis Agent
Analyzes investment risk and volatility
"""
from typing import Dict, Any
from datetime import datetime

from app.agents.base_agent import BaseAgent

class RiskAnalysisAgent(BaseAgent):
    """
    Agent responsible for risk analysis
    """
    
    def __init__(self, agent_id: str = "risk_analysis"):
        """
        Initialize Risk Analysis Agent
        
        Args:
            agent_id: Agent identifier
        """
        super().__init__(agent_id, "Risk Analysis Agent")
    
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute risk analysis task
        
        Args:
            task_data: Task parameters including stock data
            
        Returns:
            Risk analysis results
        """
        stock_data = task_data.get("stock_data", {})
        market_data = task_data.get("market_data", {})
        
        if not stock_data:
            raise ValueError("Stock data is required for risk analysis")
        
        # Calculate risk metrics
        volatility = self.calculate_volatility(stock_data)
        beta = self.calculate_beta(stock_data, market_data)
        var = self.calculate_var(stock_data)
        risk_score = self.calculate_risk_score(volatility, beta, var)
        
        return {
            "symbol": stock_data.get("symbol", ""),
            "volatility": volatility,
            "beta": beta,
            "var": var,
            "risk_score": risk_score,
            "risk_level": self.assess_risk_level(risk_score),
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    def calculate_volatility(self, stock_data: Dict[str, Any]) -> float:
        """Calculate price volatility"""
        historical_data = stock_data.get("historical_data", [])
        if len(historical_data) < 10:
            return 0.0
        
        prices = [float(day.get("close", 0)) for day in historical_data if day.get("close")]
        if len(prices) < 2:
            return 0.0
        
        # Calculate daily returns
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        
        # Calculate standard deviation
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        volatility = variance ** 0.5
        
        return round(volatility * 100, 2)  # Convert to percentage
    
    def calculate_beta(self, stock_data: Dict[str, Any], market_data: Dict[str, Any]) -> float:
        """Calculate beta coefficient"""
        # Simplified beta calculation
        # In a real system, you would compare stock returns to market returns
        volatility = self.calculate_volatility(stock_data)
        
        if volatility < 10:
            return 0.8  # Low volatility = low beta
        elif volatility < 20:
            return 1.0  # Medium volatility = neutral beta
        else:
            return 1.2  # High volatility = high beta
    
    def calculate_var(self, stock_data: Dict[str, Any]) -> float:
        """Calculate Value at Risk (95% confidence)"""
        historical_data = stock_data.get("historical_data", [])
        if len(historical_data) < 10:
            return 0.0
        
        prices = [float(day.get("close", 0)) for day in historical_data if day.get("close")]
        if len(prices) < 2:
            return 0.0
        
        # Calculate daily returns
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        
        # Sort returns and find 5th percentile
        returns.sort()
        var_index = int(len(returns) * 0.05)
        var = abs(returns[var_index]) if var_index < len(returns) else 0
        
        return round(var * 100, 2)  # Convert to percentage
    
    def calculate_risk_score(self, volatility: float, beta: float, var: float) -> float:
        """Calculate overall risk score (0-100)"""
        # Weighted risk score
        score = (volatility * 0.4) + (abs(beta - 1.0) * 20 * 0.3) + (var * 0.3)
        return min(100, max(0, round(score, 1)))
    
    def assess_risk_level(self, risk_score: float) -> str:
        """Assess risk level based on score"""
        if risk_score < 20:
            return "LOW"
        elif risk_score < 50:
            return "MEDIUM"
        elif risk_score < 80:
            return "HIGH"
        else:
            return "VERY_HIGH"