from talon import actions, cron, Context

user = actions.user
edit = actions.edit


browser_context = Context()
browser_context.matches = r"""
tag: user.browser
"""

draft_context = Context()
draft_context.matches = r"""
tag: user.draft_window_showing
"""


def bind():
    user.key_sequence_register(
        {
            # Emacs muscle memory
            "enter": edit.save,
            ",": edit.cut,
            ".": edit.copy,
            "s": edit.find,
            "/": user.search,
            # Other
            "o": "Open",
            "d": user.draft_current_textbox,
            "D": "Draft Window",
            "D s": user.draft_show,
            "D d": user.draft_current_textbox,
            "m": "Mic",
            "m m": user.noisy_sleep,
            "m w": user.wake,
            "space": user.toggle_mic_off,
            "m space": user.toggle_mic_off,
        }
    )

    user.key_sequence_register(
        {
            "o c": user.open_current_page_in_chrome,
        },
        browser_context,
    )

    user.key_sequence_register(
        {
            # Hide all the base draft window commands
            "d": None,
            "D": None,
            "h": user.draft_hide,
            "f": user.draft_finish,
            "s": user.draft_finish_and_submit,
            "c": user.draft_cancel,
            "h": user.draft_hide,
        },
        draft_context,
    )


# HACK: Actions won't be registered on startup, so wait until they are.
cron.after("1ms", bind)
