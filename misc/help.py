from typing import List

from talon import Module, Context, registry, clip, ui, actions

from user.utils import sound


module = Module()
context = Context()


def _print_and_copy_lines(lines: List):
    string = "\n".join(map(str, lines))
    print(string)
    clip.set_text(string)
    print("String copied to clipboard.")


@module.action_class
class Actions:
    def print_copy_actions() -> None:
        """Print & copy all declared actions."""
        _print_and_copy_lines(registry.decls.actions.values())

    def print_copy_captures() -> None:
        """Print & copy all declared captures."""
        # TODO: Switch this back to values once the upstream issue is fixed in Talon
        _print_and_copy_lines(registry.decls.captures.keys())

    def print_copy_settings() -> None:
        """Print & copy all declared settings."""
        _print_and_copy_lines(registry.decls.settings.values())

    def mic_test() -> None:
        """Test recognition. Prints and plays a sound when successful."""
        print("Mic check: recognition working!")
        actions.app.notify("Recognition working.", "Mic Check")
        sound.play(sound.GLASS_TAP)
        # TODO: Ping short notification

    def copy_current_app_info() -> None:
        """Copy all info for the current app."""
        active_app = ui.active_app()
        info = [
            'Bundle: "{}"'.format(active_app.bundle),
            'Exe:    "{}"'.format(active_app.exe),
            'Title:  "{}"'.format(ui.active_window().title),
        ]
        _print_and_copy_lines(info)
