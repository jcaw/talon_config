tag: emacs
-
# FIXME: This command only takes one char. Allow it to take many?
(jump | jum) <user.any_key>+$: user.emacs_jump(any_key_list)
grab <user.any_key>$:
    user.emacs_command("voicemacs-avy-copy")
    key(any_key)
kill <user.any_key>$:
    user.emacs_command("voicemacs-avy-kill")
    key(any_key)
(teleport | telly) <user.any_key>$:
    user.emacs_command("voicemacs-avy-teleport")
    key(any_key)
put <user.any_key>$:
    user.emacs_command("voicemacs-avy-yank")
    key(any_key)
(pluck | bring) <user.any_key>$:
    user.emacs_command("voicemacs-avy-duplicate")
    key(any_key)
pad <user.any_key>$:
    user.emacs_command("voicemacs-avy-pad")
    key(any_key)
