"""
Custom Exceptions for Stock Analysis System
Centralized exception handling
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException, status


class StockAnalysisException(Exception):
    """Base exception for stock analysis system"""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = "GENERAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details if details is not None else {}
        super().__init__(self.message)


class DatabaseException(StockAnalysisException):
    """Database related exceptions"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=details
        )


class ExternalAPIException(StockAnalysisException):
    """External API related exceptions"""
    
    def __init__(self, message: str, api_name: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="EXTERNAL_API_ERROR",
            details={**details, "api_name": api_name} if details else {"api_name": api_name}
        )


class AuthenticationException(StockAnalysisException):
    """Authentication related exceptions"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            details=details
        )


class AuthorizationException(StockAnalysisException):
    """Authorization related exceptions"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            details=details
        )


class ValidationException(StockAnalysisException):
    """Data validation related exceptions"""
    
    def __init__(self, message: str, field: str = None, details: Optional[Dict[str, Any]] = None):
        details = details if details is not None else {}
        if field:
            details["field"] = field
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details
        )


class BusinessLogicException(StockAnalysisException):
    """Business logic related exceptions"""
    
    def __init__(self, message: str, operation: str = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="BUSINESS_LOGIC_ERROR",
            details={**details, "operation": operation} if operation else details
        )


class TaskException(StockAnalysisException):
    """Background task related exceptions"""
    
    def __init__(self, message: str, task_name: str = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="TASK_ERROR",
            details={**details, "task_name": task_name} if task_name else details
        )


class AgentException(StockAnalysisException):
    """AI Agent related exceptions"""
    
    def __init__(self, message: str, agent_name: str = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AGENT_ERROR",
            details={**details, "agent_name": agent_name} if agent_name else details
        )


# HTTP Exception mappings
EXCEPTION_HTTP_STATUS_MAP = {
    DatabaseException: status.HTTP_503_SERVICE_UNAVAILABLE,
    ExternalAPIException: status.HTTP_502_BAD_GATEWAY,
    AuthenticationException: status.HTTP_401_UNAUTHORIZED,
    AuthorizationException: status.HTTP_403_FORBIDDEN,
    ValidationException: status.HTTP_422_UNPROCESSABLE_ENTITY,
    BusinessLogicException: status.HTTP_400_BAD_REQUEST,
    TaskException: status.HTTP_500_INTERNAL_SERVER_ERROR,
    AgentException: status.HTTP_500_INTERNAL_SERVER_ERROR,
    StockAnalysisException: status.HTTP_500_INTERNAL_SERVER_ERROR,
}


def convert_to_http_exception(exc: StockAnalysisException) -> HTTPException:
    """Convert custom exception to HTTPException"""
    status_code = EXCEPTION_HTTP_STATUS_MAP.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return HTTPException(
        status_code=status_code,
        detail={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )