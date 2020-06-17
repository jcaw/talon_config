from talon import Module, actions

from user.utils import Modifiers

user = actions.user

module = Module()


@module.action_class
class Action:
    def next_channel() -> None:
        """Go to the next chat channel."""

    def previous_channel() -> None:
        """Go to the previous chat channel."""

    def next_unread_channel() -> None:
        """Go to the next unread chat channel."""

    def previous_unread_channel() -> None:
        """Go to the previous unread chat channel."""

    # TODO: Extract from here
    def code_block() -> None:
        """Insert a code block."""
        actions.insert("```")
        actions.key("shift-enter:2")
        actions.insert("```")
        actions.key("up")

    def edit_last_message() -> None:
        """Edit the last submitted message."""

    def chat_unread() -> None:
        """Show unread items in a chat program."""

    def mark_all_channels_read() -> None:
        """Mark all messages read."""

    def mark_channel_read() -> None:
        """Mark one channel as read."""

    def discord_switch_server(number: int) -> None:
        """Switch to a numbered server in Discord."""
        with Modifiers(["ctrl"]):
            user.type_number(number)
