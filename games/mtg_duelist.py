from talon import Context, cron, actions


context = Context()
context.matches = r"""
app: mtg duelist
"""


def bind():
    try:
        actions.user.vimfinity_bind_keys(
            {
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
