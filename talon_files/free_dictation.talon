# Dictation without triggers - dictate anything, outright.
tag: user.free_dictation
-
# FIXME: Adding a start anchor seems to eat everything. This seems to work but
#   it's not ideal.
<user.complex_phrase>$: user.insert_complex(complex_phrase, "sentence")
