from talon import Module


module = Module()


@module.action_class
class ModuleActions:
    def talon_open_repl() -> None:
        """Open the interactive Talon REPL."""
        # Fragile import, make it local.
        from talon_plugins import menu

        menu.open_repl(None)

    def talon_open_user_dir() -> None:
        """Open the Talon user directory."""
        # Fragile import, make it local.
        from talon_plugins import menu

        menu.open_user(None)

    def talon_show_log() -> None:
        """Show (the tail of) the Talon log."""
        # Fragile import, make it local.
        from talon_plugins import menu

        menu.tail_log(None)
