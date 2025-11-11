"""General VSCode integration for Talon."""

from typing import Any, Optional
from talon import Module, Context, actions
from user.plugins.vimfinity.vimfinity import vimfinity_bind_keys
from user.plugins.vscode_command_client.command_client import NotSet
from user.plugins.vscode_command_client.rpc_client.types import NoFileServerException
from user.utils.formatting import SurroundingText
from user.apps.generic.code_editor import DocumentPositionInfo

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


@vscode_context.action_class("edit")
class EditActions:
    def selected_text() -> str:
        """Get the currently selected text."""
        result = actions.user.vscode_rpc_command_get("jcaw.getSelectedText")
        return result["text"]


@vscode_context.action_class("self")
class SelfActions:
    def surrounding_text() -> Optional[SurroundingText]:
        """Get text before and after cursor for context-sensitive formatting."""
        result = actions.user.vscode_rpc_command_get("jcaw.getDictationContext")
        return SurroundingText(
            text_before=result["before"],
            text_after=result["after"]
        )


@vscode_context.action_class("user")
class VSCodeUserActions:
    def cursor_position() -> tuple[int, int]:
        """Get cursor position as (line, column). Both are 0-based."""
        pos = actions.user.vscode_rpc_command_get("jcaw.getCursorPosition")
        return (pos["line"], pos["column"])

    def project_root() -> str:
        """Get the workspace root path for the current file."""
        return actions.user.vscode_rpc_command_get("jcaw.getProjectRoot")

    def find_definition() -> None:
        """Navigate to the definition of the symbol under cursor."""
        actions.user.vscode_rpc_command("editor.action.revealDefinition")

    def find_references() -> None:
        """Find references to the symbol under cursor."""
        actions.user.vscode_rpc_command("editor.action.goToReferences")

    def find_implementations() -> None:
        """Find implementations of the symbol under cursor."""
        actions.user.vscode_rpc_command("editor.action.goToImplementation")

    def show_documentation() -> None:
        """Show documentation for the symbol under cursor."""
        actions.user.vscode_rpc_command("editor.action.showHover")

    def open_file() -> None:
        """Open a file dialog to open a file."""
        actions.user.vscode_rpc_command("workbench.action.files.openFile")

    def search(text: str = None) -> None:
        """Search for text in the current project or directory."""
        actions.user.vscode_rpc_command("workbench.action.findInFiles")
        if text:
            actions.sleep("500ms")
            actions.insert(text)

    def next_error() -> None:
        """Navigate to the next error or diagnostic."""
        actions.user.vscode_rpc_command("editor.action.marker.nextInFiles")

    def previous_error() -> None:
        """Navigate to the previous error or diagnostic."""
        actions.user.vscode_rpc_command("editor.action.marker.prevInFiles")

    def toggle_comment() -> None:
        """Toggle comment on the current line or selection."""
        actions.user.vscode_rpc_command("editor.action.commentLine")

    def document_start() -> None:
        """Jump to the start of the document."""
        actions.user.vscode_rpc_command("cursorTop")

    def document_end() -> None:
        """Jump to the end of the document."""
        actions.user.vscode_rpc_command("cursorBottom")

    def toggle_fold() -> None:
        """Toggle visibility folding for the current item."""
        actions.user.vscode_rpc_command("editor.toggleFold")

    def fold() -> None:
        """Fold (hide) the current item."""
        actions.user.vscode_rpc_command("editor.fold")

    def unfold() -> None:
        """Unfold (show) the current item."""
        actions.user.vscode_rpc_command("editor.unfold")

    def fold_all() -> None:
        """Fold all items (meaning depends on context)."""
        actions.user.vscode_rpc_command("editor.foldAll")

    def unfold_all() -> None:
        """Unfold all items in the document."""
        actions.user.vscode_rpc_command("editor.unfoldAll")

    def next_fold() -> None:
        """Navigate to the next fold."""
        actions.user.vscode_rpc_command("editor.gotoNextFold")

    def previous_fold() -> None:
        """Navigate to the previous fold."""
        actions.user.vscode_rpc_command("editor.gotoPreviousFold")

    def zoom_in() -> None:
        """Increase the font size in the editor."""
        actions.user.vscode_rpc_command("editor.action.fontZoomIn")

    def zoom_out() -> None:
        """Decrease the font size in the editor."""
        actions.user.vscode_rpc_command("editor.action.fontZoomOut")

    def document_position() -> DocumentPositionInfo:
        """Get document position including file path, row, column, and offset."""
        file_path = actions.app.path()
        cursor_pos = actions.user.vscode_rpc_command_get("jcaw.getCursorPosition")
        return DocumentPositionInfo(
            path=file_path,
            row=cursor_pos["line"],
            column=cursor_pos["column"],
            offset=cursor_pos["offset"]
        )

    def delete_line() -> None:
        """Delete the current line."""
        actions.user.vscode_rpc_command("editor.action.deleteLines")

    def delete_word() -> None:
        """Delete the current word."""
        actions.user.vscode_rpc_command("deleteWord")

    def select_line(line: int = None) -> None:
        """Select the entire current line."""
        if isinstance(line, int):
            assert(line > 0, line)
            actions.user.goto_line(line)
        actions.user.vscode_rpc_command("expandLineSelection")

    def select_word() -> None:
        """Select the current word."""
        actions.user.vscode_rpc_command("editor.action.addSelectionToNextFindMatch")
        actions.key("esc")

    def goto_line(line: int) -> None:
        """Jump to a specific line number in the document."""
        actions.user.vscode_rpc_command("editor.action.gotoLine")
        actions.sleep("100ms")
        actions.insert(str(line))
        actions.key("enter")
