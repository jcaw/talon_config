tag: user.emacs
user.emacs-major-mode: dired-mode
-
^<number>: user.emacs_dired_command("dired-find-file", number)
move <number>: user.emacs_dired_highlight(number)
(open | follow) <user.optional_number>:
    user.emacs_dired_command("dired-find-file", optional_number)
[(open | follow)] other <user.optional_number>:
    user.emacs_dired_command("dired-find-file-other-window", optional_number)
(rename | move) <user.optional_number>:
    user.emacs_dired_command("dired-do-rename", optional_number)

# Use "flag" instead of "mark" because we may also want to mark text.
flag <user.optional_number>:
    user.emacs_dired_command("dired-mark", optional_number)
flag all:
    user.emacs_command("dired-mark-files-regexp")
    key("enter")
flag (regex | regexp): user.emacs_command("dired-mark-files-regexp")
unflag <user.optional_number>:
    user.emacs_dired_command("dired-unmark", optional_number)
unflag all: user.emacs_command("dired-unmark-all-marks")

copy [file] <user.optional_number>:
    user.emacs_dired_command("dired-do-copy", optional_number)
flag [to] (delete | kill) <user.optional_number>:
    user.emacs_dired_command("dired-flag-file-deletion", optional_number)
(expunge | (delete | kill) flagged): user.emacs_command("dired-do-delete")
(delete | kill) [file] <user.optional_number>:
    user.emacs_command("dired-unmark-all-marks")
    user.emacs_dired_command("dired-do-delete", optional_number)



# TODO: Maybe allow the word insert? Clashes with the key.
expand <user.optional_number>:
    user.emacs_dired_command("dired-maybe-insert-subdir", optional_number)
shell <user.optional_number>:
    user.emacs_dired_command("dired-do-shell-command", optional_number)

# TODO: To extract
parent: user.emacs_command("dired-up-directory")
(create | new) durr: user.emacs_command("dired-create-directory")
[toggle] (sort | sorting): user.emacs_command("dired-sort-toggle-or-edit")
# TODO: Maybe pull out into Voicemacs?
(create | new) file: user.emacs_command("jcaw-dired-create-file")
refresh: user.emacs_command("revert-buffer")
