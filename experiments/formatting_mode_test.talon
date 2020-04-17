mode: user.formatting
-
^<user.formatted_phrase_loose>+$:
    user.insert_formatted_phrases(formatted_phrase_loose_list)
^<user.formatted_phrase_loose>+ over:
    user.insert_formatted_phrases(formatted_phrase_loose_list)
    # mode.enable(talon)
    mode.disable("user.formatting")
over:
    mode.disable("user.formatting")
