app: /emacs/
user.emacs-major-mode: org-mode
-
status: user.emacs_command("org-todo")
status <user.org_todo_keyword>: user.org_set_todo(org_todo_keyword)
status none | (clear | kill) status: user.org_set_todo("")
