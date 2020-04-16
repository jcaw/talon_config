# Anchor or over means dictation will eat everything after it, but we can still
# overcome that behavior if necessary.
# TODO: Uncomment once testing done
# <user.formatters> <user.dictation>$:
#     user.insert_formatted(dictation, formatters)
# <user.formatters> <user.dictation> over:
#     user.insert_formatted(dictation, formatters)
<user.formatters> <number>:
    user.reformat_left(formatters, number)
