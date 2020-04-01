from talon import Context


hiss_context = Context()
hiss_context.matches = r"""
app: /emacs/
# Currently, the way Talon parses contexts means the basic context would
# override hiss-to-cancel too, so we manually exclude it.
user.zoom_mouse_zooming: False
"""


# Scrolling in Emacs is invasive - it doesn't just scroll, it moves the cursor.
# Hisses will misfire while speaking, so we add a deadzone to ignore short
# hisses.
hiss_context.settings["user.hiss_start_deadzone"] = 300
