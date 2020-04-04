import time

from talon import Module, actions

from user.utils import Modifiers

key = actions.key
user = actions.user


module = Module()


@module.action_class
class Actions:
    def slack_switch_room(number: int) -> None:
        """Switch to a numbered room."""
        with Modifiers(["ctrl"]):
            key("`")
            user.type_number(number)

    def slack_switch_channel() -> None:
        """Open the channel switching dialogue."""
        key("ctrl-j")
        # Sleep so the next action inputs into the dialogue
        time.sleep(0.1)

    def slack_search_channel(name_search: str) -> None:
        """Search for a channel to jump to."""
        actions.self.slack_switch_channel()
        actions.insert(name_search)

    def slack_messages() -> None:
        """Show slack messages."""

    def slack_threads() -> None:
        """Show slack threads."""

    def slack_history() -> None:
        """Show slack history."""

    def slack_activity() -> None:
        """Show slack activity."""

    def slack_directory() -> None:
        """Show slack directory."""

    def slack_starred_items() -> None:
        """Show starred items in Slack."""
