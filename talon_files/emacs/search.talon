tag: emacs
-
replace: user.emacs_command("replace-string")
i search [forward] [<user.complex_phrase>]$:
    user.emacs_isearch_forward()
    user.insert_complex(complex_phrase or "", "lowercase")
i search backward [<user.complex_phrase>]$:
    user.emacs_isearch_backward()
    user.insert_complex(complex_phrase or "", "lowercase")
