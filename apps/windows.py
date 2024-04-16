import os
import subprocess
import sys
from pathlib import Path

from talon import Context, Module, actions

key = actions.key
sleep = actions.sleep


module = Module()

@module.action_class
class Actions():
    def windows_cast_screen():
        """Open the Windows screen casting interface."""
        key("win:down")
        sleep("100ms")
        key("k")
        sleep("100ms")
        key("win:up")


context = Context()
context.matches = """
os: windows
"""


@context.action_class("self")
class UserActions:
    # def quit_talon() -> None:
    #     # `taskkill` has weird access permissions, so access may be denied. Use
    #     # `wmic` instead, it's more reliable.

    #     # subprocess.Popen(["taskkill", "-pid", str(os.getpid())], start_new_session=True)
    #     # subprocess.Popen(["taskkill", "-im", "talon.exe"], start_new_session=True)

    #     subprocess.Popen(
    #         [
    #             "wmic",
    #             "process",
    #             "where",
    #             "name='talon.exe'",
    #             # "processID='{}'".format(os.getpid()),
    #             "delete",
    #         ],
    #         start_new_session=True,
    #     )

    def restart_talon() -> None:
        # Should be something like: "C:/Program Files/Talon/python/bin/python3"
        python_path = Path(sys.executable)
        # Find the closest parent to Talon's root folder, since Talon's root
        # folder could be named anything
        while not str(python_path.stem) == "python":
            if python_path.parent == python_path:
                raise IOError("Can't find parent python folder")
            else:
                python_path = python_path.parent
        # From there, assume the talon exe's path
        talon_path = python_path.parent / "talon.exe"
        print(f'Restarting Talon from path: "{talon_path}"')
        subprocess.Popen(
            f'wmic process where "name=\'talon.exe\'" delete && sleep 2 && "{talon_path}"',
            # "where processID='{}'".format(os.getpid())
            start_new_session=True,
            shell=True,
        )
