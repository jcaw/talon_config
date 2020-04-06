from talon import Module, actions

from user.emacs.utils import rpc


module = Module()


@module.action_class
class Actions:
    def emacs_dired_highlight(number: int) -> None:
        """Move cursor to a Dired candidate by number."""
        # HACK: Technically it does change the state, but it doesn't mater if
        #   we do it multiple times.
        rpc.call("voicemacs-dired-move-to-item", [number], changes_state=False)

    def emacs_dired_command(command_name: str, number: int = None) -> None:
        """Perform a Dired command, optionally on item ``number``.

        Pass ``number`` to jump to a number first. Leave it blank to perform the
        command at the current point.

        """
        if isinstance(number, int):
            actions.self.emacs_dired_highlight(number)
        actions.user.emacs_command(command_name)
