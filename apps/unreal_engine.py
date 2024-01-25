from talon import Module, Context, actions, cron

key = actions.key
insert = actions.insert
sleep = actions.sleep


module = Module()


@module.action_class
class Actions:
    def unreal_command(command: str):
        """Execute a console command in the Unreal Editor."""

    def unreal_recompile_shaders(changed_only: bool = True):
        """Recompile shaders in the Unreal Editor"""
        if changed_only:
            actions.self.unreal_command("RecompileShaders Changed")
            # Shortcut - easier
            # key("ctrl-shift-.")
        else:
            actions.self.unreal_command("RecompileShaders All")


editor_context = Context()
editor_context.matches = r"""
app: /UnrealEditor/
"""


@editor_context.action_class("self")
class UnrealActions:
    def unreal_command(command: str):
        assert "\n" not in command, command

        # FIXME: IS this working?
        key("`")
        sleep("200ms")
        key("ctrl-a")
        insert(command)
        key("enter")


def bind_keys():
    try:
        actions.user.vimfinity_bind_keys(
            {
                "b": "Build",
                "b s": (actions.user.unreal_recompile_shaders, "Recompile Shaders"),
            },
            editor_context,
        )
    except KeyError:
        print("Failed to bind keys. Retrying in 1s")
        cron.after("1s", bind_keys)


cron.after("50ms", bind_keys)
