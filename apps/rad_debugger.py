import subprocess
import json
from typing import List, NamedTuple
import threading
import pprint

from talon import Module, Context, actions, clip, ui, cron, app, scope

import logging

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


key = actions.key
sleep = actions.sleep


module = Module()


# TODO: There must be a more condensed way of writing this. namedtuple?
class BreakpointData(object):
    def __init__(
        self,
        label,
        condition,
        hit_count: int,
        source_location: str,
        address_location: str,
        function_location: str,
    ) -> None:
        self.label = label
        self.condition = condition
        self.hit_count = hit_count
        self.source_location = source_location
        self.address_location = address_location
        self.function_location = function_location

    def __str__(self) -> str:
        # TODO: pprint?
        return pprint.pformat(self.to_dict())

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "condition": self.condition,
            "hit_count": self.hit_count,
            "source_location": self.source_location,
            "address_location": self.address_location,
            "function_location": self.function_location,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_string(cls, line: str):
        parts_raw = line.strip().replace('"{', "").replace('}"', "").split(", ")
        # HACK: Sometimes `parts_raw` doesn't contain the address and function
        # location, because they're truncated by the UI before copypasrting.
        # Instead, they are represented as the string "'...'" which won't
        # convert to a meaningul (or json) value. So just ignore them always, for now.
        if len(parts_raw) == 6:
            parts = [json.loads(part) for part in parts_raw]
            return BreakpointData(
                label=parts[0],
                condition=parts[1],
                hit_count=parts[2],
                source_location=parts[3],
                address_location=parts[4],
                function_location=parts[5],
            )
        else:
            assert len(parts_raw) == 5, (len(parts_raw), parts_raw)
            parts = [json.loads(part) for part in parts_raw[:4]]
            return BreakpointData(
                label=parts[0],
                condition=parts[1],
                hit_count=parts[2],
                source_location=parts[3],
                address_location="",  # address_location=parts[4],
                function_location="",  # function_location=parts[5],
            )


data_lock = threading.RLock()
breakpoints: List[BreakpointData] = []
breakpoints_synced = False
raddbg_focussed = None


# TODO: Pop up an input blocker, probably.
@module.action_class
class Actions:
    def raddbg_ipc(commands: List[str]) -> str:
        """Run `raddbg --ipc` with a list of commands."""
        return subprocess.check_output(["raddbg.exe", "--ipc", *commands]).decode(
            "utf-8"
        )

    # TODO: Get this info back into Emacs somehow. Probably when rad debugger is defocussed.
    #
    # TODO: Switch this to just read the project file directly?
    def raddbg_get_breakpoints() -> List[BreakpointData]:
        """Get all the breakpoints from the active Rad Debugger session."""
        # TODO: What if raddbg is not running?
        #
        # TODO: Probably remove the overlay. Don't want or need it.
        with actions.user.automator_overlay(
            "Getting Breakpoints from RadDB", invisible=True
        ):
            original_app = ui.active_window()
            try:
                actions.user.focus(app_name="raddbg.exe")
                try:
                    # TODO: Maybe make a new panel before opening this, so as to
                    #   not mess up current tab selection?
                    # FIXME: The animation is messing things up
                    # actions.self.raddbg_ipc(["open_window"])
                    # actions.self.raddbg_ipc(["new_panel"])
                    # actions.self.raddbg_ipc(["new_tab"])
                    actions.sleep("200ms")
                    actions.self.raddbg_ipc(["breakpoints"])
                    # sleep("200ms")
                    # We need to press down twice to get raddbg to start registering selection commands.
                    # This should select all.
                    key("ctrl-home")
                    key("shift-ctrl-end")
                    with clip.capture() as c:
                        key("ctrl-c")
                    breakpoints_raw_string = c.text()
                finally:
                    # FIXME: If it was minimized, minimize it again.
                    actions.self.raddbg_ipc(["close_tab"])
                    # actions.self.raddbg_ipc(["close_panel"])
                    # actions.self.raddbg_ipc(["close_window"])
            finally:
                original_app.focus()
            # Now parse the breakpoints
            breakpoints = []
            LOGGER.debug("Breakpoints raw string:")
            LOGGER.debug(breakpoints_raw_string)
            for line in breakpoints_raw_string.split("\n"):
                if line.startswith('"{""'):
                    breakpoints.append(BreakpointData.from_string(line))
            return breakpoints


module.tag("raddbg_main_window")
main_window_context = Context()
main_window_context.matches = """
os: windows
app: raddbg.exe
"""
main_window_context.tags = ["user.raddbg_main_window"]


def is_active_app_raddbg(tags=None):
    return "user.raddbg_main_window" in (tags or scope.get("tag"))


def is_active_app_emacs(tags=None):
    return "user.emacs" in (tags or scope.get("tag"))


def sync_breakpoints():
    global breakpoints_synced
    with data_lock:
        breakpoints_synced = False
        breakpoints = actions.self.raddbg_get_breakpoints()
        LOGGER.debug("Synced rad breakpoints.")
        LOGGER.debug(pprint.pformat(breakpoints))
        breakpoints_synced = True


# TODO: Emacs focus only?
def poll_focus():
    global raddbg_focussed, breakpoints_synced
    tags = scope.get("tag")
    is_rad = is_active_app_raddbg(tags)
    is_emacs = is_active_app_emacs(tags)
    if raddbg_focussed and is_emacs:
        # User unfocussed raddbg, and has now focussed Emacs. So, sync breakpoints.
        LOGGER.debug("raddbg unfocussed - emacs focussed")
        # TODO: Ensure rad is still actually working
        with data_lock:
            raddbg_focussed = False
            sync_breakpoints()
        # TODO: Edge case - lock screen, or other failure to sync.
    elif not raddbg_focussed and is_rad:
        # Use just focussed raddbg
        LOGGER.debug("raddbg focussed")
        with data_lock:
            raddbg_focussed = True
            # if not breakpoints_synced:
            #     sync_breakpoints()


def setup_focus():
    global raddbg_focussed
    try:
        with data_lock:
            raddbg_focussed = is_active_app_raddbg()
    # In case necessary actions weren't loaded yet
    except:
        cron.after("500ms", setup_focus)
    cron.interval("400ms", poll_focus)


# NOTE: Syncing on focus out is disabled, for now.
# if app.platform == "windows":
#     # Have to do this with cron to ensure actions are loaded
#     cron.after("500ms", setup_focus)
