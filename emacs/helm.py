from talon import Module, Context, actions, settings

from user.emacs.utils.voicemacs import rpc_call

emacs_command = actions.user.emacs_command


module = Module()
module.tag("emacs-helm-enabled", desc="Active when Helm is currently enabled.")


@module.action_class
class GlobalActions:
    def emacs_helm_goto_line(line_number: int):
        """Move to a specific line in the helm buffer."""
        rpc_call("voicemacs-helm-goto-line", [line_number])

    def emacs_helm_command(command_name: str, line_number: int = None) -> None:
        """Perform a Helm command, optionally on item ``number``.

        Pass ``number`` to jump to a number first. Leave it blank to perform the
        command at the current point.

        """
        if isinstance(line_number, int):
            actions.self.emacs_helm_goto_line(line_number)
        emacs_command(command_name)


context = Context()
context.matches = r"""
os: windows
os: linux
os: mac
tag: user.emacs
user.emacs-minor-mode: helm-mode
"""
context.tags = ["user.emacs-helm-enabled"]


@context.action_class("edit")
class EditActions:
    def find(text: str = None):
        text = text.lower()
        # Other fallbacks to add
        #
        # Doom
        if settings.get("user.is-spacemacs"):
            if text:
                # `swoop` can be slow to open on large documents because it initially
                # matches every line. It's much faster if text is provided up-front.
                rpc_call("voicemacs-helm-swoop", [text])
            else:
                emacs_command("helm-swoop")
        else:
            # TODO: Clean this up, the abstraction is wrong
            actions.user.emacs_fallbacks(
                ["+default/search-buffer", "swiper", "isearch",]
            )
            if text:
                actions.insert(text)
