from talon import Module, Context

module = Module()
module.list(
    "blender_create_menu_options",
    'Object names mapped to key sequences needed to create them in the "Add" context menu in Blender',
)

context = Context()
context.matches = r"""
app: /blender/
"""

context.lists["user.blender_create_menu_options"] = {
    # Mesh
    "plane": "mp",
    "cube": "mc",
    "circle": "mr",
    "U V sphere": "mu",
    "ico sphere": "mi",
    "cylinder": "my",
    "cone": "mo",
    "torus": "mt",
    # Curve
    "bezier": "cb",
    "circle": "cc",
    "nurbs curve": "cn",
    "nurbs circle": "cu",
    "path": "cp",
    # Surface (all these are nurbs surfaces)
    "surface curve": "sn",
    "surface circle": "sc",
    "surface": "ss",
    "surface cylinder": "su",
    "surface sphere": "sr",
    "surface torus": "st",
    # Mataball
    "meta ball": "bb",
    "meta capsule": "bc",
    "meta plain": "bp",
    "meta ellipsoid": "be",
    "meta cube": "bu",
    # Text
    "text": "t",
    # Volume
    "open V D B": "vi",
    "volume": "ve",
    # Grease Pencil
    "Grease Pencil": "gb",
    "stroke": "gs",
    "monkey": "gm",
    "scene line art": "gl",
    "collection line art": "gc",
    "object line art": "go",
    # Armature
    "armature": "a",
    # Lattice
    "lattice": "l",
    # Empty
    "axes": "ep",
    "arrows": "ea",
    "arrow": "es",
    "empty circle": "ec",
    "empty cube": "eu",
    "empty sphere": "eh",
    "empty cone": "eo",
    "empty image": "ei",
    # Image
    "reference": "ir",
    "background": "ib",
    # Light
    "point light": "hp",
    "sun": "hs",
    "spotlight": "ho",
    "area light": "ha",
    # Light Probe
    "reflection cubemap": "p",
    "reflection plane": "p",
    "irradience volume": "p",
    # Camera
    "camera": "r",
    # Speaker
    "speaker": "k",
    # Force Field
    "force": "ff",
    "wind": "fw",
    "vortex": "fv",
    "magnetic": "fm",
    "harmonic": "fh",
    "charge": "fc",
    "Leonard jones": "fl",
    "force texture": "ft",
    "curve guide": "fg",
    "force boid": "fb",
    "turbulence": "fu",
    "drag": "fd",
    "fluid flow": "fi",
    # Collection Instance
    "collection": "oc",
}
