tag: user.emacs
-
eval defun: user.emacs_command("eval-defun")
eval (last|that|thing): user.emacs_command("eval-last-sexp")
# FIXME
eval (that | thing) <number>: user.emacs_prefix_command("eval-current-bracketed-sexp", number)
eval region: user.emacs_command("eval-region")
eval [expression]: user.emacs_command("eval-expression")
eval (buff|buffer): user.emacs_command("eval-buffer")
eval [and] print: user.emacs_command("eval-print-last-sexp")
