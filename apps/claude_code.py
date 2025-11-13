"""Claude Code integration for Talon Voice using vimfinity prefix bindings."""

from typing import Optional, Any

from talon import Module, Context, actions, ui
from user.plugins.vimfinity.vimfinity import vimfinity_bind_keys
from user.misc import ocr


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
    """Context manager that focuses Claude Code and restores focus on exit."""

    def __init__(self):
        self.original_window = None

    def __enter__(self):
        self.original_window = ui.active_window()
        actions.user.claude_code_focus_text_input()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.original_window:
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
        
    def claude_code_submit_to_claude(text: str, model: Optional[str] = None) -> None:
        """Submit text to the most recent active Claude Code instance for this project."""
        text = text.strip()
        with actions.user.claude_code_temp_focus():
            if model:
                actions.user.claude_code_set_model(model, assume_focussed=True)
            actions.sleep("100ms")
            if text.startswith("/"):
                # Commands should be entered directly so they trigger command detection
                actions.insert(text)
            else:
                # Otherwise, we paste insert to avoid issues with newlines and long prompts
                actions.user.paste_insert(text)
            actions.key("enter")

    # HACK: Require `Any` so we can return subclasses of ClaudeCodeTemporaryFocusContext.
    def claude_code_temp_focus() -> Any:
        """Context manager to temporarily focus Claude Code input box."""
        return ClaudeCodeTemporaryFocusContext()
    
    def claude_code_compact(model: Optional[str] = None) -> None:
        """Send 'Make the response more compact' prompt to Claude Code."""
        actions.user.claude_code_submit_to_claude("/compact", model)

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
        actions.user.claude_code_submit_to_claude(prompt, model)

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
        actions.user.claude_code_submit_to_claude(prompt, model)

    def claude_code_fix_until_tests_pass(model: Optional[str] = None) -> None:
        """Submit request to Claude to repeatedly fix tests until they all pass."""
        prompt = "Repeatedly fix tests until they all pass. Run the tests as the final step before assuming they pass."
        actions.user.claude_code_submit_to_claude(prompt, model)

    def claude_code_submit_continue(model: Optional[str] = None) -> None:
        """Tell Claude Code to continue with what it was doing."""
        actions.user.claude_code_submit_to_claude("Continue", model)

    def claude_code_toggle_thinking(assume_focussed: bool = False) -> None:
        """Toggle thinking mode in Claude Code."""
        if assume_focussed:
            raise NotImplementedError("skipping focus not implemented for claude_code_toggle_thinking")
        with actions.user.claude_code_temp_focus():
            actions.sleep("100ms")
            # Navigate to the thinking toggle
            actions.key("tab:3")
            actions.sleep("100ms")
            # Toggle it
            actions.key("enter")
            actions.sleep("100ms")
            # Navigate back to the text input
            actions.key("shift-tab:3")


# VSCode-specific Claude Code vimfinity bindings
vimfinity_bind_keys(
    {
        "c": "Claude Code",
        "c o": (user.claude_code_open, "Open Claude Code"),
        "c c": (user.claude_code_focus_text_input, "Focus text input"),
        # TODO: Move to VSCode module for now.
        "c a": (user.claude_code_accept_changes, "Accept changes"),
        "c r": (user.claude_code_reject_changes, "Reject changes"),
        "c m": (user.claude_code_insert_mention, "Mention file"),
        # TODO: Consider moving to VSCode module.
        "c l": (user.claude_code_show_logs, "Show logs"),
        "c u": (user.claude_code_update, "Update extension"),
        "c g": (user.claude_code_get_api, "Get API"),
        "c p": (user.claude_code_set_bypass_permissions, "Set to bypass permissions"),
        "c i": (user.claude_code_implement_todo_at_cursor, "Implement TODO at cursor"),
        # TODO: Move these two to a claude file in `settings`
        "c b": (user.claude_code_fix_until_builds, "Fix problems until build succeeds"),
        "c t": (user.claude_code_fix_until_tests_pass, "Fix tests until they all pass"),
        "c e": (user.claude_code_toggle_thinking, "Toggle thinking mode"),
        # TODO: actions that combine switching model and thinking mode into one action. Be efficient too. Bind to the capitalised version, I guess. Switch model first, before the thinking mode.
        "c h": (lambda: user.claude_code_set_model("haiku"), "Switch to Haiku model"),
        "c s": (lambda: user.claude_code_set_model("sonnet"), "Switch to Sonnet model"),
    },
    code_editor_context,
)