"""Claude Code integration for Talon Voice using vimfinity prefix bindings."""

from typing import Optional, Any

from talon import Module, Context, actions, ui
from user.plugins.vimfinity.vimfinity import vimfinity_bind_keys
from user.misc import ocr


# Whether to use thinking when temporarily switching to a model.
# Used by claude_code_submit_to_claude when restore_model=True.
TEMP_USE_THINKING = {
    "haiku": False,
    "sonnet": True,
    "opus": True,
}


module = Module()
code_editor_context = Context()
code_editor_context.matches = r"""
tag: user.code_editor
"""

user = actions.user

# We mirror the currently active claude code model (per window) to avoid 
# unnecessary switching.
current_model = None


class ClaudeCodeTemporaryFocusContext:
    def __init__(self, assume_focussed: bool = False):
        self.assume_focussed = assume_focussed
        self.original_window = None

    def __enter__(self):
        if not self.assume_focussed:
            self.original_window = ui.active_window()
            actions.user.claude_code_focus_text_input()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.assume_focussed and self.original_window:
            self.original_window.focus()
        return False




@module.action_class
class ClaudeCodeActions:
    def claude_code_open() -> None:
        """Open (or focus) Claude Code. (TODO: just for this project?)"""

    def claude_code_focus_text_input() -> None:
        """Focus the Claude Code text input box."""
        print("Focusing Claude Code text input box using generic context.")
        # The default version of this action should focus a terminal running Claude Code.
        #
        # Let's just assume by focussing Claude Code, the text input will be focussed.
        user.claude_code_open()
        actions.sleep("200ms")
        # Press escape twice just in case - this will clear the input box and exit dialogues.
        actions.key("escape:2")

    def claude_code_insert_mention() -> None:
        """Insert an @-mention reference in the Claude Code prompt."""
        # TODO: Terminal implementation of file mentioning

    def claude_code_set_model(model: str, assume_focussed: bool = False, force: bool = False) -> None:
        """Set the Claude Code model."""
        global current_model
        VALID_MODELS = ["sonnet", "opus", "haiku"]

        model = model.lower()
        assert model.lower() in VALID_MODELS, f"Unknown model: {model}, must be one of: {VALID_MODELS}"

        if not assume_focussed:
            actions.user.claude_code_focus_text_input()
            actions.sleep("100ms")
        if current_model != model or force:
            actions.insert("/model")
            actions.sleep("100ms")
            actions.key("enter")
            actions.sleep("200ms")
            actions.self.claude_code_pick_from_the_open_interface(model)
            current_model = model
            actions.sleep("100ms")
            actions.key("enter")
    
    def claude_code_pick_from_the_open_interface(model: str) -> None:
        """Pick the actual model from a list of models.

        This basically just depends on the interface. Assumes the model has already been validated.

        """
        # In the terminal, we can select models with numbers. Assume by 
        # default we're in the terminal.
        # 
        # Note these numbers are based on behaviour as of 12th December 2025.
        if model == "haiku":
            actions.key("3")
        elif model == "opus":
            actions.key("2")
        elif model == "sonnet":
            actions.key("1")
    
    def claude_code_submit_to_claude(text: str, model: Optional[str] = None, restore_model: bool = False) -> None:
        """Submit text to the most recent active Claude Code instance for this project.

        If restore_model is True, saves the current model before switching and restores 
        it after submission. Thinking will also teporarily be set based on the setting
        in TEMP_USE_THINKING.

        """
        global current_model
        text = text.strip()
        model = model.lower() if model else None
        original_model = current_model
        original_thinking_state, new_thinking_state = None, None

        with actions.user.claude_code_temp_focus():
            if model:
                use_thinking = TEMP_USE_THINKING.get(model, None)
                original_thinking_state, new_thinking_state = actions.user.claude_code_set_thinking(use_thinking, assume_focussed=True)
                actions.sleep("200ms")
                if model != current_model:
                    actions.user.claude_code_set_model(model, assume_focussed=True)
            
            actions.sleep("100ms")
            if text.startswith("/"):
                # Commands should be entered directly so they trigger command detection
                actions.insert(text)
            else:
                # Otherwise, we paste insert to avoid issues with newlines and long prompts
                actions.user.paste_insert(text)
            actions.key("enter")
            actions.sleep("100ms")

            if restore_model and current_model != original_model:
                # Restore thinking state if we changed it
                if original_thinking_state and original_thinking_state != new_thinking_state:
                    if original_thinking_state:
                        actions.user.claude_code_enable_thinking(assume_focussed=True)
                    else:
                        actions.user.claude_code_disable_thinking(assume_focussed=True)
                    actions.sleep("200ms")
                actions.user.claude_code_set_model(original_model or "sonnet")
                actions.sleep("100ms")

    # HACK: Require `Any` so we can return subclasses of ClaudeCodeTemporaryFocusContext.
    def claude_code_temp_focus(assume_focussed: bool = False) -> Any:
        """Context manager to temporarily focus Claude Code input box.

        Args:
            assume_focussed: If True, assumes Claude Code is already focused and skips focus/restore
        """
        return ClaudeCodeTemporaryFocusContext(assume_focussed)
    
    def claude_code_compact(model: Optional[str] = None) -> None:
        """Send 'Make the response more compact' prompt to Claude Code."""
        actions.user.claude_code_submit_to_claude("/compact", model, restore_model=True)

    def claude_code_implement_todo_at_cursor(model: Optional[str] = None) -> None:
        """Submit request to Claude to implement the TODO at the current cursor position."""
        actions.edit.save()
        pos = actions.user.document_position()
        # Use the standard file_path:line_number format that Claude uses
        location = f"{pos.path}:{pos.line_number}"
        prompt = f"""
Implement the TODO at {location}

If there is no TODO at the exact location specified, I've made a mistake - in that case, do nothing.
"""
        actions.user.claude_code_submit_to_claude(prompt, model, restore_model=True)

    def claude_code_set_bypass_permissions() -> None:
        """Set Claude Code to bypass file permissions."""
        # It's lowercase in the terminal, uppercase in VSCode.
        BYPASS_TEXT = "» [bB]ypass permissions"
        with actions.user.claude_code_temp_focus():
        # HACK: Just use OCR to find the bypass permissions text
            try:
                actions.user.ocr_find_text_in_window(BYPASS_TEXT)
                print("Bypass permissions text detected - assuming it's already enabled.")
            except ocr.TextNotFoundError:
                # There's a max of 4 modes - if we haven't found it after 3 changes, 
                # then this approach has failed.
                for i in range(3):
                    actions.key("shift-tab")
                    actions.sleep("100ms")
                    try:
                        actions.user.ocr_find_text_in_window(BYPASS_TEXT)
                        return
                    except ocr.TextNotFoundError:
                        pass
                raise RuntimeError("Could not find bypass permissions option. Is `--dangerously-skip-permissions` enabled?")

    def claude_code_fix_until_builds(model: Optional[str] = None) -> None:
        """Submit request to Claude to fix problems repeatedly until the build succeeds."""
        prompt = "Fix problems repeatedly until the project builds successfully. Run the build as the final step before assuming it is successful."
        actions.user.claude_code_submit_to_claude(prompt, model, restore_model=True)

    def claude_code_fix_until_tests_pass(model: Optional[str] = None) -> None:
        """Submit request to Claude to repeatedly fix tests until they all pass."""
        prompt = "Repeatedly fix tests until they all pass. Run the tests as the final step before assuming they pass."
        actions.user.claude_code_submit_to_claude(prompt, model, restore_model=True)

    def claude_code_submit_continue(model: Optional[str] = None) -> None:
        """Tell Claude Code to continue with what it was doing."""
        actions.user.claude_code_submit_to_claude("Continue", model, restore_model=True)

    def claude_code_enable_thinking(assume_focussed: bool = False) -> None:
        """Enable thinking mode in Claude Code."""
        actions.user.claude_code_set_thinking(True, assume_focussed)

    def claude_code_disable_thinking(assume_focussed: bool = False) -> None:
        """Disable thinking mode in Claude Code."""
        actions.user.claude_code_set_thinking(False, assume_focussed)

    def claude_code_toggle_thinking(assume_focussed: bool = False) -> None:
        """Toggle thinking mode in Claude Code. Implementation is editor-specific."""
        with actions.user.claude_code_temp_focus(assume_focussed):
            # Tab toggles thinking in the terminal version of Claude Code.
            actions.key("tab")

    def claude_code_set_thinking(desired_state: Optional[bool], assume_focussed: bool = False) -> tuple[Optional[bool], Optional[bool]]:
        """Switch thinking mode to the desired state if specified.

        Args:
            desired_state: The desired thinking state (True/False), or None to skip switching
            assume_focussed: If True, assumes Claude Code is already focused

        Returns:
            Tuple of (original_state, new_state). Returns `(None, desired_state)` since we
            can't reliably detect the original state in terminal mode.
        """
        if desired_state is None:
            return None, None

        with actions.user.claude_code_temp_focus(assume_focussed):
            # Get all OCR results for the window once, then filter multiple times. More efficient.
            all_text_results = actions.user.ocr_get_all_text_in_window()

            # Check which thinking state text is present
            THINKING_ON_TEXT = "Thinking on (tab to toggle)"
            THINKING_OFF_TEXT = "Thinking off (tab to toggle)"
            thinking_on_found = any(THINKING_ON_TEXT.lower() in text.lower() for text in all_text_results)
            thinking_off_found = any(THINKING_OFF_TEXT.lower() in text.lower() for text in all_text_results)

            if thinking_on_found and not thinking_off_found:
                current_state = True
            elif thinking_off_found and not thinking_on_found:
                current_state = False
            else:
                print(f"Could not determine thinking state: on={thinking_on_found}, off={thinking_off_found}")
                return None, None
            
            if current_state != desired_state:
                actions.key("tab")
                actions.sleep("200ms")
                return current_state, desired_state

    def claude_code_set_model_and_thinking(model: str) -> None:
        """Set model and enable thinking mode efficiently in one focused context."""
        with actions.user.claude_code_temp_focus():
            # Switch model first
            actions.user.claude_code_set_model(model, assume_focussed=True)
            actions.sleep("1000ms")
            # Then enable thinking
            actions.user.claude_code_enable_thinking(assume_focussed=True)


HAIKU = "haiku"
SONNET = "sonnet"

# VSCode-specific Claude Code vimfinity bindings
vimfinity_bind_keys(
    {
        "c": "Claude Code",
        "c .": "Perform with Haiku",
        "c ,": "Perform with Sonnet",
        "c =": "Editor-specific",
        # General actions
        "c o": (user.claude_code_open, "Open Claude Code"),
        "c c": (user.claude_code_focus_text_input, "Focus text input"),
        # TODO: Consider moving to VSCode module.
        "c l": (user.claude_code_show_logs, "Show logs"),
        "c m": (user.claude_code_insert_mention, "Mention file"),
        "c p": (user.claude_code_set_bypass_permissions, "Set to bypass permissions"),
        "c e": (user.claude_code_toggle_thinking, "Toggle thinking mode"),
        # TODO: Figure out how to handle thinking with these switches.
        "c h": (lambda: user.claude_code_set_model(HAIKU), "Switch to Haiku"),
        "c H": (lambda: user.claude_code_set_model_and_thinking(HAIKU), "Switch to Haiku/thinking"),
        "c s": (lambda: user.claude_code_set_model(SONNET), "Switch to Sonnet"),
        "c S": (lambda: user.claude_code_set_model_and_thinking(SONNET), "Switch to Sonnet/thinking"),
        # Message dispatching actions
        "c i": (user.claude_code_implement_todo_at_cursor, "Implement TODO at cursor"),
        "c . i": (lambda: user.claude_code_implement_todo_at_cursor(HAIKU), "Implement TODO at cursor"),
        "c , i": (lambda: user.claude_code_implement_todo_at_cursor(SONNET), "Implement TODO at cursor"),
        "c n": (user.claude_code_submit_continue, "Continue"),
        "c . n": (lambda: user.claude_code_submit_continue(HAIKU), "Continue"),
        "c , n": (lambda: user.claude_code_submit_continue(SONNET), "Continue"),
        "c r": (user.claude_code_compact, "Compact (reduce)"),
        "c . r": (lambda: user.claude_code_compact(HAIKU), "Compact (reduce)"),
        "c , r": (lambda: user.claude_code_compact(SONNET), "Compact (reduce)"),
    },
    code_editor_context,
)
