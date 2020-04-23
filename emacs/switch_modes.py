"""Allow mode commands to be spoken."""

from typing import List, Dict

from talon import Module, Context

from user.utils import spoken_form
from user.emacs.utils.state import emacs_state


DEFINED_COMMANDS_KEY = "defined-commands"


module = Module()
module.list(
    "emacs_mode_commands", desc="All currently active major- and minor-mode commands."
)


@module.capture(rule="{user.emacs_mode_commands}")
def emacs_mode_command(m) -> str:
    """An Emacs major- or minor-mode command."""
    return m.emacs_mode_commands


context = Context()


def _extract_mode_commands(all_commands: List[str]) -> List[str]:
    """Extract the major- and minor-mode commands from `all_commands`."""
    mode_commands = {}
    for command in all_commands:
        if command.endswith("-mode"):
            mode_commands[spoken_form(command)] = command
    return mode_commands


def _set_mode_commands(emacs_state: Dict) -> List[str]:
    """Extract & set the current `-mode` commands."""
    defined_commands = emacs_state.get(DEFINED_COMMANDS_KEY, [])
    context.lists["user.emacs_mode_commands"] = _extract_mode_commands(defined_commands)


emacs_state.hook_key(DEFINED_COMMANDS_KEY, _set_mode_commands)
_set_mode_commands(emacs_state.freeze())
