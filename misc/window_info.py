from talon.voice import Context
from talon import ui, app, clip


ctx = Context("config_help")


def _clip_copy(message, thing):
    """Put something on the clipboard and notify the user."""
    message = message.format(thing)
    clip.set(thing)
    app.notify(title="Copied to Clipboard", body=message, sound=False)
    print(message)


def copy_current_bundle(m=None):
    _clip_copy('Current bundle: "{}"', ui.active_app().bundle)


def copy_current_exe(m=None):
    _clip_copy('Current exe: "{}"', ui.active_app().exe)


def copy_current_title(m=None):
    _clip_copy('Current title: "{}"', ui.active_window().title)


def copy_current_app_info(m=None):
    """Copy all info for the current app."""
    active_app = ui.active_app()
    info_pieces = [
        'Bundle: "{}"'.format(active_app.bundle),
        'Exe:    "{}"'.format(active_app.exe),
        'Title:  "{}"'.format(ui.active_window().title),
    ]
    info = "\n".join(info_pieces)
    _clip_copy("All info for current app:\n{}", info)


ctx.keymap(
    {
        "[copy] current bundle": copy_current_bundle,
        "[copy] current (exe | executable)": copy_current_exe,
        "[copy] current title": copy_current_title,
        "[copy] current app": copy_current_app_info,
    }
)
