# Anchor or over means dictation will eat everything after it, but we can still
# overcome that behavior if necessary.
<user.formatted_phrases>$:
    user.insert_many_formatted(formatted_phrases)
<user.formatted_phrases> over:
    user.insert_many_formatted(formatted_phrases)

<user.formatters> <number>:
    user.reformat_left(formatters, number)
