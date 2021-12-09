from talon import Module, Context, actions, settings

from user.emacs.utils.voicemacs import rpc_call

emacs_command = actions.user.emacs_command


module = Module()
module.tag("emacs-helm-enabled", desc="Active when Helm is currently enabled.")


@module.action_class
class GlobalActions:
    def emacs_helm_goto_line(line_number: int):
        """Move to a specific line in the helm buffer.

        Pass `0` in order to avoid moving.

        """
        if line_number:
            rpc_call("voicemacs-helm-goto-line", [line_number])

    def emacs_helm_command(command_name: str, line_number: int = None) -> None:
        """Perform a Helm command, optionally on item ``number``.

        Pass ``number`` to jump to a number first. Leave it blank to perform the
        command at the current point.

        """
        if isinstance(line_number, int):
            actions.self.emacs_helm_goto_line(line_number)
        emacs_command(command_name)


helm_available_context = Context()
helm_available_context.matches = r"""
os: windows
os: linux
os: mac
tag: user.emacs
user.emacs-minor-mode: helm-mode
"""
# TODO: Remove, uneeded
helm_available_context.tags = ["user.emacs-helm-enabled"]


@helm_available_context.action_class("edit")
class EditActions:
    def find(text: str = None):
        if text:
            text = text.lower()
            # `swoop` can be slow to open on large documents because it initially
            # matches every line. It's much faster if text is provided up-front.
            rpc_call("voicemacs-helm-swoop", [text])
        else:
            emacs_command("helm-swoop")

        # Fallbacks
        #
        # # TODO: Clean this up, the abstraction is wrong
        # actions.user.emacs_fallbacks(
        #     [
        #         "+default/search-buffer",
        #         "swiper",
        #         "isearch",
        #     ]
        # )
        # if text:
        #     actions.insert(text)


in_prompt_context = Context()
in_prompt_context.matches = r"""
tag: user.emacs
user.emacs-in-helm-prompt: True
"""


@in_prompt_context.action_class("user")
class UserActions:
    def opening_number_action(number: int) -> None:
        actions.self.emacs_helm_command("helm-confirm-and-exit-minibuffer", number)
