"""This module is a stopgap to improve game compatibility.

Replaces Talon's native input within certain contexts.

"""

import time


def switch_to_keyboard_module(context):
    """Switch to using the PyPI `keyboard` module for input in this context.

    Some games aren't registering Talon's input as of Windows beta 988 (for
    example, Europa Universalis IV). However, the PyPi `keyboard` module seems
    to work ok.

    """
    import keyboard

    @context.action_class("main")
    class MainActions:
        def key(key: str):
            # Naive method - this may not cover all keys.
            for individual_press in key.split(" "):
                keys = individual_press.split("-")
                keyboard.press_and_release("+".join(keys))
                # TODO: Integrate key settings, switch this delay
                time.sleep(0.02)
