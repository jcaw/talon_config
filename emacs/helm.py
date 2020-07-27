from talon import Module, Context, actions

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


context = Context()
context.matches = r"""
os: windows
os: linux
os: mac
tag: emacs
user.emacs-minor-mode: helm-mode
"""


@context.action_class("edit")
class EditActions:
    def find(text: str = None):
        if text:
            # `swoop` can be slow to open on large documents because it initially
            # matches every line. It's much faster if text is provided up-front.
            rpc.call("voicemacs-helm-swoop", [text])
        else:
            emacs_command["helm-swoop"]
