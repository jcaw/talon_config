"""General VSCode integration for Talon."""

from typing import Any, Optional
from talon import Module, Context, actions
from user.plugins.vimfinity.vimfinity import vimfinity_bind_keys
from user.plugins.vscode_command_client.command_client import NotSet
from user.plugins.vscode_command_client.rpc_client.types import NoFileServerException
from user.utils.formatting import SurroundingText
from user.apps.generic.code_editor import DocumentPositionInfo


# Convenience mappings
user = actions.user
key = actions.key
insert = actions.insert
sleep = actions.sleep


module = Module()
module.tag("vscode", desc="Enabled when Visual Studio Code is the active application.")

# FIXME: When first loading talon, this context doesn't seem to want to activate.
# Context for VSCode
vscode_context = Context()
# TODO: Matching for Mac and Linux. This is Windows-specific.
vscode_context.matches = r"""
title: /Visual Studio Code/
app: /code/
"""

vscode_context.tags = ["user.vscode", "user.command_client", "user.code_editor"]


@module.action_class
class VSCodeModuleActions:
    def vscode_rpc_command(
        command_id: str,
        arg1: Any = NotSet,
        arg2: Any = NotSet,
        arg3: Any = NotSet,
        arg4: Any = NotSet,
        arg5: Any = NotSet,
        block: bool = True,
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
    
    def vscode_restart_extension_host() -> None:
        """Restart the VSCode extension host."""
        try:
            actions.user.vscode_rpc_command("workbench.action.restartExtensionHost")
        except Exception as e:
            # Fallback to keyboard approach
            key("ctrl-shift-p")
            actions.sleep("200ms")
            insert("restart extension")
            actions.sleep("200ms")
            key("enter")

    def vscode_get_all_commands() -> None:
        """Get all VSCode commands organized hierarchically and copy to clipboard."""
        actions.user.vscode_rpc_command("jcaw.getAllCommandsHierarchical")


@vscode_context.action_class("user")
class VSCodeActions:
    def command_server_directory() -> str:
        return "vscode-command-server"

    def vscode_rpc_command(
        command_id: str,
        arg1: Any = NotSet,
        arg2: Any = NotSet,
        arg3: Any = NotSet,
        arg4: Any = NotSet,
        arg5: Any = NotSet,
        block: bool = True,
    ):
        try:
            if block:
                actions.user.run_rpc_command_and_wait(command_id, arg1, arg2, arg3, arg4, arg5)
            else:
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
        # Unlike the non-get version, this doesn't need to be wrapped, it'll raise its own error.
        return actions.user.run_rpc_command_get(
            command_id, arg1, arg2, arg3, arg4, arg5
        )


@vscode_context.action_class("app")
class AppActions:
    def path() -> str:
        return actions.user.vscode_rpc_command_get("jcaw.getFilePath")


@vscode_context.action_class("edit")
class EditActions:
    def selected_text() -> str:
        result = actions.user.vscode_rpc_command_get("jcaw.getSelectedText")
        return result["text"]

    def save():
        actions.user.vscode_rpc_command("workbench.action.files.save")


@vscode_context.action_class("self")
class SelfActions:
    def surrounding_text() -> Optional[SurroundingText]:
        result = actions.user.vscode_rpc_command_get("jcaw.getDictationContext")
        return SurroundingText(
            text_before=result["before"],
            text_after=result["after"]
        )


@vscode_context.action_class("user")
class VSCodeUserActions:
    def current_row() -> int:
        pos = actions.user.vscode_rpc_command_get("jcaw.getCursorPosition")
        return pos["line"] + 1  # Convert from 0-based to 1-based

    def current_column() -> int:
        pos = actions.user.vscode_rpc_command_get("jcaw.getCursorPosition")
        return pos["column"]

    def cursor_offset() -> int:
        pos = actions.user.vscode_rpc_command_get("jcaw.getCursorPosition")
        return pos["offset"]

    def project_root() -> str:
        return actions.user.vscode_rpc_command_get("jcaw.getProjectRoot")

    def find_definition() -> None:
        actions.user.vscode_rpc_command("editor.action.revealDefinition")

    def find_references() -> None:
        actions.user.vscode_rpc_command("editor.action.goToReferences")

    def find_implementations() -> None:
        actions.user.vscode_rpc_command("editor.action.goToImplementation")

    def show_documentation() -> None:
        actions.user.vscode_rpc_command("editor.action.showHover")

    def open_file() -> None:
        actions.user.vscode_rpc_command("workbench.action.quickOpen")

    def git_ui() -> None:
        actions.user.vscode_rpc_command("workbench.view.scm")

    def git_commit() -> None:
        actions.user.vscode_rpc_command("git.commit")

    def git_stage_file() -> None:
        actions.user.vscode_rpc_command("git.stage")

    def search(text: str = None) -> None:
        actions.user.vscode_rpc_command("workbench.action.findInFiles")
        if text:
            actions.sleep("500ms")
            insert(text)

    def next_error() -> None:
        actions.user.vscode_rpc_command("editor.action.marker.nextInFiles")

    def previous_error() -> None:
        actions.user.vscode_rpc_command("editor.action.marker.prevInFiles")

    def toggle_comment() -> None:
        actions.user.vscode_rpc_command("editor.action.commentLine")

    def document_start() -> None:
        actions.user.vscode_rpc_command("cursorTop")

    def document_end() -> None:
        actions.user.vscode_rpc_command("cursorBottom")

    def toggle_fold() -> None:
        actions.user.vscode_rpc_command("editor.toggleFold")

    def fold() -> None:
        actions.user.vscode_rpc_command("editor.fold")

    def unfold() -> None:
        actions.user.vscode_rpc_command("editor.unfold")

    def fold_all() -> None:
        actions.user.vscode_rpc_command("editor.foldAll")

    def unfold_all() -> None:
        actions.user.vscode_rpc_command("editor.unfoldAll")

    def next_fold() -> None:
        actions.user.vscode_rpc_command("editor.gotoNextFold")

    def previous_fold() -> None:
        actions.user.vscode_rpc_command("editor.gotoPreviousFold")

    def zoom_in() -> None:
        actions.user.vscode_rpc_command("editor.action.fontZoomIn")

    def zoom_out() -> None:
        actions.user.vscode_rpc_command("editor.action.fontZoomOut")

    def document_position() -> DocumentPositionInfo:
        cursor_pos = actions.user.vscode_rpc_command_get("jcaw.getCursorPosition")
        return DocumentPositionInfo(
            path=actions.app.path(),  # May be None for untitled files
            line_number=cursor_pos["line"] + 1,  # Convert from 0-based to 1-based
            column=cursor_pos["column"],
            offset=cursor_pos["offset"]
        )

    # FIXME: The prototypes for these are not defined. Probably need to define them.
    # def delete_line() -> None:
    #     """Delete the current line."""
    #     actions.user.vscode_rpc_command("editor.action.deleteLines")

    # def delete_word() -> None:
    #     """Delete the current word."""
    #     actions.user.vscode_rpc_command("deleteWord")

    # def select_line(line: int = None) -> None:
    #     """Select the entire current line."""
    #     if isinstance(line, int):
    #         assert(line > 0, line)
    #         actions.user.goto_line(line)
    #     actions.user.vscode_rpc_command("expandLineSelection")

    # def select_word() -> None:
    #     """Select the current word."""
    #     actions.user.vscode_rpc_command("editor.action.addSelectionToNextFindMatch")
    #     key("esc")

    def goto_line(line: int) -> None:
        actions.user.vscode_rpc_command("editor.action.gotoLine")
        actions.sleep("100ms")
        insert(str(line))
        key("enter")


vimfinity_bind_keys(
    {
        # "p" means "page-specific", or "app-specific" in this case
        "p": "VSCode",
        "p r": (user.vscode_restart_extension_host, "Restart extension host"),
        "p c": (user.vscode_get_all_commands, "Get all commands"),
    },
    vscode_context,
)
