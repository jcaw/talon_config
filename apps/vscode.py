"""General VSCode integration for Talon."""

from typing import Any, Optional
from xml.parsers.expat import model
import time
from talon import Module, Context, actions
from user.plugins.vimfinity.vimfinity import vimfinity_bind_keys
from user.plugins.vscode_command_client.command_client import NotSet
from user.plugins.vscode_command_client.rpc_client.types import NoFileServerException
from user.utils.formatting import SurroundingText
from user.apps.generic.code_editor import DocumentPositionInfo
from user.apps.claude_code import ClaudeCodeTemporaryFocusContext


# Convenience mappings
user = actions.user
key = actions.key
insert = actions.insert
sleep = actions.sleep


module = Module()
module.tag("vscode", desc="Enabled when Visual Studio Code is the active application.")

# Context for VSCode
vscode_context = Context()
# TODO: Matching for Mac and Linux. This is Windows-specific.
vscode_context.matches = r"""
title: /Visual Studio Code/
app: /code/
"""

vscode_context.tags = ["user.vscode", "user.command_client", "user.code_editor"]


# TODO: Remove docstrings from all context classes - they are redundant. Also do this in claude_code.py
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


class ClaudeCodeVSCodeTemporaryFocusContext(ClaudeCodeTemporaryFocusContext):
    """VSCode-specific context manager that focuses Claude Code and uses blur to defocus."""
    def __init__(self):
        super().__init__()

    def __enter__(self):
        actions.user.claude_code_focus_text_input()
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        # VSCode uses blur to defocus instead of restoring window focus
        actions.user.claude_code_blur()
        return False


@module.action_class
class ClaudeVSCodeActions:
    def claude_code_open() -> None:
        """Open Claude Code in VSCode."""
        # HACK: Use Claude's built-in focus command. This isn't perfect, but it should work.
        user.vscode_rpc_command("claude-vscode.focus")

    # TODO: These are ultimately experimental and should probably be removed.
    def claude_code_open_sidebar() -> None:
        """Open Claude Code in the sidebar."""
        user.vscode_rpc_command("claude-vscode.sidebar.open")

    def claude_code_open_editor() -> None:
        """Open Claude Code in a new editor tab."""
        user.vscode_rpc_command("claude-vscode.editor.open")

    def claude_code_open_window() -> None:
        """Open Claude Code in a new VSCode window."""
        user.vscode_rpc_command("claude-vscode.window.open")

    def claude_code_open_terminal() -> None:
        """Open Claude Code in the terminal."""
        user.vscode_rpc_command("claude-vscode.terminal.open")

    # TODO: Remove - these are old focus approaches I was experimenting with.
    # def claude_code_focus() -> None:
    #     """Focus the Claude Code input box."""
    #     # Use custom focus command that bypasses the broken claude-vscode.focus
    #     user.vscode_rpc_command("jcaw.claudeCodeFocusAuxiliary")

    # def claude_code_focus_alt_panel() -> None:
    #     """Focus Claude Code using panel strategy."""
    #     user.vscode_rpc_command("jcaw.claudeCodeFocusPanel")

    # def claude_code_focus_alt_click() -> None:
    #     """Focus Claude Code using click strategy."""
    #     user.vscode_rpc_command("jcaw.claudeCodeFocusWithClick")

    # def claude_code_focus_alt_sidebar() -> None:
    #     """Focus Claude Code using sidebar strategy."""
    #     user.vscode_rpc_command("jcaw.claudeCodeFocusSidebar")

    def claude_code_blur() -> None:
        """Unfocus the Claude Code input box."""
        user.vscode_rpc_command("claude-vscode.blur")

    def claude_code_accept_changes() -> None:
        """Accept proposed changes from Claude Code."""
        user.vscode_rpc_command("claude-vscode.acceptProposedDiff")

    def claude_code_reject_changes() -> None:
        """Reject proposed changes from Claude Code."""
        user.vscode_rpc_command("claude-vscode.rejectProposedDiff")

    def claude_code_insert_mention() -> None:
        """Insert an @-mention reference in Claude Code."""
        user.vscode_rpc_command("claude-vscode.insertAtMention")

    def claude_code_show_logs() -> None:
        """Show Claude Code logs."""
        user.vscode_rpc_command("claude-vscode.showLogs")

    def claude_code_update() -> None:
        """Update the Claude Code extension."""
        user.vscode_rpc_command("claude-vscode.update")

    def claude_code_get_api() -> None:
        """Get Claude Code's exported API and copy to clipboard."""
        user.vscode_rpc_command("jcaw.getClaudeCodeApi")

    def claude_code_toggle_include_current_file() -> None:
        """Toggle including the current file in Claude Code context."""
        # HACK: Can't find a command for this, so manually tab to get it working.
        with actions.user.claude_code_temp_focus():
            key("tab:2")
            key("enter")


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
        actions.user.vscode_rpc_command("workbench.action.files.openFile")

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
        file_path = actions.app.path()
        cursor_pos = actions.user.vscode_rpc_command_get("jcaw.getCursorPosition")
        return DocumentPositionInfo(
            path=file_path,
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


@vscode_context.action_class("user")
class ClaudeCodeUserActions:
    def claude_code_focus_text_input() -> None:
        # Open Claude Code sidebar if not already visible
        # user.claude_code_open()
        # actions.sleep("400ms")
        
        # HACK: Claude Code VSCode extension doesn't work properly - the input 
        #   focussing command specifically is broken, and doesn't reliably take 
        #   focus. So, try to find the Claude input box using OCR.
        #
        #   The cost of this on my desktop setup is about 300ms, which is not 
        #   too bad.
        #
        #   With that said, I can seem to get around this by mentioning the 
        #   current file - but this will only work if a file is open.
        if actions.app.path() and False:
            # FIXME: Disabled for now because it's so unreliable on slow machines.
            user.claude_code_insert_mention()
            sleep("200ms")
            key("ctrl-a")
            key("backspace")
        else:
            start_time = time.perf_counter()
            user.ocr_click_in_window(r"(to focus or unfocus Claude|Queue another message)")
            ocr_duration_ms = (time.perf_counter() - start_time) * 1000
            # If OCR took more than 600ms, we're on a laggy PC, so we may need to wait 
            # for the text box to get focus. If we don't, we could select and erase 
            # the previously focussed document.
            if ocr_duration_ms > 600:
                sleep(f"{int(ocr_duration_ms / 2)}ms")
            else:
                sleep("300ms")
            key("escape")
            key("ctrl-a")
            key("backspace")

    def claude_code_pick_from_the_open_interface(model: str) -> None:
        if model == "haiku":
            actions.user.ocr_click_in_window("Haiku 4.5")
        elif model == "opus":
            actions.user.ocr_click_in_window("Opus 4.1")
        elif model == "sonnet":
            # There are two Sonnet 4.5 versions available in the VSCode extension as of
            # 12th November 2025 - one is a legacy model. This should only match the
            # default (up to date) one.
            actions.user.ocr_click_in_window("Sonnet 4.5")
        else:
            raise RuntimeError(f"Unknown model: {model}")
        
    def claude_code_temp_focus() -> Any:
        """Context manager to temporarily focus Claude Code input box."""
        return ClaudeCodeVSCodeTemporaryFocusContext()
    

vimfinity_bind_keys(
    {
        # "p" means "page-specific", or "app-specific" in this case
        "p": "VSCode",
        "p r": (user.vscode_restart_extension_host, "Restart extension host"),
        "p c": (user.vscode_get_all_commands, "Get all commands"),
        # Claude Code opening commands - experimental and kept commented out
        # "c s": (user.claude_code_open_sidebar, "Open Claude Code in sidebar"),
        # "c e": (user.claude_code_open_editor, "Open Claude Code in editor tab"),
        # "c w": (user.claude_code_open_window, "Open Claude Code in new window"),
        # "c t": (user.claude_code_open_terminal, "Open Claude Code in terminal"),
    },
    vscode_context,
)
