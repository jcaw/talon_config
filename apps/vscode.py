"""General VSCode integration for Talon."""

from typing import Any
from talon import Module, Context, actions
from user.plugins.vimfinity.vimfinity import vimfinity_bind_keys
from user.plugins.vscode_command_client.command_client import NotSet
from user.plugins.vscode_command_client.rpc_client.types import NoFileServerException

module = Module()
module.tag("vscode", desc="Enabled when Visual Studio Code is the active application.")


@module.action_class
class VSCodeModuleActions:
    def vscode_rpc_command(
        command_id: str,
        arg1: Any = NotSet,
        arg2: Any = NotSet,
        arg3: Any = NotSet,
        arg4: Any = NotSet,
        arg5: Any = NotSet,
    ):
        """Execute VSCode RPC command. Only works when VSCode is active."""
        raise RuntimeError("VSCode is not the active application")

    def vscode_rpc_command_get(
        command_id: str,
        arg1: Any = NotSet,
        arg2: Any = NotSet,
        arg3: Any = NotSet,
        arg4: Any = NotSet,
        arg5: Any = NotSet,
    ) -> Any:
        """Execute VSCode RPC command and return result. Only works when VSCode is active."""
        raise RuntimeError("VSCode is not the active application")


# Context for VSCode and VSCode-based editors
vscode_context = Context()
vscode_context.matches = r"""
title: /Visual Studio Code/
app: /code/
"""
vscode_context.tags = ["user.vscode", "user.command_client"]


@vscode_context.action_class("user")
class VSCodeActions:
    def command_server_directory() -> str:
        """Return the VSCode command server directory name."""
        return "vscode-command-server"

    def vscode_rpc_command(
        command_id: str,
        arg1: Any = NotSet,
        arg2: Any = NotSet,
        arg3: Any = NotSet,
        arg4: Any = NotSet,
        arg5: Any = NotSet,
    ):
        """Execute VSCode RPC command via command server."""
        try:
            actions.user.run_rpc_command(command_id, arg1, arg2, arg3, arg4, arg5)
        except NoFileServerException:
            raise RuntimeError(
                "VSCode command server not found. Is the command-server extension installed in VSCode?"
            )

    def vscode_rpc_command_get(
        command_id: str,
        arg1: Any = NotSet,
        arg2: Any = NotSet,
        arg3: Any = NotSet,
        arg4: Any = NotSet,
        arg5: Any = NotSet,
    ) -> Any:
        """Execute VSCode RPC command via command server and return result."""
        # Unlike the non-get version, this doesn't need to be wrapped, it'll raise its own error.
        return actions.user.run_rpc_command_get(
            command_id, arg1, arg2, arg3, arg4, arg5
        )


@vscode_context.action_class("app")
class AppActions:
    def path() -> str:
        """Get the path of the currently active file."""
        return actions.user.vscode_rpc_command_get("jcaw.getFilePath")


@vscode_context.action_class("main")
class MainActions:
    def cursor_position() -> tuple[int, int]:
        """Get cursor position as (line, column). Both are 0-based."""
        pos = actions.user.vscode_rpc_command_get("jcaw.getCursorPosition")
        return (pos["line"], pos["column"])

    def selected_text() -> str:
        """Get the currently selected text."""
        result = actions.user.vscode_rpc_command_get("jcaw.getSelectedText")
        return result["text"]


@vscode_context.action_class("user")
class VSCodeUserActions:
    def dictation_get_context() -> tuple[str, str]:
        """Get text before and after cursor for context-sensitive dictation."""
        result = actions.user.vscode_rpc_command_get("jcaw.getDictationContext")
        return (result["before"], result["after"])
