app: /emacs/
user.emacs-minor-modes: isearch-mode
-
(forward | for): user.emacs_command("isearch-repeat-forward")
(backward | back): user.emacs_command("isearch-repeat-backward")
action(user.on_pop): user.emacs_command("voicemacs-isearch-dwim")
cancel: user.emacs_command("isearch-cancel")
