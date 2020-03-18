os: windows
os: linux
app: /.*slack\.exe/
app: slack
-

action(user.slack_messages): key(ctrl-shift-k)
action(user.slack_threads): key(ctrl-shift-t)
action(user.slack_history): key(TODO)
action(user.slack_forward): key(TODO)
action(user.slack_activity): key(ctrl-shift-m)
action(user.slack_directory): key(ctrl-shift-e)
action(user.slack_starred_items): key(ctrl-shift-s)
action(user.slack_unread): key(TODO maybe ctrl-j)

action(user.next_unread_channel): key(alt-shift-down)
action(user.previous_unread_channel): key(alt-shift-up)
action(edit.search): key(ctrl-j)

action(user.slack_attach_snippet): key(ctrl-shift-enter)

action(user.fullscreen): key(ctrl-shift-f)

# TODO: Extract
action(user.edit_last_message): key(ctrl-up)
action(user.toggle_bullets): key(ctrl-shift-8)
action(user.toggle_number_list): key(ctrl-shift-7)
action(user.toggle_quote): key(ctrl-shift->)
action(user.upload_file): key(ctrl-u)
action(user.list_app_shortcuts): key(ctrl-/)
action(user.toggle_bold): key(ctrl-b)
action(user.toggle_italic): key(ctrl-i)
action(user.toggle_strikethrough): key(ctrl-shift-x)
