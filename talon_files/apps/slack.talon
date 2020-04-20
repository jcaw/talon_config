app: /.*slack\.exe/
app: slack
-
# TODO: Pull actions into linux/windows module?
# Actions

action(user.next_channel): key(alt-down)
action(user.previous_channel): key(alt-up)
# TODO: Pull safe newline into its own action?
# TODO: Pull markdown code block into a generic action?
action(user.code_block):
    "```"
    key(shift-enter shift-enter)
    "```"
    key(up)
action(user.mark_all_channels_read): key(shift-esc)
action(user.mark_channel_read): key(esc)


# Commands

# Basic Navigation
(next | neck) channel: user.next_channel()
(last | larse) channel: user.previous_channel()
(next | neck) unread [channel]: user.next_unread_channel()
(last | larse) unread [channel]: user.previous_unread_channel()

# Quick Move
[jump] channel [<user.dictation>]: user.slack_switch_channel(dictation)
[switch] room <number>: user.slack_switch_room(number)

messages: user.slack_messages()
threads: user.slack_threads()
history: user.slack_history()
activity: user.slack_activity()
directory: user.slack_directory()
(stars | starred): user.slack_starred_items()
[show] unread: user.chat_unread()

# Misc
channel info: user.slack_channel_info()
mark all read: user.mark_all_channels_read()
mark [(this | channel)] read: user.mark_channel_read()
[attach] snippet: user.slack_attach_snippet()
edit (last | larse) [message]: user.edit_last_message()
