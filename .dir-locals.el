((nil . (
         ;; Spacemacs automatically activates talon's venv, causing all
         ;; kinds of problems. Just deactivate it.
         (python-auto-set-local-pyvenv-virtualenv . nil)
         ))
 (python-mode . ((eval . (blacken-mode 1))
                 ;; Some backends cause Flycheck to create temp .py files. Talon
                 ;; will try and auto-load them, causing problems. Blunt
                 ;; solution is to disable it outright.
                 (eval . (flycheck-mode 0))
                 ;; FIXME: Spacemacs automatically activates talon's venv,
                 ;; causing all kinds of problems. Just deactivate it.
                 (eval . (progn
                           (pyvenv-deactivate)
                           (pipenv-deactivate)))
                 )))
