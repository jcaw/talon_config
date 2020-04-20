app: /emacs/
user.emacs-minor-mode: git-commit-mode
-
# TODO: Extract free dictation enabling into a mode, share the mode
# Commits are mostly natural language - free dictation is desired.
^<user.open_formatted_phrases>$: user.insert_many_formatted(open_formatted_phrases)
