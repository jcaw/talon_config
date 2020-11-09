from typing import Optional

from talon import Context

from user.emacs.utils.voicemacs import rpc_call
from user.utils.formatting import SurroundingText


context = Context()

context.matches = r"""
tag: user.emacs
"""


@context.action_class("self")
class UserActions:
    def surrounding_text() -> Optional[SurroundingText]:
        # TODO: If the voicemacs server is inactive, return nothing.
        raw_info = rpc_call(
            "voicemacs-surrounding-text",
            [":chars-before", 30000, ":chars-after", 30000],
            # Use a very long timeout
            timeout=10,
        )
        return SurroundingText(
            text_before=raw_info["text-before"], text_after=raw_info["text-after"]
        )
