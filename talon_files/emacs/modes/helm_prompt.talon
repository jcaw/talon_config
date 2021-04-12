tag: user.emacs
user.emacs-in-helm-prompt: True
-
^<number>:
    user.emacs_helm_command("helm-confirm-and-exit-minibuffer", number)
# TODO: Probably pull common number commands out?
move <number>: user.emacs_helm_goto_line(number)
pick [<number>]:
    user.emacs_helm_goto_line(number or 0)
    user.emacs_helm_command("helm-confirm-and-exit-minibuffer")
follow [<number>]:
    user.emacs_helm_goto_line(number or 0)
    user.emacs_helm_command("helm-next-source")
mark [<number>]:
    user.emacs_helm_goto_line(number or 0)
    user.emacs_helm_command("helm-toggle-visible-mark")

# When we need to submit an empty prompt
(submit | empty): user.emacs_command("helm-cr-empty-string")
actions [<number>]:
    user.emacs_helm_goto_line(number or 0)
    user.emacs_helm_command("helm-select-action")
