# Anchor or over means dictation will eat everything after it, but we can still
# overcome that behavior if necessary.
<user.formatters> <user.complex_phrase>$:
    user.insert_complex(complex_phrase, formatters)
<user.formatters> <user.complex_phrase> over:
    user.insert_complex(complex_phrase, formatters)

<user.formatters> <user.digit>:
    user.reformat_left(formatters, digit)
