from talon import Module, Context, actions

key = actions.key


module = Module()
module.tag("firefox", "Enabled when firefox is in focus.")


context = Context()
context.matches = r"""
app: /firefox/
"""
context.tags = ["user.firefox"]


@module.action_class
class Action:
    def rango_toggle_keyboard_clicking():
        """Rango browser extension - toggle keyboard clicking on/off."""
        key("ctrl-shift-5")

    def rango_disable():
        """Disable Rango browser extension and stop showing labels."""
        key("ctrl-shift-4")

    def rango_enable():
        """Enable Rango browser extension and start showing labels."""
        key("ctrl-shift-6")

    # TODO: Read aloud


# TODO: Vimfinity shortcuts for rango and read aloud.
