# TODO: Binding to turn off capslock. Maybe even make it automatic?

from talon import Module, Context, actions, ui, cron, app

ON_WINDOWS = app.platform == "windows"
if ON_WINDOWS:
    import ctypes


user = actions.user
key = actions.key
sleep = actions.sleep


module = Module()
windows_context = Context()


@module.action_class
class Actions:
    def vimfinity_disable_capslock_windows():
        """Disable backspace by focussing the talon log then pressing backspace."""

    def vimfinity_disable_capslock_if_enabled():
        """Disables Caps Lock even if it's bound by Talon or another app."""


@windows_context.action_class("self")
class WindowsActions:
    def vimfinity_disable_capslock_windows():
        with actions.user.automator_overlay("Automatically Disabling CapsLock"):
            initial_window = ui.active_window()
            # When Caps Lock is pressed in the Talon log, it will register and open
            # the Vimfinity menu, but it will also actually trigger Caps Lock
            # because the key cannot be perfectly intercepted in all situations. We
            # can leverage that to disable the CapsLock without actually changing
            # the state of capitalization.
            new_instance = user.open_talon_log()
            if new_instance:
                # Give it a while to open
                sleep("1000ms")
            else:
                sleep("100ms")
            key("capslock")
            sleep("200ms")
            # Even though Caps Lock fires default behaviour, it will also open the
            # Vimfinity prompt. Press escape again to close it.
            key("esc")
            if new_instance:
                key("alt-f4")
            initial_window.focus()

    def vimfinity_disable_capslock_if_enabled():
        caps_lock_enabled = ctypes.windll.user32.GetKeyState(0x14) & 0xFFFF != 0
        if caps_lock_enabled and not actions.user.vimfinity_is_active():
            print(
                "[vimfinity_capslock_fix]: CapsLock detected as enabled - automatically disabling."
            )
            actions.self.vimfinity_disable_capslock_windows()


if ON_WINDOWS:
    # TODO: For now, try forcing Caps Lock to be automatically disabled. The UI
    #  automation taking incomplete control may cause a problem here, so disable
    #  this if it causes problems.
    cron.interval("100ms", actions.self.vimfinity_disable_capslock_if_enabled)


def bind():
    try:
        actions.user.vimfinity_bind_keys(
            {
                "= backspace": (
                    actions.user.vimfinity_disable_capslock_windows,
                    "Disable Caps Lock",
                )
            },
            context=windows_context,
        )
    except KeyError:
        print("Failed to bind capslock key sequence. Retrying in 1s.")
        cron.after("1s", bind)


cron.after("100ms", bind)
