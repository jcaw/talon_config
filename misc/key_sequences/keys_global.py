from talon import actions, cron, Context, app

user = actions.user
edit = actions.edit


browser_context = Context()
browser_context.matches = r"""
tag: user.browser
"""

windows_context = Context()
windows_context.matches = r"""
os: windows
"""

draft_context = Context()
draft_context.matches = r"""
tag: user.draft_window_showing
"""


def bind():
    try:
        user.key_sequence_register(
            {
                # Emacs Muscle Memory
                "enter": edit.save,
                ",": edit.cut,
                ".": edit.copy,
                "s": edit.find,
                "/": user.search,
                # Everything Else
                "o": "Open",
                "d": user.draft_current_textbox,
                "D": "Draft Window",
                "D s": user.draft_show,
                "D d": user.draft_current_textbox,
                "o": "Switch Program",
                "o f": user.open_firefox,
                "o c": user.open_chrome,
                "o d": user.open_discord,
                "o s": user.open_slack,
                "o r": user.open_rider,
                "o b": user.open_blender,
                "o w": user.open_whatsapp,
                "o e": user.open_emacs,
                "o t": user.focus_talon_log,
                "o T": user.focus_talon_repl,
                "o space": actions.app.window_hide,
                "m": "Mic",
                # For quicker access
                "space": user.toggle_mic_off,
                "m m": user.noisy_sleep,
                "m w": user.wake,
                "m space": user.toggle_mic_off,
                "=": "Utils",
                "= i": user.copy_current_app_info,
            }
        )

        user.key_sequence_register(
            {
                "o m": user.open_task_manager,
                "o p": user.open_windows_terminal,
                # "o p": user.open_command_prompt,
                # "o P": user.open_powershell,
                "o u": user.open_unreal_engine,
                "o g": user.open_epic_games,
            },
            windows_context,
        )

        user.key_sequence_register(
            {
                "o ,": user.open_current_page_in_chrome,
            },
            browser_context,
        )

        user.key_sequence_register(
            {
                # Hide all the base draft window commands
                "d": None,
                "D": None,
                "h": user.draft_hide,
                "f": user.draft_finish,
                "s": user.draft_finish_and_submit,
                "c": user.draft_cancel,
                "h": user.draft_hide,
            },
            draft_context,
        )

        print("Key sequences registered successfully.")
    except KeyError:
        # The action is not declared yet. Just re-run it on a delay.
        print("Failed to register key sequences. Retrying in 1s.")
        cron.after("1s", bind)


# HACK: Actions won't be registered on startup, so wait until they are.
cron.after("50ms", bind)
