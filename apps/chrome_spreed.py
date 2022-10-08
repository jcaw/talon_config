from talon import Context, actions
ctx = Context()
ctx.matches = r"""
# Commands for the spreed speed-reading addon for Chrome
app: /chrome/
title: /^Spreed/
"""

@ctx.action_class('edit')
class EditActions:
    def zoom_in():  actions.key('up')
    def zoom_out(): actions.key('down')
