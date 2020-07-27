tag: emacs
-
replace: user.emacs_command("replace-string")
i search [<user.dictation>]:
    user.emacs_command("voicemacs-isearch-dwim")
    insert (dictation or "")
i search (forward | for) [<user.dictation>]:
    user.emacs_command("voicemacs-isearch-forward")
    insert(dictation or "")
i search (backward | back) [<user.dictation>]:
    user.emacs_command("voicemacs-isearch-backward")
    insert(dictation or "")
