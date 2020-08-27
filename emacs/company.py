from talon import Module, actions

user = actions.user
emacs_prefix_command = actions.user.emacs_prefix_command


module = Module()


@module.action_class
class Actions:
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

    def emacs_company_show_doc(number: int) -> None:
        """Pop doc for a specific company candidate."""
        emacs_prefix_command("voicemacs-company-pop-doc", number)
