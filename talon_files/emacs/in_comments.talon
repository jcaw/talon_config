app: /emacs/
user.emacs-in-comment: True
-
# Allow free dictation when the cursor is in a comment
^<user.open_formatted_phrases>$: user.insert_many_formatted(open_formatted_phrases)
