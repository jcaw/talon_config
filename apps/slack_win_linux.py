from talon import Module, Context, actions


module = Module()


@module.action_class
class Actions:
    def slack_messages() -> None:
        """Go to messages in Slack."""

    def slack_threads() -> None:
        """Go to threads in Slack."""

    def slack_history() -> None:
        """Show history in Slack."""

    def slack_forward():
        """Go forward in Slack."""
        # TODO: Better docstring

    def slack_activity() -> None:
        """Go to activity in Slack."""

    def slack_directory() -> None:
        """TODO"""

    def slack_starred_items() -> None:
        """Go to starred items in Slack."""

    def slack_unread():
        """Go to unread items in Slack."""

    def next_unread_channel() -> None:
        """Go to the next unread channel in Slack (going down)."""

    def previous_unread_channel() -> None:
        """Go to the previous unread channel in Slack (going up)."""

    def slack_attach_snippet():
        """Attach a snippet to the current message in Slack."""

    # TODO: Extract all below. They're generic.

    def edit_last_message() -> None:
        """Edit the last message in a chat app."""

    def toggle_bullets():
        """Toggle bullet points in the current text editor."""

    def toggle_number_list():
        """Toggle a numbered list in the current text editor."""

    def toggle_quote():
        """Toggle a quoted passage in the current text editor."""

    def upload_file():
        """Upload a file to the current dialogue/message box."""

    def list_app_shortcuts():
        """List all shortcuts for the current app."""

    def toggle_bold():
        """Toggle the highlighted text to be bold in the current text editor."""

    def toggle_italic():
        """Toggle the highlighted text to be italic in the current text editor."""

    def toggle_strikethrough():
        """Toggle the highlighted text to be crossed out in the current text editor."""


context = Context()
context.matches = r"""
os: windows
os: linux
app: /slack/
"""


@context.action_class("user")
class SlackActions:
    def slack_messages() -> None:
        actions.key("ctrl-shift-k")

    def slack_threads() -> None:
        actions.key("ctrl-shift-t")

    def slack_history() -> None:
        actions.key("TODO")

    def slack_forward():
        actions.key("TODO")

    def slack_activity() -> None:
        actions.key("ctrl-shift-m")

    def slack_directory() -> None:
        actions.key("ctrl-shift-e")

    def slack_starred_items() -> None:
        actions.key("ctrl-shift-s")

    def slack_unread():
        actions.key("TODO maybe ctrl-j")

    def next_unread_channel() -> None:
        actions.key("alt-shift-down")

    def previous_unread_channel() -> None:
        actions.key("alt-shift-up")

    def slack_attach_snippet():
        actions.key("ctrl-shift-enter")

    def toggle_fullscreen():
        actions.key("ctrl-shift-f")

    def edit_last_message() -> None:
        actions.key("ctrl-up")

    def toggle_bullets():
        actions.key("ctrl-shift-8")

    def toggle_number_list():
        actions.key("ctrl-shift-7")

    def toggle_quote():
        actions.key("ctrl-shift->")

    def upload_file():
        actions.key("ctrl-u")

    def list_app_shortcuts():
        actions.key("ctrl-/")

    def toggle_bold():
        actions.key("ctrl-b")

    def toggle_italic():
        actions.key("ctrl-i")

    def toggle_strikethrough():
        actions.key("ctrl-shift-x")


@context.action_class("edit")
class EditActions:
    def search():
        actions.key("ctrl-j")
