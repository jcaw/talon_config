import logging

from talon import Module, Context, actions

from user.emacs.utils.state import emacs_state

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


IT_OBJECTS_KEY = "it-object-types"


module = Module()
module.list("dynamic_commands", "Dynamic commands for manipulating semantic objects.")


context = Context()
context.matches = r"""
tag: emacs
"""

context.lists["user.dynamic_commands"] = {}
context.lists["user.dynamic_prefix_commands"] = {}


def bind_command(commands_map, object_name, action_set):
    # Just a super simple spoken form for now.
    action = action_set["action"]
    cleaned_action = action.replace("it-", "").replace("-", " ")
    naive_voice_command = f"{cleaned_action} {object_name}"
    commands_map[naive_voice_command] = action_set["command"]


def object_bindings(object_tables):
    simple_commands, prefix_commands = {}, {}
    # `object_tables` structure:
    # {"python-mode": {"type-1": <object>,
    #                  "type-2": <object>}
    #  "global": {"type-1": <object>}}
    for mode, objects in object_tables.items():
        for object_ in objects:
            # `object_` structure:
            # {"name": <str>,
            #  "available-actions": <List[action_set]>}
            object_name = object_["name"]
            action_sets = object_["available-actions"]
            for action_set in action_sets:
                # `action_set` structure:
                # {"action": <str>,
                #  "command": <str>
                #  "takes-prefix": <bool>}
                target_map = (
                    prefix_commands if action_set["takes-prefix"] else simple_commands
                )
                bind_command(target_map, object_name, action_set)
    return simple_commands, prefix_commands


def update_objects(state):
    global context
    tables = state.get(IT_OBJECTS_KEY, {})
    simple_commands, prefix_commands = object_bindings(tables)
    LOGGER.debug("Dynamic simple commands update:\n", simple_commands)
    context.lists["user.dynamic_commands"] = simple_commands
    LOGGER.debug("Dynamic prefix commands update:\n", prefix_commands)
    context.lists["user.dynamic_prefix_commands"] = prefix_commands


emacs_state.hook_key(IT_OBJECTS_KEY, update_objects)
