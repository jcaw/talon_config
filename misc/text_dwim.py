import time

from talon import Module, actions, clip, app

user = actions.user


module = Module()


@module.action_class
class ModuleActions:
    # TODO: Long-term it may be good to pull out the act of getting the current
    #   "thing" into a text range to allow arbitrary actions on it.

    def get_that_dwim() -> str:
        """Get the current text object - meaning depends on context.

        Highlighted text is usually preferred.

        """
        return user.get_highlighted()

    def copy_that_dwim() -> None:
        """Copy the current text object - meaning depends on context.

        Highlighted text is usually preferred.

        """
        user.copy_safe()

    def cut_that_dwim() -> None:
        """Cut the current text object - meaning depends on context.

        Highlighted text is usually preferred.

        """
        user.cut_safe()
