import talon
from talon import cron, Module, Context, actions

key = actions.key
user = actions.user


windows_context = Context()
windows_context.matches = "os: windows"


def keypress(spec: str):
    return lambda: key(spec)


def bind():
    actions.user.vimfinity_bind_keys(
        {
            "P": "Powertoys",
            "p r": (keypress("win-shift-m"), "On-Screen Ruler - Toggle"),
            "p a": (keypress("win-ctrl-t"), "Always on Top - Toggle"),
            "p p": (keypress("win-shift-v"), "Advanced Paste Window"),
            "p v": (keypress("win-ctrl-alt-v"), "Paste as Plain Text"),
            "p c": (keypress("win-shift-c"), "Color Picker"),
            "p l": (keypress("win-ctrl-shift-t"), "Crop and Lock - Thumbnail"),
            "p L": (keypress("win-ctrl-shift-r"), "Crop and Lock - Reparent"),
            "p z": (keypress("win-shift-'"), "FancyZones Editor"),
            "p H": (keypress("win-shift-h"), "Mouse Highlighter - Toggle"),
            "p R": (keypress("alt-space"), "Run"),
            "p s": (keypress("win-shift-/"), "Shorcuts Guide"),
            "p t": (keypress("win-shift-t"), "Text Extractor"),
            "p w": (keypress("win-ctrl-'"), "Workspaces"),
        },
        windows_context,
    )


cron.after("100ms", bind)
