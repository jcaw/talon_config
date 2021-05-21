# Generic actions powered by LSP
tag: user.emacs
user.emacs-minor-mode: lsp-mode
# Doom overrides with its own behaviour
not user.emacs-is-doom: True
# TODO: Spacemacs may override with its own behaviour, maybe check at some point
# not user.emacs-is-spacemacs: True
-
action(user.find_definition): user.emacs_command("lsp-find-definition")
action(user.find_references): user.emacs_command("lsp-find-references")
action(user.find_implementations): user.emacs_command("lsp-find-implementation")
type (def | definition): user.emacs_command("lsp-find-type-definition")
action(user.show_documentation): user.emacs_command("lsp-describe-thing-at-point")
# TODO: Extract this probably
pop doc: user.emacs_command("lsp-ui-doc-glance")
