from talon import Module, Context, actions, imgui, app, ui
from typing import Optional, List, Tuple, Any
from pathlib import Path
import os
import subprocess
import webbrowser
from itertools import chain


module = Module()


def duplicates_removed(input_list: List[Any]) -> List[Any]:
    seen = set()
    return [x for x in input_list if x not in seen and not seen.add(x)]


@module.action_class
class Actions:
    """Class holding cleanly named switcher functions"""

    def launch_exact(program_name: str) -> None:
        """Launch a program exactly matching `name`."""
        # TODO: Exact name match, but not path match, on Windows?
        ui.launch(path=program_name)

    def launch_fuzzy(program_name: str) -> None:
        """Launch a program matching `name` - will use fuzzy heuristics to find the program."""

    def heirarchical_name_match(
        target_name: str,
        candidates: List[Tuple[str, Any]],
        match_start: bool,
        match_anywhere: bool,
        match_fuzzy: bool,
    ) -> Any:
        """Match a name to a list of candidates, using a variety of methods.

        Each candidate should be a tuple with the name you want to match
        against, and the values you want to return.

        Each matching method is tried on the entire list before falling back to the
        next matching method. Matches are made against the keys in the `candidates`
        dict, and all matching values will be returned, best to worst.

        """
        # TODO: Maybe switch this to return a list?
        target_name = target_name.lower()

        candidates = [(key.lower(), value) for (key, value) in candidates]
        results = []

        for name, value in candidates:
            if name == target_name:
                results.append(value)

        if match_start:
            for name, value in candidates:
                if name.startswith(target_name):
                    results.append(value)

        if match_anywhere:
            for name, value in candidates:
                if target_name in name:
                    results.append(value)

        # Expand the fuzziness - allow words out of order
        if match_fuzzy:
            target_words = target_name.split(" ")
            for name, value in candidates:
                # If all words are present
                if all(map(lambda word: word in name.split(" "), target_words)):
                    results.append(value)

        return duplicates_removed(results)

    def focus(app_name: Optional[str] = None, title: Optional[str] = None):
        """Focus a program by either the app name, title, or both."""
        assert app_name or title, "Must provide `app_name` and/or `title`."
        apps = ui.apps(background=False)
        if app_name:
            names_matcher = [(app.name, app) for app in apps]
            apps = actions.user.heirarchical_name_match(
                app_name, names_matcher, True, True, True
            )
            if not apps:
                raise IndexError(f'Running app not found matching name: "{app_name}"')
        if title:
            titles_matcher = [(app.active_window.title, app) for app in apps]
            print(titles_matcher)
            apps = actions.user.heirarchical_name_match(
                title, titles_matcher, True, True, True
            )
            if not apps:
                raise IndexError(f'Running app not found matching title: "{title}"')

        app = apps[0]

        try:
            app.focus()
        except Exception as e:
            # HACK: Raise a generic error to make it easier to catch weird or
            #   platform-specific focus failures
            #
            # TODO: This is horrifying, rewrite it
            raise IndexError(f'Problem focussing app: "{e}"')

    def switch_or_start(
        start_name: str,
        focus_name: Optional[str] = None,
        focus_title: Optional[str] = None,
        start_delay: str = "2000ms",
    ) -> None:
        """Switch to a program, starting it if necessary."""
        # Revert to the same name used to start the program when no focus
        # parameters have been set.
        if not (focus_name or focus_title):
            focus_name = start_name

        try:
            actions.user.focus(app_name=focus_name, title=focus_title)
        # Sometimes talon's ui.focus() will pop a `UIErr` because it can't find
        # a window for a running program - in these cases, we assume the program
        # needs to be relaunched.
        except (IndexError, ui.UIErr) as e:
            actions.user.launch_fuzzy(start_name)
            # Give it time to start up
            actions.sleep(start_delay)
            try:
                actions.user.focus(app_name=focus_name, title=focus_title)
            except (IndexError, ui.UIErr) as e:
                print(f"Could not focus newly started program: {focus_name}. Skipping.")
        # Give it time to focus
        actions.sleep("200ms")

    # TODO: Go through each of these and check they all work?

    def open_firefox():
        """Switch to firefox, starting it if necessary."""
        actions.user.switch_or_start("firefox", "5000s")

    def open_chrome():
        """Switch to chrome, starting it if necessary."""
        actions.user.switch_or_start("chrome")

    def open_discord():
        """Switch to discord, starting it if necessary."""
        # FIXME: Won't launch Discord on Windows - but does switch to it if it's
        #   running and not minimized to the tray.
        actions.user.switch_or_start("discord")

    def open_slack():
        """Switch to slack, starting it if necessary."""
        # If slack is minimized to the tray, focussing it causes weird errors -
        # so just restart it. This functions the same as focussing it.
        actions.user.launch_fuzzy("slack")

    def open_rider():
        """Switch to rider, starting it if necessary."""
        actions.user.switch_or_start("rider")

    def open_blender():
        """Switch to blender, starting it if necessary."""
        actions.user.switch_or_start("blender")

    def open_unreal_engine():
        """Switch to unreal_engine, starting it if necessary."""
        actions.user.switch_or_start(
            start_name="Unreal Engine", focus_name="UnrealEditor"
        )

    def open_task_manager():
        """Switch to task_manager, starting it if necessary."""
        actions.user.switch_or_start("task manager")

    # TODO: Remove this? Just leave the Windows Terminal command?
    def open_command_prompt():
        """Switch to command_prompt, starting it if necessary."""
        # Doubles as talon's output
        actions.user.switch_or_start("command prompt")

    # TODO: Remove this? Just leave the Windows Terminal command?
    def open_powershell():
        """Switch to powershell, starting it if necessary."""
        # Doubles as talon's output
        actions.user.switch_or_start("powershell")

    def open_windows_terminal():
        """Switch to Windows Terminal, starting it if necessary."""
        actions.user.switch_or_start("terminal")

    def open_windows_explorer():
        """Open windows explorer (specifically, open the file browser)."""
        # FIXME: Doesn't start file explorer
        actions.user.switch_or_start(
            start_name="file explorer", focus_name="windows explorer"
        )

    def open_epic_games():
        """Switch to epic_games, starting it if necessary."""
        actions.user.switch_or_start(start_name="epic games", focus_name="EpicGames")

    def open_emacs():
        """Switch to emacs, starting it if necessary."""
        # TODO: An action that focuses based on exe AND title
        try:
            actions.user.focus(app_name="vcxsrv", title="emacs")
            return
        except IndexError:
            pass
        try:
            actions.user.focus(app_name="emacs")
            return
        except IndexError:
            pass
        try:
            # Prefer my custom WSL Emacs shortcut on Windows
            actions.user.launch_fuzzy("WSL Emacs")
            return
        except ValueError:
            pass
        # But if all else fails, just use a basic match.
        actions.user.launch_fuzzy("emacs")

    def open_whatsapp():
        """Switch to whatsapp, starting it if necessary."""
        actions.user.switch_or_start(
            start_name="WhatsApp",
            focus_name="Application Frame Host",
            focus_title="WhatsApp",
        )

    def focus_talon_log():
        """Switch to the Talon log."""
        actions.user.focus(app_name="talon", title="Talon Log Viewer")

    def focus_talon_repl():
        """Switch to the Talon repl."""
        # These titles rely on fuzzy match
        if app.platform == "windows":
            actions.user.focus(app_name="WindowsTerminal", title="Talon - REPL")
        else:
            actions.user.focus(title="Talon - REPL")

    def open_talon_log() -> bool:
        """Switch to the Talon log, or open it if it's not showing."""
        try:
            actions.self.focus_talon_log()
            return False
        except IndexError:
            actions.user.automator_open_talon_log()
            return True

    def open_talon_repl() -> bool:
        """Switch to the Talon repl, or start one if it's not running."""
        try:
            actions.self.focus_talon_repl()
            return False
        except IndexError:
            actions.user.automator_open_talon_repl()
            return True


windows_context = Context(name="programs_windows")
windows_context.matches = r"os: windows"


@windows_context.action_class("self")
class WindowsActions:
    def launch_exact(program_name: str) -> None:
        launch_program_windows(program_name, match_start=False, match_fuzzy=False)

    def launch_fuzzy(program_name: str) -> None:
        launch_program_windows(program_name, match_start=True, match_fuzzy=True)


def list_appx_packages():
    out = subprocess.check_output(
        # This will still flash the powershell window even with `-WindowStyle
        # hidden`, which is a shame, but doesn't seem to be avoidable.
        'powershell.exe -WindowStyle hidden -ExecutionPolicy Bypass -Command "Get-AppxPackage"',
        shell=False,
        text=True,
    )
    apps = []
    for app_text in out.split("\n\n"):
        app_dict = {}
        lines = app_text.split("\n")
        # Some sections will be empty - ignore them.
        if len(lines) > 1:
            for line in lines:
                sections = line.split(":")
                if len(sections) >= 2:
                    app_dict[sections[0].strip()] = ":".join(sections[1:])[1:]
            apps.append(app_dict)
    return apps


def launch_program_windows(
    program_name: str, match_start: bool = True, match_fuzzy: bool = True
) -> None:
    # First, try it as an exact path.
    try:
        ui.launch(path=program_name)
        return
    except FileNotFoundError as e:
        pass

    # Now try Windows Store apps.
    #
    # TODO: Apps take priority over start menu shortcuts under this model - do we want that?
    apps = list_appx_packages()
    appx_targets = [(app["Name"], app["PackageFamilyName"]) for app in apps]
    matching_apps = actions.user.heirarchical_name_match(
        program_name, appx_targets, match_start, match_fuzzy, match_fuzzy
    )
    if matching_apps:
        app = matching_apps[0]
        print(f'Launching "{app}" via `explorer.exe shell:AppsFolder`')
        subprocess.run(f"explorer.exe shell:AppsFolder\\{app}!App", shell=False)
        return

    # Next, try matching against the shortcuts in the start menu and on the
    # desktop
    program_name = program_name.lower()

    system_start_programs_path = (
        Path(os.environ.get("PROGRAMDATA")) / "Microsoft/Windows/Start Menu/Programs"
    )
    user_start_programs_path = (
        Path(os.environ.get("APPDATA")) / "Microsoft/Windows/Start Menu/Programs"
    )
    # Note this will only work if the desktop is on the default path
    desktop_path = Path(os.environ.get("APPDATA")) / "Desktop"
    # For now, only use shortcuts
    LNK_PATTERN = "**/*.lnk"
    # Note we remove the file extension when matching against the program name.
    # We also never match against the folder.
    #
    # TODO: Match against the folder too, maybe?
    programs = [
        (path.stem.lower(), path)
        for path in chain(
            # Desktop takes priority - then user start, then global start.
            desktop_path.glob(LNK_PATTERN),
            user_start_programs_path.glob(LNK_PATTERN),
            system_start_programs_path.glob(LNK_PATTERN),
        )
    ]
    programs = duplicates_removed(programs)
    # HACK: Sort by length of name, so Linux versions get lower priority
    programs.sort(key=lambda it: len(it[0]))

    matching_paths = actions.user.heirarchical_name_match(
        program_name, programs, match_start, match_fuzzy, match_fuzzy
    )
    if matching_paths:
        path = matching_paths[0]
        print(f'Launching "{path}"')
        os.startfile(str(path))
        return

    raise ValueError(f'Program could not be started: "{program_name}"')
