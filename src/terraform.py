from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from tools.base import Tool


WORKSPACE_ROOT = Path(__file__).resolve().parent
SAFE_SUBCOMMANDS = {"version", "fmt", "init", "validate", "plan", "show"}
BLOCKED_ARGS = {
    "-auto-approve",
    "-destroy",
    "apply",
    "console",
    "destroy",
    "force-unlock",
    "import",
    "login",
    "logout",
    "state",
    "taint",
    "test",
    "untaint",
    "workspace",
}


class TerraformTool(Tool):
    """Bedrock tool for running safe Terraform CLI commands."""

    @property
    def name(self) -> str:
        return "terraform_cli"

    @property
    def description(self) -> str:
        return(
            "Run safe Terraform CLI commands inside the local workspace. "
            "Use this for version checks, formatting, initialization, validation, "
            "planning, and showing saved plan files."
        )

    def schema(self) -> dict[str, Any]:
        return {
            "toolSpec": {
                "name": self.name,
                "description": self.description,
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "subcommand": {
                                "type": "string",
                                "enum": ["version", "fmt", "init", "validate", "plan", "show"],
                                "description": "The Terraform subcommand to execute.",
                            },
                            "working_directory": {
                                "type": "string",
                                "description": "Directory relative to the workspace root. Use '.' for the repo root.",
                                "default": ".",
                            },
                            "args": {
                                "type": "array",
                                "description": "Optional additional CLI arguments for the selected subcommand.",
                                "items": {"type": "string"},
                                "default": [],
                            },
                        },
                        "required": ["subcommand"],
                        "additionalProperties": False,
                    }
                },
            }
        }
    
    def execute(self, tool_input: dict[str, Any]) -> dict[str, Any]:
        subcommand = str(tool_input.get("subcommand", "")).strip()
        if subcommand not in SAFE_SUBCOMMANDS:
            return{
                "ok": False,
                "error":f"Unsupported Terraform subcommand: {subcommand!r}",
            }

        working_directory = self._resolve_working_directory(tool_input.get("working_directory", "."))
        args = self._sanitize_args(tool_input.get("args", []))
        command = self._build_command(subcommand, args)

        try:
            result= subprocess.run(
                command,
                cwd=working_directory,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
        except FileNotFoundError:
            return {
                "ok": False,
                "error": "Terraform CLI was not found on PATH.",
            }

        payload = {
            "ok": result.returncode == 0,
            "exit_code": result.returncode,
            "command": command,
            "working_directory": str(working_directory),
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
        return payload

    def format_result(self, result: dict[str, Any]) -> str:
        return json.dumps(result, indent=2)

    @staticmethod
    def _resolve_working_directory(raw_path: Any) -> Path:
        relative_path = str(raw_path or ".")
        candidate = (WORKSPACE_ROOT / relative_path).resolve()
        if WORKSPACE_ROOT not in candidate.parents and candidate != WORKSPACE_ROOT:
            raise ValueError("working_directory must stay within the workspace root")
        if not candidate.exists():
            raise ValueError(f"working_directory does not exist: {relative_path}")
        if not candidate.is_dir():
            raise ValueError(f"working_directory is not a directory: {relative_path}")
        return candidate

    @staticmethod
    def _sanitize_args(raw_args: Any) -> list[str]:
        if raw_args is None:
            return []
        if not isinstance(raw_args, list):
            raise ValueError("args must be a list of strings")

        sanitized: list[str] = []
        for item in raw_args:
            arg = str(item).strip()
            if not arg:
                continue
            if arg in BLOCKED_ARGS:
                raise ValueError(f"Blocked Terraform argument: {arg}")
            sanitized.append(arg)
        return sanitized

    @staticmethod
    def _build_command(subcommand: str, args: list[str]) -> list[str]:
        command = ["terraform", subcommand]
        if subcommand in {"init", "validate", "plan", "show"}:
            command.append("-no-color")
            if subcommand in {"init", "plan"}:
                command.append("-input=false")
        command.extend(args)
        return command
    