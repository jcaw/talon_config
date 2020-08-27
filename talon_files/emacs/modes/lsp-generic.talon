# Generic actions powered by LSP
app: emacs
user.emacs-minor-mode: lsp-mode
# Doom overrides with its own behaviour
not user.emacs-is-doom: True
# TODO: Spacemacs may override with its own behaviour, check at some point
# not user.emacs-is-spacemacs: True
-
(follow | definition | nishion): user.emacs_command("lsp-find-definition")
(refs | references): user.emacs_command("lsp-find-references")
(impal | implementation): user.emacs_command("lsp-find-implementation")
type (def | definition): user.emacs_command("lsp-find-type-definition")
docs: user.emacs_command("lsp-describe-thing-at-point")
pop doc: user.emacs_command("lsp-ui-doc-glance")
