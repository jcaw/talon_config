tag: emacs
user.emacs-is-spacemacs: True
-
## Text Alignment
align <user.character>: user.spacemacs_align(character)
align (math|operator): user.emacs_command("spacemacs/align-repeat-math-oper")
align regex: user.emacs_command("spacemacs/align-repeat")


## Window Layouts
# Commands to pop various basic window layouts
split (one | single) [column]: user.emacs_command("spacemacs/window-split-single-column")
split (two | double) [columns]: user.emacs_command("spacemacs/window-split-double-columns")
split (three | triple) [columns]: user.emacs_command("spacemacs/window-split-triple-columns")
split (four | grid): user.emacs_command("spacemacs/window-split-grid")
# Custom function - not in Spacemacs by default
split ([(two | double)] rows | five): user.emacs_command("spacemacs/window-split-double-rows")


## Misc
set theme [<user.dictation>]:
    user.emacs_command("spacemacs/helm-themes")
    user.insert_lowercase(dictation or "")
[toggle] debug on error: user.emacs_command("spacemacs/toggle-debug-on-error")
(follow | definition | nishion ): user.emacs_command("spacemacs/jump-to-definition")
backtrack: user.emacs_command("pop-tag-mark")
