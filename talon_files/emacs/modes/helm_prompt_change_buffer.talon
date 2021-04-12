tag: user.emacs
user.emacs-in-helm-prompt: True
# Heuristic, just assume these are buffer change prompts
user.emacs-helm-title: /Buffer/
user.emacs-helm-title: /buffer/
user.emacs-helm-title: /Recentf/
-
(close | kill) (buffer | buff):   user.emacs_helm_command("helm-buffer-run-kill-buffers")
(close | kill) (buffers | buffs): user.emacs_helm_command("helm-buffer-run-kill-buffers")
