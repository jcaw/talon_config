tag: emacs
user.emacs-minor-mode: company-mode
user.emacs-company-prompt-open: True
-
^<number>: user.emacs_company_complete(number)
pick <number>: user.emacs_company_complete(number)
pick that: user.emacs_command("company-complete")
# Overloading this may get confusing, might be better to have a separate command.
(complete | pleat): user.emacs_command("company-complete")
move <number>: user.emacs_company_highlight(number)
(doc | dock) <number>: user.emacs_company_show_doc(number)
