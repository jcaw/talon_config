"""Module for very small app implementations

"""

from talon import Context, actions

key = actions.key
insert = actions.insert

gimp_context = Context()
gimp_context.matches = r"""
app: /gimp/
"""


@gimp_context.action_class("user")
class GimpUserActions:
    def fullscreen():
        key("f11")
