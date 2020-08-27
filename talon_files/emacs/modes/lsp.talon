tag: emacs
user.emacs-minor-mode: lsp-mode
-
# Code modification
#
# TODO: Probably extract to generic action
rename: user.emacs_command("lsp-rename")
rename <user.complex_phrase>:
    user.emacs_command("lsp-rename")
    # It will have a default value, need to clear that.
    user.emacs_command("clear-buffer")
    user.complex_insert(complex_phrase)
(fix | action): user.emacs_command("lsp-execute-code-action")
sort imports: user.emacs_command("lsp-organize-imports")


# Navigation
#
# TODO: Is there another way to do this?
(decal | declaration): user.emacs_command("lsp-find-declaration")
# Like Visual Studio's peeking, pops up in-buffer
peek [def | definition | nishion]: user.emacs_command("lsp-ui-peek-find-definitions")
peek (refs | references): user.emacs_command("lsp-ui-peek-find-references")
peek (sim | symbol): user.emacs_command("lsp-ui-peek-find-workspace-symbol")
# Search
# TODO: Both of these redundant?
search symbol: user.emacs_command("xref-find-apropos")
# TODO: Move these out to helm module?
scout [<user.complex_phrase>]:
    user.emacs_command("helm-lsp-workspace-symbol")
    user.insert_complex(complex_phrase or "")
scout all [<user.complex_phrase>]:
    user.emacs_command("helm-lsp-global-workspace-symbol")
    user.insert_complex(complex_phrase or "")


# Toggles
[toggle] [doc] popups: user.emacs_command("lsp-ui-doc-mode")
[toggle] sideline: user.emacs_command("lsp-ui-sideline-mode")
[toggle] breadcrumbs: user.emacs_command("lsp-headerline-breadcrumb-mode")
[toggle] highlight (symbol | symbols): user.emacs_command("lsp-toggle-symbol-highlight")


# LSP Meta Commands
L S P session: user.emacs_command("lsp-describe-session")
L S P diagnose: user.emacs_command("lsp-diagnose")
L S P lens: user.emacs_command("lsp-lens-mode")
L S P restart: user.emacs_command("lsp-restart-workspace")


# Unsorted
#
# This should be automatic
# highlight: user.emacs_command("lsp-document-highlight")
lens <user.character>:
    user.emacs_command("lsp-avy-lens")
    key(character)
# TODO: Remove this?
signature: user.emacs_command("lsp-signature-activate")
