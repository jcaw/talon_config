from talon import Module, actions


module = Module()


@module.action_class
class Actions:
    def magit_mark_lines(number: int) -> None:
        """Mark a specific number of lines in magit."""
        actions.user.emacs_command("set-mark-command")
        # This will actually mark (number + 1) lines, but it means we can read
        # directly off the relative line numbers.
        actions.key("down:{}".format(number))
