from __future__ import annotations

from typing import Any

from tools.base import Tool
from terraform import TerraformTool


# Registry of all available tools (add new tools to this list)
_TOOLS: list[Tool] = [
     TerraformTool(),
     # GitTool(),
     # AWSTool(),
     # CloudWatchTool(),
]

# Build a name->tool lookup for fast execution
_TOOLS_BY_NAME: dict[str, Tool] = {tool.name: tool for tool in _TOOLS}


def get_bedrock_tool_config() -> dict[str, Any]:
    """Return Bedrock tool configuration with all registered tools."""
    return {
         "tools": [tool.schema() for tool in _TOOLS],
    }


def execute_tool(tool_name: str, tool_input: dict[str, Any]) -> dict[str, Any]:
    """Execute a tool by name."""
    tool = _TOOLS_BY_NAME.get(tool_name)
    if tool is None:
         return {
              "ok": False,
              "error": f"Unknown tool: {tool_name}",
         }

    try:
        return tool.execute(tool_input)
    except ValueError as exc:
         return {
              "ok": False,
              "error": str(exc),
         }


def build_tool_result_content(tool_name: str, tool_result: dict[str, Any]) -> list[dict[str, Any]]:
    """Format tool result for Bedrock consumption."""
    tool = _TOOLS_BY_NAME.get(tool_name)
    if tool is None:
        formatted_text = str(tool_result)
    else:
        formatted_text = tool.format_result(tool_result)

    return [
        {
            "json": tool_result,
        },
        {
            "text": formatted_text,
        },
    ]
