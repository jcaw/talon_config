import emacs_porthole as porthole

from talon import Context

from user.emacs.utils import rpc
from user.utils.formatting import SurroundingText


context = Context()

context.matches = r"""
app: /emacs/
"""


@context.action_class
class UserActions:
    def surrounding_text() -> SurroundingText:
        try:
            raw_info = rpc.call(
                "voicemacs-surrounding-text",
                [":chars-before", 30000, ":chars-after", 30000],
                # Use a very long timeout
                timeout=10,
                changes_state=False,
            )
        except porthole.PortholeConnectionError:
            return None
        return SurroundingText(
            text_before=raw_info["text-before"], text_after=raw_info["text-after"]
        )
