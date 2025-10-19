"""
Base Agent Class
All agents inherit from this base class
"""
from abc import ABC, abstractmethod
from typing import Any, Dict
from enum import Enum

class AgentStatus(str, Enum):
    """Agent status enumeration"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class BaseAgent(ABC):
    """
    Abstract base class for all agents
    """
    
    def __init__(self, agent_id: str):
        """
        Initialize base agent
        
        Args:
            agent_id: Unique identifier for the agent
        """
        self.agent_id = agent_id
        self.status = AgentStatus.IDLE
    
    @abstractmethod
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent task
        
        Args:
            task_data: Input data for the task
            
        Returns:
            Task execution result
        """
        # TODO: Implement in subclasses
        pass
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data
        
        Args:
            data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        # TODO: Implement validation logic
        return True
    
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """
        Handle agent execution errors
        
        Args:
            error: Exception that occurred
            
        Returns:
            Error information dictionary
        """
        # TODO: Implement error handling
        self.status = AgentStatus.FAILED
        return {
            "agent_id": self.agent_id,
            "status": "error",
            "error_message": str(error)
        }
    
    def get_status(self) -> AgentStatus:
        """
        Get current agent status
        
        Returns:
            Current status
        """
        return self.status


