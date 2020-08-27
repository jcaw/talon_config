tag: emacs
user.emacs-minor-modes: isearch-mode
-
(forward | for): key("C-s")
(backward | back): key("C-r")
# TODO: Don't just go forwards, repeat prior
action(user.on_pop): key("C-s")
cancel: user.emacs_command("isearch-cancel")
