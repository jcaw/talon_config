"""Map noises (pop, hiss) to actions with contextual behavior.

Based on the talonhub/community pattern. Define base actions here,
then override them in context-specific modules.
"""

from talon import Module, actions, cron, noise, settings

mod = Module()
_hiss_cron = None

mod.setting(
    "hiss_debounce_time",
    type=int,
    default=100,
    desc="Debounce time in ms - hiss must last this long to trigger",
)


@mod.action_class
class Actions:
    def on_pop():
        """Called when the user makes a pop noise.

        Override this in contexts to provide custom behavior.
        Default: do nothing.
        """
        actions.skip()

    def on_hiss(active: bool):
        """Called when the user makes a hiss noise.

        Args:
            active: True when hiss starts, False when it ends.

        Override this in contexts to provide custom behavior.
        Default: do nothing.
        """
        actions.skip()


def _on_hiss_debounce(active: bool):
    """Debounce hiss to avoid triggering during speech."""
    global _hiss_cron
    if active:
        debounce_ms = settings.get("user.hiss_debounce_time")
        _hiss_cron = cron.after(
            f"{debounce_ms}ms",
            lambda: actions.user.on_hiss(True),
        )
    else:
        if _hiss_cron:
            cron.cancel(_hiss_cron)
            _hiss_cron = None
        actions.user.on_hiss(False)


noise.register("pop", lambda _: actions.user.on_pop())
noise.register("hiss", _on_hiss_debounce)
