tag: user.emacs
user.emacs-major-mode: emacs-lisp-mode
user.emacs-major-mode: lisp-interaction-mode
-
test all: key(alt-m m t a)
test (buff | buffer):
    user.emacs_command("eval-buffer")
    key(alt-m m t a)
