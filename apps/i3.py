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
