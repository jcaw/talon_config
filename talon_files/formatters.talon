# Anchor or over means dictation will eat everything after it, but we can still
# overcome that behavior if necessary.
<user.formatted_dictation>$:
    user.insert_complex(formatted_dictation)
<user.formatted_dictation> over:
    user.insert_complex(formatted_dictation)
<user.formatters> <number>:
    user.reformat_left(formatters, number)
