"""Captures & actions that aren't in a dedicated module yet."""

from talon import Module, Context, actions


module = Module()


@module.action_class
class ModuleActions:
    pass


global_context = Context()


@global_context.action_class
class GlobalActions:
    pass
