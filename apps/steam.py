import re

from talon import Module, Context, actions, clip, ctrl

key = actions.key


module = Module()


context = Context()
context.matches = r"""
app: /steam/
"""
context.tags = ["user.browser"]


@context.action_class("user")
class Actions:
    def browser_address_backup() -> str:
        with clip.capture() as c:
            # TODO: could replace the OCR approach with UI Automation. Steam
            #   supports it. But it's probably slower.

            # Assume it's the only result, and farthest to the top-left
            actions.user.ocr_click_in_window("https://")
        return c.text()
