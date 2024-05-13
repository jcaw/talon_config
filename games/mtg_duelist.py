"""Module to assist playing Magic The Gathering: Duelist."""

from talon import Context, cron, actions


context = Context()
context.matches = r"""
app: mtg duelist
"""


def bind():
    try:
        actions.user.vimfinity_bind_keys(
            {
                # Middle mouse button flips cards, but it doesn't register
                # unless the mouse is moved a bit, so add an explicit action to
                # do that. Also just binds middle click which helps when using a
                # trackball without a middle mouse button.
                "backspace": (
                    lambda: actions.user.shake_click(button=2),
                    "Middle Click/Flip Card",
                )
            },
            context=context,
        )
    except KeyError:
        print("Failed to bind MTG Duelist shortcuts. Retrying in 1s.")
        cron.after("1s", bind)


cron.after("1s", bind)
