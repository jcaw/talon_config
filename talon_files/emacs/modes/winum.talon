app: /emacs/
user.emacs-minor-modes: /,winum-mode,/
-
# NOTE: This will only work with windows up to 10.
(window | win) <number>: user.emacs_command("winum-select-window-{number}")
