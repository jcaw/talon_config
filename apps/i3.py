import subprocess
import platform
import shutil

from talon import Module, Context, actions, app


key = actions.key
sleep = actions.sleep


module = Module()
module.tag("i3", "Active when i3 is the window manager (Linux only).")

if platform.system() == "Linux" and shutil.which("xprop"):
    # Sketchy method. i3 doesn't provide something better?
    result = subprocess.run(["xprop", "-root"], capture_output=True)
    if '"i3"' in result.stdout.decode("utf-8"):
        i3_context = Context()
        i3_context.tags = ["user.i3", "user.tiling_window_manager"]

        # HOTFIX: Talon doesn't update parts of the i3 context until first
        #   window switch, so force it.
        #
        # TODO 1: Test if this is still an issue, vaguely remember it being
        #   fixed upstream.
        def _force_window_switch():
            actions.key("alt-tab")
            actions.key("alt-shift-tab")

        # Delay it so it fires after Talon grabs its own context (this also
        # ensures actions.key is already registered).
        app.register("launch", _force_window_switch)


i3_context = Context()
i3_context.matches = """
tag: user.i3
# Narrow with Linux to increase priority over just using the tag
os: linux
"""


@i3_context.action_class("user")
class i3Actions:
    def restart_talon() -> None:
        key("super-shift-t")

    def quit_talon() -> None:
        key("super-ctrl-t")

    def tiling_switch_workspace(digit: int) -> None:
        key(f"super-{digit}")
        sleep("100ms")

    def tiling_move_workspace_and_switch(digit: int) -> None:
        key(f"super-shift-{digit}")
        sleep("100ms")

    def tiling_move_workspace_no_switch(digit: int) -> None:
        key(f"super-ctrl-{digit}")

    def tiling_flip_workspace() -> None:
        key("super-tab")
        sleep("100ms")

    def tiling_focus_direction(arrow_key: str) -> None:
        key(f"super-{arrow}")
        sleep("100ms")

    def tiling_move_direction(arrow_key: str) -> None:
        key(f"super-shift-{arrow}")

    def tiling_resize_mode() -> None:
        key("super-r")

    def tiling_split_vertical() -> None:
        key("super-h")

    def tiling_split_horizontal() -> None:
        key("super-v")

    def tiling_toggle_floating() -> None:
        key("super-shift-space")

    def tiling_switch_window() -> None:
        key("super-right")
        # Do this in case they're vertically stacked.
        key("super-down")
