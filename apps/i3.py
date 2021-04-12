import subprocess
import platform
import shutil

from talon import Module, Context


module = Module()
module.tag("i3", "Active when i3 is the window manager (Linux only).")

if platform.system() == "Linux" and shutil.which("xprop"):
    # Sketchy method. i3 doesn't provide something better?
    result = subprocess.run(["xprop", "-root"], capture_output=True)
    if '"i3"' in result.stdout.decode("utf-8"):
        i3_context = Context()
        i3_context.tags = ["user.i3"]


i3_context = Context()
i3_context.matches = """
tag: user.i3
"""

# @i3_context.action_class("user")
# class i3Actions():
#     def snap_window(snap_keys: str) -> None:
#         key("win-shift:down")
#         try:
#             for keyname in snap_keys.split():
#                 key(keyname)
#         finally:
#             key("win-shift:up")
