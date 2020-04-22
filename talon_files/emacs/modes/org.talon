app: /emacs/
user.emacs-major-mode: org-mode
-
# Basic Structure
heading: user.emacs_command("org-insert-heading-respect-content")
subheading: user.emacs_command("org-insert-subheading")
demote: user.emacs_command("org-metaright")
promote: user.emacs_command("org-metaleft")
move up: user.emacs_command("org-metaup")
move down: user.emacs_command("org-metadown")

# Tasks
status: user.emacs_command("org-todo")
status <user.org_todo_keyword>: user.org_set_todo(org_todo_keyword)
status none | (clear | kill) status: user.org_set_todo("")
priority <user.letter>:
    user.emacs_command("org-priority")
    key(letter)
pririty none | (clear | kill) priority:
    user.emacs_command("org-priority")
    key(space)

# Unsorted
code block [<user.dictation>]: user.org_code_block(dictation or "")
