app: /.*slack\.exe/
app: slack
-
# Commands

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
[attach] snippet: user.slack_attach_snippet()
edit (last | larse) [message]: user.edit_last_message()
