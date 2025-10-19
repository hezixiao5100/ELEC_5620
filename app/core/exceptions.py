"""
Custom Exceptions
"""

class StockAnalysisException(Exception):
    """Base exception for stock analysis system"""
    pass

class UserNotFoundException(StockAnalysisException):
    """User not found exception"""
    pass

class StockNotFoundException(StockAnalysisException):
    """Stock not found exception"""
    pass

class AlertNotFoundException(StockAnalysisException):
    """Alert not found exception"""
    pass

class ReportNotFoundException(StockAnalysisException):
    """Report not found exception"""
    pass

class UnauthorizedException(StockAnalysisException):
    """Unauthorized access exception"""
    pass

class InvalidCredentialsException(StockAnalysisException):
    """Invalid credentials exception"""
    pass

class DuplicateResourceException(StockAnalysisException):
    """Duplicate resource exception"""
    pass

class ExternalAPIException(StockAnalysisException):
    """External API error exception"""
    pass

class AgentExecutionException(StockAnalysisException):
    """Agent execution error exception"""
    pass


