from talon import Module, Context, registry, clip, ui, actions

from user.utils import sound


module = Module()
context = Context()


def _action_declarations():
    """Generate all defined actions, as strings."""
    for decl in registry.decls.actions.values():
        yield str(decl)


def _capture_declarations():
    # TODO: Switch this back to values once the upstream issue is fixed in Talon
    # for decl in registry.decls.captures.values():
    for decl in registry.decls.captures.keys():
        yield str(decl)


def _print_and_copy(string):
    print(string)
    clip.set(string)
    print("String copied to clipboard.")


@module.action_class
class Actions:
    def print_copy_actions() -> None:
        """Print & copy all declared actions."""
        _print_and_copy("\n".join(_action_declarations()))

    def print_copy_captures() -> None:
        """Print & copy all declared captures."""
        _print_and_copy("\n".join(_capture_declarations()))

    def mic_test() -> None:
        """Test recognition. Prints and plays a sound when successful."""
        print("Mic check: recognition working!")
        actions.app.notify("Recognition working.", "Mic Check")
        sound.play(sound.GLASS_TAP)
        # TODO: Ping short notification

    def copy_current_app_info() -> None:
        """Copy all info for the current app."""
        active_app = ui.active_app()
        info = "\n".join(
            [
                'Bundle: "{}"'.format(active_app.bundle),
                'Exe:    "{}"'.format(active_app.exe),
                'Title:  "{}"'.format(ui.active_window().title),
            ]
        )
        _print_and_copy(info)

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
