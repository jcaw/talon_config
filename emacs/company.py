from talon import Module

from user.emacs.utils import rpc


module = Module()


@module.action_class
class Actions:
    def emacs_company_highlight(number: int) -> None:
        """Move to a specific company candidate."""
        rpc.call("voicemacs-company-highlight", [number])

    def emacs_company_complete(number: int) -> None:
        """Pick & complete a numbered company candidate."""
        rpc.call("voicemacs-company-complete", [number])

    def emacs_company_show_doc(number: int) -> None:
        """Pop doc for a specific company candidate."""
        rpc.call("voicemacs-company-pop-doc", [number])
