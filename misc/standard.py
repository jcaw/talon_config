from talon.voice import Word, Context, Key, Str, press
from talon import app, clip, ui
from talon_init import TALON_HOME, TALON_PLUGINS, TALON_USER
import string
from user.utils import (
    surround,
    parse_words,
    parse_word,
    sentence_text,
    text,
    word,
    ctrl_cmd,
)
from talon.engine import engine
from .vocab import NEXT, PREVIOUS


def engine_update(j):
    engine.cmd("g.update", name="dragon", enabled=False)


engine.register("ready", engine_update)


def copy_bundle(m):
    bundle = ui.active_app().bundle
    clip.set(bundle)
    app.notify("Copied app bundle", body="{}".format(bundle))


ctx = Context("standard")

ctx.vocab = [
    "docker",
    "talon",
    "pragma",
    "pragmas",
    "vim",
    "configs",
    "spotify",
    "upsert",
    "utils",
]

keymap = {}
keymap.update(
    {
        "dragon words": "<dgnwords>",
        "dragon dictation": "<dgndictation>",
        "slap": "enter",
        # "cd": "cd ",
        # "cd talon home": "cd {}\n".format(TALON_HOME),
        # "cd talon user": "cd {}\n".format(TALON_USER),
        # "cd talon [user] emily": "cd {}/emily\n".format(TALON_USER),
        # "cd talon plugins": "cd {}\n".format(TALON_PLUGINS),
        # "talon logs": "cd {} && tail -f talon.log\n".format(TALON_HOME),
        # TODO: How to handle cmd/terminal?
        # "grep": "grep ",
        # "elle ess": "ls ",
        # "run L S": "ls\n",
        # "run (S S H | S H)": "ssh",
        # "S S H": "ssh ",
        # "ack": "ack ",
        # "diff": "diff ",
        # "dot pie": ".py",
        # "run vim": "vim ",
        # "run make": "make\n",
        # "run jobs": "jobs\n",
        # "run make (durr | dear)": "mkdir ",
        # "(jay son | jason )": "json",
        # "(http | htp)": "http",
        # "tls": "tls",
        # "md5": "md5",
        # "(regex | rejex)": "regex",
        # "const": "const ",
        # "static": "static ",
        # TODO: Pull keywords like types out. How to generalize?
        # "tip pent": "int ",
        # "tip char": "char ",
        # "tip byte": "byte ",
        # "tip pent 64": "int64_t ",
        # "tip you went 64": "uint64_t ",
        # "tip pent 32": "int32_t ",
        # "tip you went 32": "uint32_t ",
        # "tip pent 16": "int16_t ",
        # "tip you went 16": "uint16_t ",
        # "tip pent 8": "int8_t ",
        # "tip you went 8": "uint8_t ",
        # "tip size": "size_t",
        # "tip float": "float ",
        # "tip double": "double ",
        # "word queue": "queue",
        # "word eye": "eye",
        # "word bson": "bson",
        # "word iter": "iter",
        # "word no": "NULL",
        # "word cmd": "cmd",
        # "word dup": "dup",
        # "word streak": ["streq()", Key("left")],
        # "word printf": "printf",
        # "word shell": "shell",
        # "word Point2d": "Point2d",
        # "word Point3d": "Point3d",
        # "title Point": "Point",
        # "word angle": "angle",
        "dunder in it": "__init__",
        # "self taught": "self.",
        # "string utf8": "'utf8'",
        # "state past": "pass",
        "shebang bash": "#!/bin/bash -u\n",
        "new window": ctrl_cmd("n"),
        # NEXT + " window": Key("cmd-`"),
        # PREVIOUS + " window": Key("cmd-shift-`"),
        # NEXT + ' app': Key('cmd-tab'),
        # PREVIOUS + ' app': Key('cmd-shift-tab'),
        "new tab": ctrl_cmd("t"),
        NEXT + " tab": Key("ctrl-tab"),
        PREVIOUS + " tab": Key("ctrl-shift-tab"),
        # NEXT + " space": Key("cmd-alt-ctrl-right"),
        # PREVIOUS + " space": Key("cmd-alt-ctrl-left"),
        # TODO: Alternate zoom commands
        # "zoom in": Key("cmd-+"),
        # "zoom out": Key("cmd--"),
        "(page | scroll) up": Key("pgup"),
        "(page | scroll) [down]": Key("pgdown"),
        "copy": ctrl_cmd("c"),
        "cut": ctrl_cmd("x"),
        "paste": ctrl_cmd("v"),
        "(undo | scrap)": ctrl_cmd("z"),
        "redo": ctrl_cmd("shift-z"),
        # "menu help": Key("cmd-shift-?"),
        # "spotlight": Key("cmd-space"),
        # "(bass | clear | scratch )": Key("cmd-backspace"),
        "more bright": Key("brightness_up"),
        "less bright": Key("brightness_down"),
        # "copy active bundle": copy_bundle,
        # "wipe": Key("backspace"),
        "(pad | padding ) ": ["  ", Key("left")],
        "funny": "ha ha",
        # "menubar": Key("ctrl-f2"),
        # "status menu": Key("ctrl-f8"),
        # "my doc": Key("ctrl-f3"),
    }
)

ctx.keymap(keymap)
