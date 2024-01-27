from talon import Module, Context, actions, cron, clip

key = actions.key
insert = actions.insert
sleep = actions.sleep
user = actions.user
edit = actions.edit


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
# Retry window that up when there's a shader compilation error
shader_error_context = Context()
shader_error_context.matches = r"""
app: /UnrealEditor/
title: /Error/
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


@shader_error_context.action_class("edit")
class ShaderErrorEditActions:
    def select_all():
        actions.user.select_all_using_home_end()


SHADER_ERROR_QUESTION = """When Unreal Engine tries to compile my shader, I'm getting the following error:

```
{}
```

What's going wrong?

"""


@shader_error_context.action_class("user")
class ShaderErrorUserActions:
    def copilot_explain_error():
        # Select all text, and copy it
        edit.select_all()
        # Exclude the bottom 3 lines, they're irrelevant.
        # key("shift-up:3")
        # key("shift-end")
        sleep("200ms")
        with clip.capture() as c:
            edit.copy()
        error_text = c.text()
        user.jetbrains_switch_and_ask_copilot(
            SHADER_ERROR_QUESTION.format(error_text), user.open_rider
        )


def bind_keys():
    try:
        actions.user.vimfinity_bind_keys(
            {
                "b": "Build",
                "b s": (user.unreal_recompile_shaders, "Recompile Shaders"),
                "p": "GitHub Copilot",
            },
            editor_context,
        )
        actions.user.vimfinity_bind_keys(
            {"p e": (user.copilot_explain_error, "Explain error")},
            shader_error_context,
        )
    except KeyError:
        print("Failed to bind keys. Retrying in 1s")
        cron.after("1s", bind_keys)


cron.after("50ms", bind_keys)
