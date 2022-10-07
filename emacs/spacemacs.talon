tag: user.emacs
user.emacs-is-spacemacs: True
-
## Text Alignment
align <user.character>: user.spacemacs_align(character)
align (math|operator): user.emacs_command("spacemacs/align-repeat-math-oper")
align regex: user.emacs_command("spacemacs/align-repeat")

## Unsorted
# TODO: Why use Spacemacs' indirection?
[toggle] debug on error: user.emacs_command("spacemacs/toggle-debug-on-error")

(buff | buffer) scratch:  user.emacs_command("spacemacs/switch-to-scratch-buffer")
(buff | buffer) messages: user.emacs_command("spacemacs/switch-to-messages-buffer")
