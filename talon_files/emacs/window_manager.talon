tag: user.emacs
-
# These commands are from Spacemacs, but I've extracted them into my own config.
#
# Commands to pop various basic window layouts
split (one | single) [column]: user.emacs_command("spacemacs/window-split-single-column")
split (two | double) [columns]: user.emacs_command("spacemacs/window-split-double-columns")
split (three | triple) [columns]: user.emacs_command("spacemacs/window-split-triple-columns")
split (four | grid): user.emacs_command("spacemacs/window-split-grid")
# Custom function - not in Spacemacs by default
split ([(two | double)] rows | five): user.emacs_command("jcaw-spacemacs/window-split-double-rows")
