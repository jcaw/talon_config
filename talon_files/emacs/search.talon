app: /emacs/
-
action(edit.find): user.emacs_command("helm-swoop")
action(user.search): user.emacs_command("spacemacs/helm-project-smart-do-search")
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
