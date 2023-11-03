from talon import Module, Context


module = Module()
module.tag("chrome", "Active when Chrome is in focus.")


context = Context()
context.matches = r"""
app: /chrome/
title: /Google Chrome/
"""
context.tags = ["user.chrome"]
