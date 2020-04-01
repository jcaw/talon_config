app: /emacs/
user.emacs-minor-modes: /,company-mode,/
user.emacs-company-prompt-open: True
-
^<number>: self.emacs_company_complete(number)
pick <number>: self.emacs_company_complete(number)
pick that: self.emacs_command("company-complete")
move <number>: self.emacs_company_highlight(number)
(doc | dock) <number>: self.emacs_company_show_doc(number)
