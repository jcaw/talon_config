from typing import List
import time

from talon import Module, actions

from user.newapi.emacs.utils import rpc
from user.newapi.emacs.utils.state import emacs_state


key = actions.key
insert = actions.insert

# TODO: Context-based action here? Fallback for some behaviour.


def typed_prefix_arg(prefix_arg):
    if prefix_arg is not None:
        key("ctrl-u")
        time.sleep(0.1)
        for char in str(prefix_arg):
            key(char)


def type_command(command, prefix_arg):
    typed_prefix_arg(prefix_arg)
    key("alt-x")
    insert(command)
    key("enter")


def is_command_bound(command):
    defined_commands = emacs_state.get("defined-commands", [])
    return command in defined_commands


module = Module()


@module.action_class
class Actions:
    def emacs_command(command: str) -> None:
        """Run an Emacs command."""
        rpc.run_command(command)

    def emacs_prefix_command(command: str, prefix_arg: str = [4]) -> None:
        """Run an Emacs command with a prefix argument.

        Leave ``prefix_arg`` blank to supply an empty prefix argument. (You
        cannot supply multiple empty prefix arguments with this method - use
        `emacs_prefix` and `emacs_command` for that.)

        Note if ``prefix_arg`` is `None`, the command will be called without a
        prefix argument. This works well with optional components, such as
        `[<number>]`.

        """
        if isinstance(prefix_arg, int):
            prefix_arg = str(prefix_arg)
        rpc.run_command(command, prefix_arg=prefix_arg)

    def emacs_fallbacks(
        commands: List[str], prefix_arg: str = None, keypress: str = None
    ) -> None:
        """Run the first bound Emacs command.

        If none are available, press ``keypress``.

        Use this to map one phrase to a similar action across Emacs
        configurations.

        """
        for command in commands:
            if is_command_bound(command):
                actions.self.emacs_command(command, prefix_arg)
                break
        else:
            if keypress:
                if prefix_arg:
                    typed_prefix_arg(prefix_arg)
                key(keypress)
            else:
                raise ValueError(
                    "None of these commands appear bound, and no fallback key "
                    f"was defined. Commands: {commands}"
                )

    def emacs_prefix(arg: str = None) -> None:
        """Input a prefix argument.

        :param arg: the argument. Leave as None to type an empty prefix
          argument.

        """
        # TODO: Switch to RPC `universal-argument` when possible
        if arg in ["-", ""] or isinstance(arg, int):
            typed_prefix_arg(arg)
        elif arg is None or arg is True:
            typed_prefix_arg("")
        else:
            raise ValueError(f"Invalid prefix arg: {type(arg)}, {arg}")
