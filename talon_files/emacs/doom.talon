tag: emacs
user.emacs-is-doom: True
-
## Text Alignment
# TODO: Port Spacemacs text alignment
# align <user.character>: user.spacemacs_align(character)
# align (math|operator): user.emacs_command("spacemacs/align-repeat-math-oper")
# align regex: user.emacs_command("spacemacs/align-repeat")

action(user.emacs_restart): user.emacs_command("doom/restart-and-restore")
action(user.emacs_quit): user.emacs_command("save-buffers-kill-terminal")


# Code Lookup
action(user.find_definition): user.emacs_command("+lookup/definition")
action(user.find_definition_other_window):
    user.emacs_command("+lookup/definition-other-window")
action(user.find_references): user.emacs_command("+lookup/references")
action(user.find_references_other_window):
    user.emacs_command("+lookup/references-other-window")
action(user.find_implementations): user.emacs_command("+lookup/implementations")
action(user.find_implementations_other_window):
    user.emacs_command("+lookup/implementations-other-window")
action(user.show_documentation): user.emacs_command("+lookup/documentation")


# Generic Lookup
# TODO: Good command for this?
lookup [<user.complex_phrase>]:
    user.emacs_command("+lookup/online")
    user.insert_complex(complex_phrase or "")
pick lookup: user.emacs_command("+lookup/online-select")
# FIXME: Doesn't work
synonyms: user.emacs_command("+lookup/synonyms")
dictionary: user.emacs_command("+lookup/dictionary-definition")

# TODO: lookup file: user.emacs_command("+lookup/file")
