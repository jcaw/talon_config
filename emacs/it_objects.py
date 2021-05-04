import logging

from talon import Module, Context, actions

from user import utils
from user.emacs.utils.voicemacs import rpc_call, emacs_state

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


IT_OBJECTS_KEY = "it-object-types"


# short_action_prefixes = {
#     # Should this be last and next? (lass and neck)
#     "it-go-backward": (
#         # "leff",
#         "lass",
#         # "l",
#     ),
#     "it-go-forward": (
#         # "ritt",
#         "neck",
#         # "n",
#     ),
#     "it-mark": ("sell", "sl"),
#     # TODO: Maybe select right & left?
#     "it-copy": "copp",
#     "it-kill": "kill",  # Should this double as cut across the board?
#     # "for" can be unreliable. Use both to increase reliability.
#     "it-kill-forward": ("fr", "for"),
#     "it-kill-backward": "back",
#     "it-mark-forward": ("nesl", "nessell"),
#     "it-mark-backward": ("lasl", "lassell"),
#     "it-mark-outer": ("sellout", "sloutt"),
#     "it-mark-expand": "spand",
#     # TODO: Untested
#     "it-go-inner-start": "ins",  # "cins"?
#     "it-go-inner-end": "ind",  # "cind"?
#     # Movement
#     #
#     # TODO: These other move commands should use last and next? f and b are
#     #   for modifying commands.
#     #
#     # TODO: Could also try "down" and "up" in these contractions.
#     # "fowness", "fuppess", "bowness", "buppess"
#     "it-go-forward-down": "nent",
#     "it-go-backward-down": "lant",
#     "it-go-forward-up": "nowt",
#     "it-go-backward-up": "loutt",
#     "it-go-forward-start": "ness",
#     "it-go-backward-end": "land",
#     # TODO: These aren't implemented by `it` yet. What layout do I want?
#     "it-skip-backward-start": "ins",
#     "it-skip-forward-end": "ind",
#     # TODO: These seem kinda dodgy.
#     "it-skip-forward": "nemp",  # [ne]xt jup[mp]
#     "it-skip-backward": "lamp",  # [la]st ju[mp]
#     # Inside/Outside
#     "it-kill-inside": ("gutt", "klin"),
#     "it-copy-inside": (
#         # [g]rab [in]side
#         "ginn",
#         # Doesn't work
#         # "coppinn",
#     ),
#     "it-mark-inside": ("sellin", "slinn"),
#     "it-strip": "strip",
#     "it-wrap": "wrap",
#     # Slurp & Barf
#     "it-slurp-forward": "nerp",
#     "it-slurp-backward": "larp",
#     "it-slurp-forward": "nerf",
#     "it-slurp-backward": "larf",
#     # Advanced manipulations
#     "it-transpose-forward": "push",
#     "it-transpose-backward": "pull",
#     # TODO: Not implemented by it yet
#     # Mostly for s-expressions
#     "it-convolute": "conv",
#     # "it-list-all": "list",
#     "it-multiply-cursor-forward": "faltip",
#     "it-multiply-cursor-backward": "baltip",
#     # TODO: Is this going to introduce ambiguity with characters?
#     "it-jump-to": "jump",
# }

# FIXME: "lass<whatever>" commands seem to causing a lot of trouble under wav2letter.
short_action_prefixes = {
    # Should this be last and next? (lass and neck)
    "it-go-backward": "back",
    "it-go-forward": ("for", "fr"),
    "it-mark": ("sell", "sl"),
    # TODO: Maybe select right & left?
    "it-copy": "copp",
    "it-kill": "kill",  # Should this double as cut across the board?
    # "for" can be unreliable. Use both to increase reliability.
    "it-kill-forward": "neck",
    "it-kill-backward": "lass",
    # "it-mark-forward": ("fosl", "fossell"),
    # "it-mark-backward": ("basl", "bassell"),
    "it-mark-forward": "foss",
    "it-mark-backward": "bass",
    "it-mark-outer": ("sellout", "sloutt"),
    "it-mark-expand": "spand",
    # TODO: Untested
    "it-go-inner-start": "ins",  # "cins"?
    "it-go-inner-end": "ind",  # "cind"?
    # Movement
    #
    # TODO: These other move commands should use last and next? f and b are
    #   for modifying commands.
    #
    # TODO: Could also try "down" and "up" in these contractions.
    # "fowness", "fuppess", "bowness", "buppess"
    "it-go-forward-down": "font",
    "it-go-backward-down": "bant",
    "it-go-forward-up": "fowt",  # Pronounced "f-out"
    "it-go-backward-up": "bowt",  # Pronounced "b-out"
    # TODO: Will this be too similar to "foss"?
    "it-go-forward-start": "fost",
    # TODO: band or bend?
    "it-go-backward-end": "band",
    # TODO: These aren't implemented by `it` yet. What layout do I want?
    "it-skip-backward-start": "ins",
    "it-skip-forward-end": "ind",
    # TODO: These seem kinda dodgy.
    "it-skip-forward": "fomp",
    "it-skip-backward": "bamp",
    # Inside/Outside
    "it-kill-inside": ("gutt", "klin"),
    "it-copy-inside": (
        # [g]rab [in]side
        "ginn",
        # Doesn't work
        # "coppinn",
    ),
    "it-mark-inside": ("sellin", "slinn"),
    "it-strip": "strip",
    # "it-wrap": "wrap",
    "it-wrap": "rapp",  # Better than "wrap" with conformer
    # Slurp & Barf
    "it-slurp-forward": "furp",
    "it-slurp-backward": "bapp",
    "it-slurp-forward": "farf",
    "it-slurp-backward": "barf",
    # Advanced manipulations
    "it-transpose-forward": "push",
    "it-transpose-backward": "pull",
    # TODO: Not implemented by it yet
    # Mostly for s-expressions
    "it-convolute": "conv",
    # "it-list-all": "list",
    "it-multiply-cursor-forward": "faltip",
    "it-multiply-cursor-backward": "baltip",
    # TODO: Is this going to introduce ambiguity with characters?
    "it-jump-to": "jump",
    "it-duplicate": ("joop", "doop"),
    # TODO: Comment commands?
    "it-comment": "comment",
}

# TODO: Not used yet
long_name_remaps = {
    "invokation": "call",
}

short_suffixes = {
    "word": "urd",
    # "word": "erd",
    "sexp": "ess",
    # "symbol": "oll",
    "symbol": "imble",
    "line": "ign",
    "block": "ock",
    # TODO: Should this be "function" in `it`?
    # "defun": " funk",
    # "defun": " def",
    # (Dragon) "eff" misrecognizes a lot.
    # "defun": "ef",
    "defun": "unk",
    "class": " class",
    # Clashes with line
    "statement": "ent",
    # "statement": " atement",
    "comment": " comment",
}


module = Module()
module.list(
    "emacs_object_commands", "Dynamic commands for manipulating semantic objects."
)
module.list(
    "emacs_object_prefix_commands",
    "Dynamic commands for manipulating semantic objects - these can take a prefix.",
)
module.list(
    "emacs_object_wrapping_commands",
    "Commands wrap an object. Each command should correspond to its object type.",
)


context = Context()
context.matches = r"""
tag: user.emacs
"""

context.lists["user.emacs_object_commands"] = {}
context.lists["user.emacs_object_prefix_commands"] = {}
context.lists["user.emacs_object_wrapping_commands"] = {}


@module.action_class
class Actions:
    def emacs_wrap_object(object_type: str, pair_opening: str) -> None:
        """Wrap the current object of `object_type`.

        `pair_opening` is the start of the pair to wrap it with.

        """
        rpc_call(
            "it-wrap",
            [
                # Convert to Elisp symbol
                #
                # FIXME: Probably fix `it` to allow reference by symbol or string
                f"'{object_type}",
                pair_opening,
            ],
        )


context = Context()
context.matches = """
tag: user.emacs
"""


@context.action_class("self")
class EmacsActions:
    def get_that_dwim() -> str:
        return rpc_call("it-text-of-thing-at-dwim")

    def copy_that_dwim() -> None:
        actions.self.emacs_command("it-copy-dwim")

    def cut_that_dwim() -> None:
        actions.self.emacs_command("it-kill-dwim")


def short_commands(object_name, action):
    """Yield every short command for `action` on `object_name`."""
    suffix = short_suffixes.get(object_name)
    if not suffix:
        return
    prefixes = short_action_prefixes.get(action, [])
    if isinstance(prefixes, str):
        prefixes = [prefixes]
    elif not isinstance(prefixes, (list, tuple)):
        raise TypeError(f'Invalid prefix type: "{prefixes}", {type(prefixes)}')
    for prefix in prefixes:
        yield f"{prefix}{suffix}"


def action_command(action: str) -> str:
    """Create a spoken form of a particular action."""
    if action.startswith("it-"):
        action = action[3:]
    # Go implies movement. It's unnecessary.
    if action.startswith("go-"):
        action = action[3:]
    return utils.spoken_form(action)


def object_bindings(object_tables):
    simple_commands, prefix_commands, wrap_commands = {}, {}, {}
    # `object_tables` structure:
    # {"python-mode": {"type-1": <object>,
    #                  "type-2": <object>}
    #  "global": {"type-1": <object>}}
    for mode, objects in object_tables.items():
        # TODO: This method will redefine multiple times for objects in
        #   multiple tables.
        for object_ in objects:
            # `object_` structure:
            # {"name": <str>,
            #  "available-actions": <List[action_set]>}
            object_name = object_["name"]
            speakable_name = utils.spoken_form(object_name)
            action_sets = object_["available-actions"]

            # Emacs uses "mark", so manually add another selection command
            mark_command = f"it-mark-{object_name}"
            simple_commands[f"select {speakable_name}"] = mark_command
            simple_commands[f"sell {speakable_name}"] = mark_command
            for action_set in action_sets:
                # `action_set` structure:
                # {"action": <str>,
                #  "command": <str>,
                #  "takes-prefix": <bool>}
                target_map = (
                    prefix_commands if action_set["takes-prefix"] else simple_commands
                )
                # Just a super simp spoken form for now.
                action = action_set["action"]
                # TODO: Cache this? Regenerating for every object.
                speakable_action = action_command(action)
                emacs_command = action_set["command"]
                # Long command
                long_command = f"{speakable_action} {speakable_name}"
                target_map[long_command] = emacs_command
                # Short command
                for short_command in short_commands(object_name, action):
                    # HACK: Special commands for wrapping that can take a character.
                    # TODO: Make regular wrap available eventually
                    if action == "it-wrap":
                        wrap_commands[short_command] = object_name
                    else:
                        target_map[short_command] = emacs_command
    return simple_commands, prefix_commands, wrap_commands


def update_objects(state):
    global context
    tables = state.get(IT_OBJECTS_KEY, {})
    simple_commands, prefix_commands, wrap_commands = object_bindings(tables)
    LOGGER.debug(f"Dynamic simple commands update:\n{simple_commands}")
    context.lists["user.emacs_object_commands"] = simple_commands
    LOGGER.debug(f"Dynamic prefix commands update:\n{prefix_commands}")
    context.lists["user.emacs_object_prefix_commands"] = prefix_commands
    LOGGER.debug(f"Wrappping commands update:\n{wrap_commands}")
    context.lists["user.emacs_object_wrapping_commands"] = wrap_commands


emacs_state.hook_key(IT_OBJECTS_KEY, update_objects)
