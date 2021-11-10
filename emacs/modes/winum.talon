tag: user.emacs
user.emacs-minor-mode: winum-mode
-
# NOTE: This will only work with windows up to 10.
#
# "wind" is added because "win one" is often misrecognized as "one one"
(window | win | wind) <user.digit>: user.emacs_command("winum-select-window-{digit}")
# FIXME: Doesn't work, "buffer <user.complex_phrase>$" always takes priority.
(buffer | buff) <user.digit>$:
    user.emacs_command("winum-select-window-{number}")
    user.emacs_switch_buffer()
