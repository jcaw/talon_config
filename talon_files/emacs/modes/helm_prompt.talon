tag: user.emacs
user.emacs-in-helm-prompt: True
-
^<number>:
    user.emacs_helm_command("helm-confirm-and-exit-minibuffer", number)
# TODO: Probably pull common number commands out?
move [<number>]: user.emacs_helm_goto_line(number)
pick <user.optional_number>:
    user.emacs_helm_command("helm-confirm-and-exit-minibuffer", optional_number)
follow <user.optional_number>:
    user.emacs_helm_command("helm-next-source", optional_number)
mark <user.optional_number>:
    user.emacs_helm_command("helm-toggle-visible-mark", optional_number)

# When we need to submit an empty prompt
(submit | empty): user.emacs_command("helm-cr-empty-string")
actions <user.optional_number>:
    user.emacs_helm_command("helm-select-action", optional_number)
