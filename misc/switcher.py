"""Switch programs.

Module originally from knausj_talon:
https://github.com/knausj85/knausj_talon/blob/8bf1a32bd8ecf588774ca15263114310495f9e7c/code/switcher.py

"""


import os
import re
import time
import logging
import subprocess

from talon import Context, Module, app, imgui, ui, fs, actions
from talon_init import TALON_USER

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

key = actions.key


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
running_names = set()


@mod.capture
def running_applications(m) -> str:
    "Returns a single application name"


@mod.capture
def launch_applications(m) -> str:
    "Returns a single application name"


@mod.capture(
    rule=(
        "("
        "{self.running}"
        # " | <user.dictation>"
        ")"
    )
)
def running_applications(m) -> str:
    return m.running if hasattr(m, "running") else m.dictation


# TODO: Removed because it now was just peppering an error through my log. Figure out what this was doing and how it's changed in knausj.
@mod.capture(rule="{self.launch}")
def launch_applications(m) -> str:
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
    global running_names
    running_names.clear()
    running = {}
    launch = {}
    for cur_app in ui.apps(background=False):
        name = cur_app.name

        if name.endswith(".exe"):
            name = name.rsplit(".", 1)[0]

        words = get_words(name)
        for word in words:
            if word and word not in running and len(word) > 2:
                running[word.lower()] = cur_app.name

        running[name.lower()] = cur_app.name
        running_names.add(cur_app.name)

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


def launchable_app(target_name, app_list):
    target_name = target_name.lower()


def running_app_from_title(target_title, app_list=None):
    if not app_list:
        app_list = ui.apps(background=False)

    for app in app_list:
        print(app)

    app_pairs = [(app.active_window.title, app) for app in app_list]

    # TODO: Switch this to a regexp match?
    matching = actions.user.heirarchical_name_match(
        target_title, app_pairs, True, True, False
    )
    return matching[0] if matching else None


def running_app_from_name(
    target_name, app_list=None, match_start=True, match_fuzzy=True
):
    if not app_list:
        app_list = ui.apps(background=False)

    app_pairs = [(app.name, app) for app in app_list]
    matching = actions.user.heirarchical_name_match(
        target_name, app_pairs, match_start, match_fuzzy, match_fuzzy
    )
    return matching[0] if matching else None


@mod.action_class
class Actions:
    def switcher_kill(executable: str = "", title: str = "") -> None:
        """Kill all apps matching `executable` and `title`."""
        assert title or executable, (executable, title)
        for cur_app in ui.apps():
            LOGGER.debug("Title:", cur_app.active_window.title)
            LOGGER.debug("Name: ", cur_app.exe)
            if (
                (title in cur_app.active_window.title)
                and (executable in cur_app.exe)
                # and not cur_app.background
            ):
                try:
                    cur_app.focus()
                    time.sleep(0.1)
                    # TODO: Raise error off windows
                    key("alt-f4")
                except:
                    pass

    def switcher_focus_title(title: str) -> None:
        """Focus an application by title."""
        app = running_app_from_title()
        if app:
            app.focus()
        else:
            raise IndexError(f'Running app not found matching title: "{title}"')

    def switcher_focus(name: str, match_title: bool = True):
        """Focus an application by name"""

        ui_apps = ui.apps(background=False)

        # we should use the capture result directly if it's already in the
        # list of running applications
        # otherwise, name is from <user.text> and we can be a bit fuzzier
        if name in running_names:
            wanted_app = running_app_from_name(
                name, app_list=ui_apps, match_start=False, match_fuzzy=False
            )
        elif len(name) < 3:
            # don't process silly things like "focus i"
            ValueError(f'switcher_focus skipped: len("{name}") < 3')
        else:
            # Prefer matching on app name
            wanted_app = running_app_from_name(name, app_list=ui_apps)
            if match_title and wanted_app is None:
                wanted_app = running_app_from_title(name, app_list=ui_apps)

        if wanted_app is None:
            raise IndexError(f'Running app not found matching name: "{name}"')
        else:
            LOGGER.debug(f"switching to {wanted_app}")
            wanted_app.focus()
            # User may have been choosing from the list. So after a
            # successful switch, hide it.
            actions.self.switcher_hide_running()

    def switcher_focus_temporarily(
        name: str, pause: str = "300ms", match_title: bool = True
    ) -> None:
        """Switch to an application by name, then switch back."""
        current_app = ui.active_app()
        actions.self.switcher_focus(name)
        actions.sleep(pause)
        current_app.focus()

    # TODO: Allow command line parameters (see code search for `ui.launch` implementations)
    def switcher_launch(path: str):
        """Launch a new application by path (all OSes), or AppUserModel_ID path on Windows"""
        if app.platform == "windows":
            is_valid_path = False
            try:
                current_path = Path(path)
                is_valid_path = current_path.is_file()
            except:
                is_valid_path = False
            if is_valid_path:
                ui.launch(path=path)
            else:
                # TODO: Maybe try searching for it in the start menu before reverting to this method?
                cmd = "explorer.exe shell:AppsFolder\\{}".format(path)
                subprocess.Popen(cmd, shell=False)
        else:
            # TODO: Search all programs for this one
            ui.launch(path=path)

    def switcher_list_running():
        """Toggles display of running applications"""
        if gui.showing:
            gui.hide()
        else:
            gui.show()

    def switcher_hide_running():
        """Hides list of running applications"""
        gui.hide()


@imgui.open()
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
