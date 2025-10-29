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
        Execute risk analysis task (Enhanced version)
        
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
        annualized_volatility = self.calculate_annualized_volatility(volatility)
        beta = self.calculate_beta(stock_data, market_data)
        var = self.calculate_var(stock_data)
        max_drawdown = self.calculate_max_drawdown(stock_data)
        sharpe_ratio = self.calculate_sharpe_ratio(stock_data)
        risk_score = self.calculate_risk_score(volatility, beta, var)
        risk_level = self.assess_risk_level(risk_score)
        
        # Generate risk recommendations
        risk_metrics = {
            "volatility": annualized_volatility,
            "max_drawdown": max_drawdown,
            "beta": beta,
            "sharpe_ratio": sharpe_ratio,
            "risk_level": risk_level
        }
        recommendations = self.generate_risk_recommendations(risk_metrics)
        
        return {
            "symbol": stock_data.get("symbol", ""),
            "volatility": {
                "daily": volatility,
                "annualized": annualized_volatility
            },
            "beta": beta,
            "var": var,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe_ratio,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "recommendations": recommendations,
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
    
    def calculate_max_drawdown(self, stock_data: Dict[str, Any]) -> float:
        """
        Calculate maximum drawdown
        
        Args:
            stock_data: Stock data including historical prices
            
        Returns:
            Maximum drawdown percentage
        """
        historical_data = stock_data.get("historical_data", [])
        if len(historical_data) < 10:
            return 0.0
        
        prices = [float(day.get("close", 0)) for day in historical_data if day.get("close")]
        if len(prices) < 2:
            return 0.0
        
        # Calculate cumulative returns
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        cumulative_returns = [1.0]
        for ret in returns:
            cumulative_returns.append(cumulative_returns[-1] * (1 + ret))
        
        # Calculate drawdowns
        running_max = [cumulative_returns[0]]
        for val in cumulative_returns[1:]:
            running_max.append(max(running_max[-1], val))
        
        drawdowns = [(cumulative_returns[i] - running_max[i]) / running_max[i] 
                     for i in range(len(cumulative_returns))]
        
        max_drawdown = min(drawdowns) * 100  # Convert to percentage
        return round(max_drawdown, 2)
    
    def calculate_annualized_volatility(self, volatility: float, trading_days: int = 252) -> float:
        """
        Calculate annualized volatility
        
        Args:
            volatility: Daily volatility percentage
            trading_days: Number of trading days in a year
            
        Returns:
            Annualized volatility percentage
        """
        return round(volatility * (trading_days ** 0.5), 2)
    
    def calculate_sharpe_ratio(self, stock_data: Dict[str, Any], risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sharpe Ratio
        
        Args:
            stock_data: Stock data including historical prices
            risk_free_rate: Risk-free rate (default 2%)
            
        Returns:
            Sharpe ratio
        """
        historical_data = stock_data.get("historical_data", [])
        if len(historical_data) < 10:
            return 0.0
        
        prices = [float(day.get("close", 0)) for day in historical_data if day.get("close")]
        if len(prices) < 2:
            return 0.0
        
        # Calculate returns
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        
        # Calculate mean return and standard deviation
        avg_return = sum(returns) / len(returns)
        std_return = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5
        
        # Annualize
        annual_return = avg_return * 252
        annual_std = std_return * (252 ** 0.5)
        
        # Sharpe ratio
        if annual_std == 0:
            return 0.0
        sharpe = (annual_return - risk_free_rate) / annual_std
        return round(sharpe, 2)
    
    def generate_risk_recommendations(self, risk_metrics: Dict[str, Any]) -> list:
        """
        Generate risk recommendations based on metrics
        
        Args:
            risk_metrics: Dictionary of risk metrics
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        volatility = risk_metrics.get("volatility", 0)
        max_drawdown = risk_metrics.get("max_drawdown", 0)
        beta = risk_metrics.get("beta", 1.0)
        sharpe = risk_metrics.get("sharpe_ratio", 0)
        risk_level = risk_metrics.get("risk_level", "MEDIUM")
        
        # Based on volatility
        if volatility > 40:
            recommendations.append("⚠️ 高波动性：建议控制仓位，避免过度集中")
        elif volatility < 15:
            recommendations.append("✅ 低波动性：相对稳定，适合保守投资者")
        
        # Based on max drawdown
        if max_drawdown < -30:
            recommendations.append("⚠️ 大幅回撤风险：历史上曾有较大跌幅，需要谨慎")
        elif max_drawdown < -20:
            recommendations.append("⚠️ 中等回撤：历史上有明显的价格回调")
        
        # Based on Beta
        if beta > 1.5:
            recommendations.append("⚠️ 高 Beta：该股票波动性高于市场平均水平，适合风险偏好较高的投资者")
        elif beta < 0.5:
            recommendations.append("✅ 低 Beta：该股票相对稳定，与市场相关性较低")
        
        # Based on Sharpe ratio
        if sharpe < 0:
            recommendations.append("⚠️ 负夏普比率：风险调整后收益为负，投资回报不佳")
        elif sharpe > 1.0:
            recommendations.append("✅ 良好的风险收益比：夏普比率 > 1.0，风险调整后收益较好")
        elif sharpe > 0.5:
            recommendations.append("✓ 合理的风险收益比：夏普比率在可接受范围内")
        
        # Based on overall risk level
        if risk_level == "VERY_HIGH":
            recommendations.append("🔴 极高风险：建议谨慎投资，仅适合风险承受能力极强的投资者")
        elif risk_level == "HIGH":
            recommendations.append("🟠 高风险：建议严格控制仓位，密切关注市场变化")
        
        if not recommendations:
            recommendations.append("✅ 风险指标在合理范围内")
        
        return recommendations