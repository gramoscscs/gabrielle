from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    """Base interface for all Bedrock tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique tool identifier (e.g., 'terraform_cli', 'git_cli' 'aws_cli')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable tool description."""
        pass

    @abstractmethod
    def schema(self) -> dict[str, Any]:
        """Return Bedrock tool specification.
        
        Must return:
        {
            "toolSpec": {
                "name": str,
                "description": str,
                "inputSchema": {...P}
            }
        }
        """
        pass

    @abstractmethod
    def execute(self, tool_input: dict[str, Any]) -> dict [str, Any]:
        """Execute the tool with given input.

        Should return:
        {
            "ok": bool,
            "error"?: str,
            ... other result fields ...
        }        
        """
        pass

    @abstractmethod
    def format_result(self, result: dict[str, Any]) -> str:
        """Format execution result for Bedrock consumption."""
        pass