tag: user.emacs
-
# FIXME: This command only takes one char. Allow it to take many?
(jump | jum) <user.any_key>$: user.emacs_jump(any_key)
(jump | jum) <user.any_key> <user.any_key>+$: user.emacs_jump_chars(any_key_list)
# More powerful jump - jump anywhere (e.g. inside words)
jump in <user.any_key>$:
    user.emacs_command("avy-goto-char")
    key(any_key)
grab <user.any_key>$:
    user.emacs_command("voicemacs-avy-copy")
    key(any_key)
kill <user.any_key>$:
    user.emacs_command("voicemacs-avy-kill")
    key(any_key)
(sell | select | mark) <user.any_key>$:
    user.emacs_command("voicemacs-avy-mark")
    key(any_key)
(teleport | telly) <user.any_key>$:
    user.emacs_command("voicemacs-avy-teleport")
    key(any_key)
place <user.any_key>$:
    user.emacs_command("voicemacs-avy-yank")
    key(any_key)
(pluck | bring | kate) <user.any_key>$:
    user.emacs_command("voicemacs-avy-duplicate")
    key(any_key)
pad <user.any_key>$:
    user.emacs_command("voicemacs-avy-pad")
    key(any_key)
