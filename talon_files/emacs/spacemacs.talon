tag: emacs
user.emacs-is-spacemacs: True
-
## Text Alignment
align <user.character>: user.spacemacs_align(character)
align (math|operator): user.emacs_command("spacemacs/align-repeat-math-oper")
align regex: user.emacs_command("spacemacs/align-repeat")

## Navigation
action(user.emacs_find_definition): user.emacs_command("spacemacs/jump-to-definition")

## Unsorted
# TODO: Why use Spacemacs' indirection?
[toggle] debug on error: user.emacs_command("spacemacs/toggle-debug-on-error")

[(buff | buffer)] scratch:  user.emacs_command("spacemacs/switch-to-scratch-buffer")
[(buff | buffer)] messages: user.emacs_command("spacemacs/switch-to-messages-buffer")
# TODO: Pop mesages

action(user.emacs_restart): user.emacs_command("spacemacs/restart-emacs-resume-layouts")
action(user.emacs_exit):    user.emacs_command("spacemacs/prompt-kill-emacs")
