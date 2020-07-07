# Ignore repeats that occur as the first element, to stop hallucinated repeats.
^<number>: print("Got repeat {number} without prior command, ignoring.")

(start | search ) program | search windows [<phrase>]:
    key(win-s)
    insert(phrase)

(refresh | reload) words: user.update_custom_words()
