# Anchor or over means dictation will eat everything after it, but we can still
# overcome that behavior if necessary.
<user.formatter_phrase>$:     user.insert_complex(formatter_phrase)
<user.formatter_phrase> over: user.insert_complex(formatter_phrase)

re <user.formatters> <user.digit>: user.reformat_left(formatters, digit)
rih <user.formatters> <user.digit>: user.reformat_left(formatters, digit)
