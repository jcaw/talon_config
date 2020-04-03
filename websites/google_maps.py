from talon import Context

from user.games.utils.map_scroll import EyeScroller, KeyMover


hiss_move_context = Context()
hiss_move_context.matches = r"""
app: /firefox/
app: /chrome/
title: /Google Maps/
user.zoom_mouse_zooming: False
"""


key_mover = KeyMover()
map_scroller = EyeScroller(key_mover.do_move)


@hiss_move_context.action_class("user")
class UserActions:
    def on_hiss(start: bool):
        if start:
            map_scroller.start()
        else:
            map_scroller.stop()
