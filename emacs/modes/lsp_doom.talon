# Generic actions powered by LSP
tag: user.emacs
user.emacs-minor-mode: lsp-mode
# Doom overrides with its own behaviour
not user.emacs-is-doom: True
# TODO: Spacemacs may override with its own behaviour, maybe check at some point
# not user.emacs-is-spacemacs: True
-
type (def | definition): user.emacs_command("lsp-find-type-definition")
# TODO: Extract this probably
pop doc: user.emacs_command("lsp-ui-doc-glance")
