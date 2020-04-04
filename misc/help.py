from talon import Module, Context, registry, clip, ui

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
        print("Recognition working!")
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