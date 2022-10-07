app: /slack/
app: /discord/
-

# TODO: Safe newline action
newline: key(shift-enter)

mark all read: user.mark_all_channels_read()
mark [(this | channel)] read: user.mark_channel_read()

(next | neck) channel: user.next_channel()
(last | larse) channel: user.previous_channel()
(next | neck) (unn | unread) [channel]: user.next_unread_channel()
(last | larse) (unn | unread) [channel]: user.previous_unread_channel()
