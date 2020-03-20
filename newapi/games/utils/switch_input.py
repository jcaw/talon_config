"""This module is a stopgap to improve game compatibility.

Replaces Talon's native input within certain contexts.

"""


def switch_to_keyboard(context):
    """Switch to using the `keyboard` module for input in this context.

    Some games aren't registering Talon's input as of Windows beta 988 (for
    example, Europa Universalis IV). However, the PyPi `keyboard` module seems
    to work ok.

    """
    import keyboard

    @context.action_class("main")
    class MainActions:
        def key(key: str):
            keys = key.split("-")
            assert len(keys) > 0
            keyboard.press_and_release("+".join(keys))
