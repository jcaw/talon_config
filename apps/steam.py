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
            results = actions.self.ocr_find_text_in_window(re.escape("https://"))
            if not results:
                raise RuntimeError('Could not find "https://" via OCR.')
            # Assume it's the only result, and farthest to the top-left
            original_position = ctrl.mouse_pos()

            actions.mouse_move(*results[0].rect.center)
            actions.mouse_click(button=0)
            actions.mouse_move(*original_position)
        return c.text()
