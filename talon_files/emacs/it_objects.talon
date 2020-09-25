tag: user.emacs
-
{user.emacs_object_commands}: user.emacs_command(emacs_object_commands)
{user.emacs_object_prefix_commands} <user.optional_number>:
    user.emacs_prefix_command(emacs_object_prefix_commands, optional_number)

action(edit.select_line): user.emacs_command("it-mark-line")

# TODO: Maybe make a nicer system than this
{user.emacs_object_wrapping_commands} <user.character>:
    user.emacs_wrap_object(emacs_object_wrapping_commands, character)


(copy | cop) that: user.emacs_command("it-copy-dwim")
kill that: user.emacs_command("it-kill-dwim")
(sell | select | mark) that: user.emacs_command("it-mark-dwim")
