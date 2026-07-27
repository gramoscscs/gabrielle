from __future__ import annotations

from typing import Any, Callable

from terraform import execute_terraform_tool, format_tool_result_for_bedrock, get_terraform_tool_spec


ToolHandler = Callable[[dict[str, Any]], dict[str, Any]]


_TOOL_SPECS: dict[str, dict[str, Any]] = {
    "terraform_cli": get_terraform_tool_spec(),
}

_TOOL_HANDLERS: dict[str, ToolHandler] = {
    "terraform_cli": execute_terraform_tool,
}


def get_bedrock_tool_config() -> dict[str, Any]:
    return {
        "tools": list(_TOOL_SPECS.values()),
    }


def execute_tool(tool_name: str, tool_input: dict[str, Any]) -> dict[str, Any]:
    handler = _TOOL_HANDLERS.get(tool_name)
    if handler is None:
        return {
            "ok": False,
            "error": f"Unknown tool: {tool_name}",
        }

    try:
        return handler(tool_input)
    except ValueError as exc:
        return {
            "ok": False,
            "error": str(exc)
        }


def build_tool_result_content(tool_result: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            {
                "json": tool_result,
            },
            {
                "text": format_tool_result_for_bedrock(tool_result),
            },
        ]
    