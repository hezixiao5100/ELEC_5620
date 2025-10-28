"""
Base Agent Class
All agents inherit from this base class
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from enum import Enum
import asyncio
import logging
from datetime import datetime

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
    
    def __init__(self, agent_id: str, name: str = None):
        """
        Initialize base agent
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name for the agent
        """
        self.agent_id = agent_id
        self.name = name or agent_id
        self.status = AgentStatus.IDLE
        self.logger = logging.getLogger(f"agent.{agent_id}")
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
    
    @abstractmethod
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent task
        
        Args:
            task_data: Input data for the task
            
        Returns:
            Task execution result
        """
        pass
    
    async def run(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the agent with error handling and status management
        
        Args:
            task_data: Input data for the task
            
        Returns:
            Task execution result or error information
        """
        try:
            # Validate input
            if not self.validate_input(task_data):
                raise ValueError("Invalid input data")
            
            # Set status to running
            self.status = AgentStatus.RUNNING
            self.start_time = datetime.utcnow()
            self.logger.info(f"Agent {self.name} started execution")
            
            # Execute the task
            result = await self.execute_task(task_data)
            
            # Set status to completed
            self.status = AgentStatus.COMPLETED
            self.end_time = datetime.utcnow()
            self.logger.info(f"Agent {self.name} completed successfully")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Agent {self.name} failed: {str(e)}")
            return self.handle_error(e)
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data
        
        Args:
            data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Basic validation - can be overridden in subclasses
        return isinstance(data, dict) and len(data) > 0
    
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """
        Handle agent execution errors
        
        Args:
            error: Exception that occurred
            
        Returns:
            Error information dictionary
        """
        self.status = AgentStatus.FAILED
        self.end_time = datetime.utcnow()
        
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": "error",
            "error_message": str(error),
            "error_type": type(error).__name__,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current agent status and metadata
        
        Returns:
            Status information dictionary
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else None
        }
    
    def reset(self):
        """Reset agent to idle state"""
        self.status = AgentStatus.IDLE
        self.start_time = None
        self.end_time = None




