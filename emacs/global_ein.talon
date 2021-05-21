tag: user.emacs
-
notebook (start | run) [server]: user.emacs_command("ein:run")
notebook (stop | exit):  user.emacs_command("ein:stop")
notebook login:          user.emacs_command("ein:login")
notebook traceback:      user.emacs_command("ein:tb-show")
notebook open:           user.emacs_command("ein:notebook-open")
notebook (close | kill): user.emacs_command("ein:notebook-close")
notebook menu:           user.emacs_command("ein:notebook-menu")
