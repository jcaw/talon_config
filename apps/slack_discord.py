from talon import Context, actions
ctx = Context()
ctx.matches = r"""
app: /slack/
app: /discord/
"""

@ctx.action_class('user')
class UserActions:
    # Actions
    def next_channel() -> None:            actions.key('alt-down')
    def previous_channel() -> None:        actions.key('alt-up')
    def mark_all_channels_read() -> None:  actions.key('shift-esc')
    def mark_channel_read() -> None:       actions.key('esc')
    def next_unread_channel() -> None:     actions.key('alt-shift-down')
    def previous_unread_channel() -> None: actions.key('alt-shift-up')
