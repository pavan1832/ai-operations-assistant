"""
Base tool classes and tool registry for AI Operations Assistant
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """Abstract base class for all tools"""
    
    def __init__(self, name: str, description: str, parameters: Optional[Dict[str, Any]] = None):
        """
        Initialize a tool
        
        Args:
            name: Tool identifier
            description: What the tool does
            parameters: Expected parameters schema
        """
        self.name = name
        self.description = description
        self.parameters = parameters or {}
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with given parameters
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            Tool execution results
        """
        pass
    
    def get_spec(self) -> Dict[str, Any]:
        """
        Get tool specification for agent planning
        
        Returns:
            Tool specification dict
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"


class ToolRegistry:
    """Registry for managing available tools"""
    
    def __init__(self):
        """Initialize empty tool registry"""
        self.tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool) -> None:
        """
        Register a new tool
        
        Args:
            tool: Tool instance to register
        """
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def get(self, name: str) -> Optional[BaseTool]:
        """
        Get a tool by name
        
        Args:
            name: Tool name
            
        Returns:
            Tool instance or None
        """
        return self.tools.get(name)
    
    def get_all_specs(self) -> List[Dict[str, Any]]:
        """
        Get specifications for all registered tools
        
        Returns:
            List of tool specifications
        """
        return [tool.get_spec() for tool in self.tools.values()]
    
    def list_tools(self) -> List[str]:
        """
        Get list of registered tool names
        
        Returns:
            List of tool names
        """
        return list(self.tools.keys())
    
    def execute_tool(self, name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a tool by name
        
        Args:
            name: Tool name
            **kwargs: Tool parameters
            
        Returns:
            Tool execution results
        """
        tool = self.get(name)
        if not tool:
            raise ValueError(f"Tool not found: {name}")
        
        try:
            logger.info(f"Executing tool: {name} with params: {kwargs}")
            result = tool.execute(**kwargs)
            logger.info(f"Tool {name} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Tool {name} failed: {str(e)}")
            raise


# Global tool registry instance
_registry = ToolRegistry()


def get_registry() -> ToolRegistry:
    """Get the global tool registry instance"""
    return _registry
