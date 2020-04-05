((nil . (
         ))
 (python-mode . ((eval . (blacken-mode 1))
                 ;; Some backends cause Flycheck to create temp .py files. Talon
                 ;; will try and auto-load them, causing problems. Blunt
                 ;; solution is to disable it outright.
                 (eval . (flycheck-mode 0))
                 )))
