"""VSCode-specific Claude Code integration for Talon."""

from typing import Any, Optional
import time
from talon import Module, actions
from user.plugins.vimfinity.vimfinity import vimfinity_bind_keys
from user.apps.claude_code import ClaudeCodeTemporaryFocusContext
from user.apps.vscode import vscode_context


# Convenience mappings
user = actions.user
key = actions.key
insert = actions.insert
sleep = actions.sleep


module = Module()


class ClaudeCodeVSCodeTemporaryFocusContext(ClaudeCodeTemporaryFocusContext):
    def __init__(self, assume_focussed: bool = False):
        super().__init__(assume_focussed)

    def __enter__(self):
        if not self.assume_focussed:
            actions.user.claude_code_focus_text_input()
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        # VSCode uses blur to defocus instead of restoring window focus
        if not self.assume_focussed:
            actions.user.claude_code_blur()
        return False


THINKING_ICON_THRESHOLD = 0.99  # Very strict matching to distinguish on/off states

def claude_code_find_thinking_on_icon():
    """Find the thinking on icon in the Claude Code interface using image recognition.

    Returns the screen coordinates of the icon if found, None otherwise.
    """
    return actions.user.find_icon_in_window(
        "user/assets/icons/claude_code/thinking_on.png",
        threshold=THINKING_ICON_THRESHOLD
    )

def claude_code_find_thinking_off_icon():
    """Find the thinking off icon in the Claude Code interface using image recognition.

    Returns the screen coordinates of the icon if found, None otherwise.
    """
    return actions.user.find_icon_in_window(
        "user/assets/icons/claude_code/thinking_off.png",
        threshold=THINKING_ICON_THRESHOLD
    )


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

    def claude_code_blur() -> None:
        """Unfocus the Claude Code input box."""
        user.vscode_rpc_command("claude-vscode.blur")

    def claude_code_accept_changes() -> None:
        """Accept proposed changes from Claude Code."""
        user.vscode_rpc_command("claude-vscode.acceptProposedDiff")

    def claude_code_reject_changes() -> None:
        """Reject proposed changes from Claude Code."""
        user.vscode_rpc_command("claude-vscode.rejectProposedDiff")

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
            user.ocr_click_in_window(r"(to focus or unfocus Claude|Queue another message...)")
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

    def claude_code_temp_focus(assume_focussed: bool = False) -> Any:
        """Context manager to temporarily focus Claude Code input box.

        Args:
            assume_focussed: If True, assumes Claude Code is already focused and skips focus/restore
        """
        return ClaudeCodeVSCodeTemporaryFocusContext(assume_focussed)

    def claude_code_enable_thinking(assume_focussed: bool = False) -> None:
        """Enable thinking mode in Claude Code (VSCode-specific implementation)."""
        actions.user.claude_code_set_thinking(True, assume_focussed)

    def claude_code_disable_thinking(assume_focussed: bool = False) -> None:
        """Disable thinking mode in Claude Code (VSCode-specific implementation)."""
        actions.user.claude_code_set_thinking(False, assume_focussed)

    def claude_code_toggle_thinking(assume_focussed: bool = False) -> None:
        """Toggle thinking mode in Claude Code (VSCode-specific implementation)."""
        with actions.user.claude_code_temp_focus(assume_focussed):
            actions.sleep("100ms")

            # Try image detection first - look for either state of the thinking toggle
            coords = claude_code_find_thinking_on_icon()
            if not coords:
                coords = claude_code_find_thinking_off_icon()
            if not coords:
                raise RuntimeError("Could not find thinking toggle icon in Claude Code interface")
            # Click the icon we found
            actions.mouse_move(*coords)
            actions.sleep("100ms")
            actions.mouse_click()

    def claude_code_set_thinking(desired_state: Optional[bool], assume_focussed: bool = False) -> tuple[Optional[bool], Optional[bool]]:
        """VSCode-specific implementation: Switch thinking mode using icon detection.

        Args:
            desired_state: The desired thinking state (True/False), or None to skip switching
            assume_focussed: If True, assumes Claude Code is already focused

        Returns:
            Tuple of (original_state, new_state). Returns `(None, None)` if switching failed.
        """
        if desired_state is None:
            return None, None

        with actions.user.claude_code_temp_focus(assume_focussed):
            try:
                # Try to find both icons to determine current state
                on_coords = claude_code_find_thinking_on_icon()
                off_coords = claude_code_find_thinking_off_icon()

                # Determine current state based on which icon is visible
                if on_coords and not off_coords:
                    current_state = True
                elif off_coords and not on_coords:
                    current_state = False
                else:
                    # Can't determine state reliably (either both found or neither found)
                    print(f"Could not determine thinking state: on_coords={on_coords}, off_coords={off_coords}")
                    return None, None

                # Only switch if there's a divergence
                if current_state != desired_state:
                    # Re-use the coordinates we just found
                    coords_to_click = on_coords if current_state else off_coords
                    actions.mouse_move(*coords_to_click)
                    actions.sleep("100ms")
                    actions.mouse_click()
                    return current_state, desired_state
                else:
                    # Already in desired state, no need to switch
                    return current_state, current_state

            except Exception as e:
                print(f"Failed to switch thinking mode: {e}")
                return None, None

    def claude_code_insert_mention() -> None:
        user.vscode_rpc_command("claude-vscode.insertAtMention")


vimfinity_bind_keys(
    {
        # VSCode-specific Claude Code commands
        "c = u": (user.claude_code_update, "Update extension"),
        "c = ~": (user.claude_code_get_api, "Get API"),
        "c = a": (user.claude_code_accept_changes, "Accept changes"),
        "c = r": (user.claude_code_reject_changes, "Reject changes"),
        "c = s": (user.claude_code_open_sidebar, "Open in sidebar"),
        "c = e": (user.claude_code_open_editor, "Open in editor tab"),
        "c = w": (user.claude_code_open_window, "Open in new window"),
        "c = t": (user.claude_code_open_terminal, "Open terminal version"),
    },
    vscode_context,
)
