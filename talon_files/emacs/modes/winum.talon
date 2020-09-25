tag: user.emacs
user.emacs-minor-mode: winum-mode
-
# NOTE: This will only work with windows up to 10.
#
# "wind" is added because "win one" is often misrecognized as "one one"
(window | win | wind) <number>: user.emacs_command("winum-select-window-{number}")
