# Ignore repeats that occur as the first element, to stop hallucinated repeats.
^<number>: print("Got repeat {number} without prior command, ignoring.")

# TODO: Extract to Windows module
(start | search ) program | search windows [<phrase>]:
    key(win-s)
    insert(phrase)

(refresh | reload) words: user.update_custom_words()

<user.file_suffix>: insert(file_suffix)

# We'll want to use this in all sorts of places
(interrupt | cease): key(ctrl-c)
