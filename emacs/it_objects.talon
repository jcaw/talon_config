tag: user.emacs
-
# HACK: I think the flash feedback in Voicemacs causes a redisplay, which causes
#   the RPC "surrounding_text" call to be processed. To fix that we just
#   artificially wait after all Voicemacs commands.
#
# TODO: Probably add an explicit check to see if this is OK?

{user.emacs_object_commands}:
    user.emacs_command(emacs_object_commands)
    sleep(500ms)
{user.emacs_object_prefix_commands} [<number>]:
    user.emacs_prefix_command(emacs_object_prefix_commands, number or 0)
    sleep(500ms)

action(edit.select_line): user.emacs_command("it-mark-line")

# TODO: Maybe make a nicer system than this
{user.emacs_object_wrapping_commands} <user.character>:
    user.emacs_wrap_object(emacs_object_wrapping_commands, character)
    sleep(500ms)


(copy | cop) (that | thing):
    user.emacs_command("it-copy-dwim")
    sleep(500ms)
kill (that | thing):
    user.emacs_command("it-kill-dwim")
    sleep(500ms)
(sell | select | mark) (that | thing):
    user.emacs_command("it-mark-dwim")
    sleep(500ms)
