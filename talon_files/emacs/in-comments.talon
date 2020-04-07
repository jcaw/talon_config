app: /emacs/
user.emacs-in-comment: True
-
# Allow free dictation when the cursor is in a comment
^<user.dictation>$: user.insert_natural(dictation)
