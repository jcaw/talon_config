tag: emacs
-
(follow | definition | nishion): user.find_definition()
(follow | definition | nishion) other: user.find_definition_other_window()
(impal | implementations): user.find_implementations()
(impal | implementations) other:
    user.find_implementations_other_window()
(refer | references): user.find_references()
(refer | references) other:
    user.find_references_other_window()

backtrack: user.emacs_command("pop-tag-mark")
# Hacky, but should work for quick lookups.
backtrack other:
    user.emacs_command("evil-switch-to-windows-last-buffer")
    user.emacs_command("other-window")
    user.emacs_command("pop-tag-mark")

(docs | documentation): user.show_documentation()
