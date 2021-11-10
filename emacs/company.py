from talon import Module, Context, actions

user = actions.user
emacs_command = actions.user.emacs_command
emacs_prefix_command = actions.user.emacs_prefix_command


module = Module()

context = Context()
context.matches = """
tag: user.emacs
user.emacs-minor-mode: company-mode
user.emacs-company-prompt-open: True
"""


@module.action_class
class ModuleActions:
    def emacs_company_highlight(number: int) -> None:
        """Move to a specific company candidate."""
        emacs_prefix_command("voicemacs-company-highlight", number)

    def emacs_company_complete(number: int) -> None:
        """Pick & complete a numbered company candidate."""
        # We don't use `voicemacs-company-complete` because it doesn't reliably
        # give visual feedback.
        # emacs_prefix_command("voicemacs-company-complete", number)
        user.emacs_company_highlight(number)
        # Sleep briefly to ensure there's visual feedback
        actions.sleep("100ms")
        user.emacs_command("company-complete")


@context.action_class("user")
class UserActions:
    def show_documentation():
        emacs_command("company-quickhelp-manual-begin")

    def opening_number_action(number: int) -> None:
        actions.self.emacs_company_complete(number)
