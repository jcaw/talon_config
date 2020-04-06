from talon import Module, actions

from user.emacs.utils import rpc


module = Module()


@module.action_class
class GlobalActions:
    def emacs_helm_goto_line(line_number: int):
        """Move to a specific line in the helm buffer."""
        # HACK: Technically it does change the state, but it doesn't mater if
        #   we do it multiple times.
        rpc.call("voicemacs-helm-goto-line", [line_number], changes_state=False)

    def emacs_helm_command(command_name: str, line_number: int = None) -> None:
        """Perform a Helm command, optionally on item ``number``.

        Pass ``number`` to jump to a number first. Leave it blank to perform the
        command at the current point.

        """
        if isinstance(line_number, int):
            actions.self.emacs_helm_goto_line(line_number)
        actions.self.emacs_command(command_name)
