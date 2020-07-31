"""Switch programs.

Module originally from knausj_talon:
https://github.com/knausj85/knausj_talon/blob/8bf1a32bd8ecf588774ca15263114310495f9e7c/code/switcher.py

"""


import os
import re
import time
import logging

from talon import Context, Module, app, imgui, ui, fs
from talon_init import TALON_USER

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


# Construct at startup a list of overides for application names (similar to how homophone list is managed)
# ie for a given talon recognition word set  `one note`, recognized this in these switcher functions as `ONENOTE`
# the list is a comma seperated `<Recognized Words>, <Overide>`
# TODO: Consider put list csv's (homophones.csv, app_name_overrides.csv) files together in a seperate directory,`knausj_talon/lists`
settings_dir = os.path.join(TALON_USER, "settings")
overrides_path = os.path.join(settings_dir, f"app_name_overrides_{app.platform}.csv")
if not os.path.isdir(settings_dir):
    os.mkdir(settings_dir)
if not os.path.isfile(overrides_path):
    with open(overrides_path, "w") as f:
        f.write("")


mod = Module()
mod.list("running", desc="all running applications")
mod.list("launch", desc="all launchable applications")
ctx = Context()

# a list of the current overrides
overrides = {}

# a list of the currently running application names
running_application_dict = {}


@mod.capture
def running_applications(m) -> str:
    "Returns a single application name"


@mod.capture
def launch_applications(m) -> str:
    "Returns a single application name"


@ctx.capture(
    rule=(
        "("
        "{self.running}"
        # " | <user.dictation>"
        ")"
    )
)
def running_applications(m):
    try:
        return m.running
    except AttributeError:
        return m.dictation


@ctx.capture(rule="{self.launch}")
def launch_applications(m):
    return m.launch


def split_camel(word):
    return re.findall(r"[0-9A-Z]*[a-z]+(?=[A-Z]|$)", word)


def get_words(name):
    words = re.findall(r"[0-9A-Za-z]+", name)
    out = []
    for word in words:
        out += split_camel(word)
    return out


def update_lists():
    global running_application_dict
    running_application_dict = {}
    running = {}
    launch = {}
    for cur_app in ui.apps(background=False):
        name = cur_app.name

        if name.endswith(".exe"):
            name = name.rsplit(".", 1)[0]

        words = get_words(name)
        for word in words:
            if word and word not in running:
                running[word.lower()] = cur_app.name

        running[name.lower()] = cur_app.name
        running_application_dict[cur_app.name] = True

    for override in overrides:
        running[override] = overrides[override]

    if app.platform == "mac":
        for base in "/Applications", "/Applications/Utilities":
            for name in os.listdir(base):
                path = os.path.join(base, name)
                name = name.rsplit(".", 1)[0].lower()
                launch[name] = path
                words = name.split(" ")
                for word in words:
                    if word and word not in launch:
                        if len(name) > 6 and len(word) < 3:
                            continue
                        launch[word] = path

    lists = {
        "self.running": running,
        "self.launch": launch,
    }

    # batch update lists
    ctx.lists.update(lists)


def update_overrides(name, flags):
    """Updates the overrides list"""
    global overrides
    overrides = {}

    if name is None or name == overrides_path:
        LOGGER.info("Updating app switcher overrides")
        with open(overrides_path, "r") as f:
            for line in f:
                line = line.rstrip()
                line = line.split(",")
                if len(line) == 2:
                    overrides[line[0].lower()] = line[1].strip()

        update_lists()


update_overrides(None, None)
fs.watch(settings_dir, update_overrides)


@mod.action_class
class Actions:
    def switcher_focus(name: str):
        """Focus a new application by  name"""

        wanted_app = name

        # we should use the capture result directly if it's already in the
        # list of running applications
        # otherwise, name is from <user.text> and we can be a bit fuzzier
        if name not in running_application_dict:

            # don't process silly things like "focus i"
            if len(name) < 3:
                LOGGER.info("switcher_focus skipped: len({}) < 3".format(name))
                return

            running = ctx.lists["self.running"]
            wanted_app = None

            for running_name in running.keys():

                if running_name == name or running_name.lower().startswith(
                    name.lower()
                ):
                    wanted_app = running[running_name]
                    break

            if wanted_app is None:
                return

        for cur_app in ui.apps():
            if cur_app.name == wanted_app and not cur_app.background:
                cur_app.focus()
                break

    def switcher_launch(path: str):
        """Launch a new application by path"""
        ui.launch(path=path)

    def switcher_list_running():
        """Lists all running applications"""
        gui.show()

    def switcher_hide_running():
        """Hides list of running applications"""
        gui.hide()


@imgui.open(software=False)
def gui(gui: imgui.GUI):
    gui.text("Names of running applications")
    gui.line()
    for line in ctx.lists["self.running"]:
        gui.text(line)


def ui_event(event, arg):
    if event in ("app_activate", "app_launch", "app_close", "win_open", "win_close"):
        LOGGER.debug(f"------------------ event:{event}  arg:{arg}")
        update_lists()


ui.register("", ui_event)
