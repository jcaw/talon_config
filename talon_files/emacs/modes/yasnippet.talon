app: /emacs/
user.emacs-minor-mode: yas-global-mode
user.emacs-minor-mode: yas-minor-mode
-
# Dynamic snippets
# TODO: Dynamic snippets
nip <user.emacs_snippet>: user.emacs_insert_yasnippet(emacs_snippet)

add (snippet | nip): user.emacs_command("yas-new-snippet")
edit (snippet | nip): user.emacs_command("yas-visit-snippet-file")
expand [(snippet | nip)]: user.emacs_command("yas-expand")
# TODO: Maybe require being in a snippet?
exit [(snippet | nip)]: user.emacs_command("yas-exit-snippet")
describe (sippets | nips): user.emacs_command("yas-describe-tables")
skip [field]: user.emacs_command("yas-skip-and-clear-or-delete-char")
((next | neck) field | nefield): user.emacs_command("yas-next-field")
((last | larse) field | lafield): user.emacs_command("yas-prev-field")
(cancel|abort) (snippet | nip): user.emacs_command("yas-abort-snippet")
