tag: user.emacs
user.emacs-major-mode: prog-mode
-
# Not all languages are semicolon-terminated, but most are and it's easier than
# enumerating them all.
termi:
    edit.line_end()
    key(;)
    key(enter)
# TODO: termi <user.character> (jump to char, termi at end, then pop back)
