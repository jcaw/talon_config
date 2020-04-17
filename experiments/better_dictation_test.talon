<user.formatted_phrase>+$:
    mode.enable("user.formatting")
    user.insert_formatted_phrases(formatted_phrase_list)
<user.formatted_phrase>+ over:
    user.insert_formatted_phrases(formatted_phrase_list)
    # Just in case the mode-specific capture is eaten.
    mode.disable("user.formatting")
