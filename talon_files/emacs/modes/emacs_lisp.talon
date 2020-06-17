app: /emacs/
user.emacs-major-mode: emacs-lisp-mode
-
test all: key(alt-m m t a)
test (buff | buffer):
    user.emacs_command("eval-buffer")
    key(alt-m m t a)
