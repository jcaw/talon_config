tag: user.emacs
-
python shell:
    user.emacs_command("run-python")
    # user.emacs_command("python-shell-switch-to-shell")
restart python:
    user.emacs_command("jcaw-python-force-kill-repl")
    user.emacs_Command("run-python")
