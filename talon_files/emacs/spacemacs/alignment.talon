app: /emacs/
user.emacs-is-spacemacs: True
-
align <user.character>: user.spacemacs_align(character)
align (math|operator): user.emacs_command("spacemacs/align-repeat-math-oper")
align regex: user.emacs_command("spacemacs/align-repeat")
