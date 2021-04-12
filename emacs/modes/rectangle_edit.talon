tag: user.emacs
emacs.emacs-minor-mode: rectangle-edit-mode
-
action(edit.cut): user.emacs_command("kill-rectangle")
action(edit.copy): user.emacs_command("copy-rectangle-as-kill")
action(edit.paste): user.emacs_command("yank-rectangle")
padding: user.emacs_command("open-rectangle")
number lines: user.emacs_command("rectangle-number-lines")
clear: user.emacs_command("clear-rectangle")
(kill | delete) whitespace: user.emacs_command("delete-whitespace-rectangle")
replace (rect | rectangle): user.emacs_command("string-rectangle")
insert: user.emacs_command("string-insert-rectangle")
