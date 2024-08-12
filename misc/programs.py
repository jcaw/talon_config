from talon import Module, Context, actions, imgui, app, ui
from typing import Optional, List, Tuple, Any
from pathlib import Path
import os
import subprocess
import webbrowser
import re
import time
from itertools import chain


module = Module()


def duplicates_removed(input_list: List[Any]) -> List[Any]:
    seen = set()
    return [x for x in input_list if x not in seen and not seen.add(x)]


def wait_string_to_seconds_rough(time_string: str) -> float:
    if re.match(r"^[0-9]+ms$", time_string):
        return float(time_string[:-2]) / 1000
    elif re.match(r"^[0-9]+s$", time_string):
        return float(time_string[:-1])
    else:
        raise ValueError(
            f'Only "ms" and "s" time formats are supported in the switcher at this time. You gave: "{time_string}"'
        )


class FocusTimeoutError(RuntimeError):
    pass


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
        # apps = ui.apps(background=False)
        windows = ui.windows()
        # TODO 1: Filter windows to ensure they're valid focus targets
        if app_name:
            names_matcher = [(w.app.name, w) for w in windows]
            windows = actions.user.heirarchical_name_match(
                app_name, names_matcher, True, True, True
            )
            if not windows:
                raise IndexError(f'Window not found matching app name: "{app_name}"')
        if title:
            titles_matcher = [(w.title, w) for w in windows]
            windows = actions.user.heirarchical_name_match(
                title, titles_matcher, True, True, True
            )
            if not windows:
                raise IndexError(
                    f'Window not found matching app name: "{app_name}" and title: "{title}"'
                    if app_name
                    else f'Window not found matching title: "{title}"'
                )

        # TODO 1: Try focussing each in turn, only error out if none can be focussed?
        window = windows[0]

        # Another edge case - Windows didn't focus anything. In this case alt-tab to get something in focus before focussing.
        if not ui.active_window():
            print("Window:", ui.active_window())
            print("No window focussed. Alt-tabbing to handle edge case.")
            actions.key("alt-tab")
        # Edge case - if the window is already focussed, don't bother re-focussing it.
        if window == ui.active_window():
            print("Window already focussed.")
            return

        try:
            window.focus()
            # Allow some time for it to focus. Failing to do this can cause
            # weird race conditions where no windows at all end up focussed,
            # depending how this `focus` action is used.
            actions.sleep("100ms")
        except Exception as e:
            # HACK: Raise a generic error to make it easier to catch weird or
            #   platform-specific focus failures
            #
            # TODO: This is horrifying, rewrite it
            raise IndexError(f'Problem focussing app: "{e}"')

    # TODO: Roll this back into `switch_or_start`? Do I actually want to use it
    #   given the inherent race condition (what if the program starts before
    #   it's called)? Maybe, but "maybe" is a bad reason to keep code around.
    def focus_and_wait(
        focus_name: Optional[str] = None,
        focus_title: Optional[str] = None,
        timeout: str = "5000ms",
        start_delay: str = "300ms",
    ):
        """Focus a window. If it's not open, wait for it to open.

        Use this e.g. when you already opened a window, and you're waiting for
        it to be created.

        `timeout` is the wait for it to open. `start_delay` is the time to wait
        afterwards, iff it wasn't immediately detected.

        """
        assert focus_name or focus_title

        timeout_secs = wait_string_to_seconds_rough(timeout)
        deadline = time.monotonic() + timeout_secs

        # Try to focus quickly first - only pop the automation overlay if
        # there's a delay.
        try:
            actions.user.focus(app_name=focus_name, title=focus_title)
            return True
        except (IndexError, ui.UIErr):
            pass

        # Now we know this will take non-negligible amount of time, so pop the
        # automation overlay.
        if focus_name and focus_title:
            focus_prompt = f'Focussing {focus_name}, "{focus_title}"'
        elif focus_name:
            focus_prompt = f"Focussing {focus_name}"
        else:
            focus_prompt = f'Focussing "{focus_title}"'
        with actions.user.automator_overlay(focus_prompt):
            while True:
                actions.sleep("100ms")
                try:
                    actions.user.focus(app_name=focus_name, title=focus_title)
                    break
                except (IndexError, ui.UIErr) as e:
                    if time.monotonic() > deadline:
                        raise FocusTimeoutError(
                            "Could not detect app after trying to focus."
                        )
        with actions.user.automator_overlay(
            f"Waiting {start_delay} for app to finish startup"
        ):
            # Give it a little time for the window to get into the correct state.
            actions.sleep(start_delay)
            return False

    def switch_or_start(
        start_name: str,
        focus_name: Optional[str] = None,
        focus_title: Optional[str] = None,
        # TODO: Rename this to `start_timeout`
        start_deadline: str = "7000ms",
        start_delay: str = "300ms",
    ) -> bool:
        """Switch to a program, starting it if necessary.

        Returns `True` if a new instance was started, `False` if an existing
        instance was focussed.

        """
        # Early validate the input
        wait_string_to_seconds_rough(start_deadline)

        # Revert to the same name used to start the program when no focus
        # parameters have been set.
        if not (focus_name or focus_title):
            focus_name = start_name

        try:
            actions.user.focus(app_name=focus_name, title=focus_title)
            return False
        # Sometimes talon's ui.focus() will pop a `UIErr` because it can't find
        # a window for a running program - in these cases, we assume the program
        # needs to be relaunched.
        except (IndexError, ui.UIErr) as e:
            with actions.user.automator_overlay(f"Starting {start_name}"):
                actions.user.launch_fuzzy(start_name)
                try:
                    actions.user.focus_and_wait(
                        focus_name, focus_title, start_deadline, start_delay
                    )
                except FocusTimeoutError:
                    raise FocusTimeoutError(
                        "Could not detect app after trying to start."
                    )
                return True

    # TODO: Go through each of these and check they all work?

    def open_firefox() -> bool:
        """Switch to firefox, starting it if necessary."""
        return actions.user.switch_or_start(
            "firefox", start_deadline="15s", start_delay="3s"
        )

    def open_chrome() -> bool:
        """Switch to chrome, starting it if necessary."""
        return actions.user.switch_or_start(
            "chrome", start_deadline="15s", start_delay="1s"
        )

    def open_discord() -> bool:
        """Switch to discord, starting it if necessary."""
        # FIXME: Won't launch Discord on Windows - but does switch to it if it's
        #   running and not minimized to the tray.
        return actions.user.switch_or_start("discord")

    def open_slack():
        """Switch to slack, starting it if necessary."""
        # If slack is minimized to the tray, focussing it causes weird errors -
        # so just restart it. This functions the same as focussing it.
        actions.user.launch_fuzzy("slack")

    def open_rider() -> bool:
        """Switch to rider, starting it if necessary."""
        return actions.user.switch_or_start(
            "rider", start_deadline="30s", start_delay="10s"
        )

    def open_blender() -> bool:
        """Switch to blender, starting it if necessary."""
        return actions.user.switch_or_start("blender")

    def open_unreal_engine() -> bool:
        """Switch to unreal_engine, starting it if necessary."""
        return actions.user.switch_or_start(
            start_name="Unreal Engine", focus_name="UnrealEditor"
        )

    def open_task_manager() -> bool:
        """Switch to task_manager, starting it if necessary."""
        return actions.user.switch_or_start("task manager")

    # TODO: Remove this? Just leave the Windows Terminal command?
    def open_command_prompt() -> bool:
        """Switch to command_prompt, starting it if necessary."""
        # Doubles as talon's output
        return actions.user.switch_or_start("command prompt")

    # TODO: Remove this? Just leave the Windows Terminal command?
    def open_powershell() -> bool:
        """Switch to powershell, starting it if necessary."""
        # Doubles as talon's output
        return actions.user.switch_or_start("powershell")

    def open_windows_terminal() -> bool:
        """Switch to Windows Terminal, starting it if necessary."""
        return actions.user.switch_or_start("terminal")

    def open_windows_explorer() -> bool:
        """Open windows explorer (specifically, open the file browser)."""
        # FIXME: Doesn't start file explorer
        return actions.user.switch_or_start(
            start_name="file explorer", focus_name="windows explorer"
        )

    def open_epic_games() -> bool:
        """Switch to epic_games, starting it if necessary."""
        return actions.user.switch_or_start(
            start_name="epic games", focus_name="EpicGames"
        )

    def open_emacs() -> bool:
        """Switch to emacs, starting it if necessary."""

    def open_whatsapp() -> bool:
        """Switch to whatsapp, starting it if necessary."""
        return actions.user.switch_or_start(
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
            try:
                # Just in case it didn't focus, try to do so manually.
                actions.self.focus_talon_log()
            except:
                pass
            return True

    def open_talon_repl() -> bool:
        """Switch to the Talon repl, or start one if it's not running."""
        try:
            actions.self.focus_talon_repl()
            return False
        except IndexError:
            actions.user.automator_open_talon_repl()
            try:
                # Just in case it didn't focus (seems to happen sometimes with
                # the UI automation), try to manually focus it.
                actions.self.focus_talon_repl()
            except:
                pass
            return True


windows_context = Context(name="programs_windows")
windows_context.matches = r"os: windows"


@windows_context.action_class("self")
class WindowsActions:
    def launch_exact(program_name: str) -> None:
        launch_program_windows(program_name, match_start=False, match_fuzzy=False)

    def launch_fuzzy(program_name: str) -> None:
        launch_program_windows(program_name, match_start=True, match_fuzzy=True)

    def open_emacs() -> bool:
        # Emacs needs special handling because it's started weirdly and I may
        # not be running a consistent version.
        try:
            actions.user.focus(app_name="vcxsrv", title="emacs")
            return False
        except IndexError:
            pass
        try:
            actions.user.focus(app_name="emacs")
            return False
        except IndexError:
            pass
        # It's not already open. Start it.
        with actions.user.automator_overlay("Starting Emacs"):
            try:
                # Prefer my custom WSL Emacs shortcut on Windows
                actions.user.launch_fuzzy("WSL Emacs")
                return actions.user.focus_and_wait(
                    focus_name="vcxsrv",
                    focus_title="emacs",
                    timeout="10s",
                    start_delay="10s",
                )
            except ValueError:
                # TODO: Explain `ValueError` here probably.
                pass
            # But if all else fails, just use a basic match.
            actions.user.launch_fuzzy("emacs")
            return actions.user.focus_and_wait(
                app_name="emacs", timeout="10s", start_delay="10s"
            )


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
        print(f'Launched successfully via ui: "{program_name}"')
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
