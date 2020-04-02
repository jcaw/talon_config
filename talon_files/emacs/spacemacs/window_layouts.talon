app: /emacs/
user.emacs-is-spacemacs: True
-
# Commands to pop various basic window layouts
(win | window) (split | layout) (one | single) [column]: user.emacs_command("spacemacs/window-split-single-column")
(win | window) (split | layout) (two | double) [columns]: user.emacs_command("spacemacs/window-split-double-columns")
(win | window) (split | layout) (three | triple) [columns]: user.emacs_command("spacemacs/window-split-triple-columns")
(win | window) (split | layout) (grid | four): user.emacs_command("spacemacs/window-split-grid")
# Custom function - not in Spacemacs by default
(win | window) (split | layout) ([(two | double)] rows | five): user.emacs_command("spacemacs/window-split-double-rows")
