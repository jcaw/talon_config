tag: user.emacs
user.emacs-major-mode: c-mode
user.emacs-major-mode: c++-mode
-
include: "#include "
# TODO: "stand"?
standard [<user.complex_phrase>]$:
    insert("std::")
    user.insert_complex(complex_phrase, "c_path")
