tag: emacs
-
replace: user.emacs_command("replace-string")
i search [<user.complex_phrase>$]:
    key("C-s")
    user.complex_insert(complex_phrase, "lowercase")
# Is this necessary?
i search forward [<user.complex_phrase>$]:
    key("C-s")
    user.complex_insert(complex_phrase, "lowercase")
i search backward [<user.complex_phrase>$]:
    key("C-r")
    user.insert_complex(complex_phrase, "lowercase")
