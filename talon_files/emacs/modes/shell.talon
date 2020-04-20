app: /emacs/
user.emacs-major-mode: shell-mode
-
# TODO: Extract comint features to comint file

((last | larse) input | lanput): user.emacs_command("comint-previous-input")
((next | neck) input | nenput): user.emacs_command("comint-next-input")
# TODO: Move to current input
(input | bottom | output end): user.emacs_command("comint-show-maximum-output")
# TODO: input + dictation?
input <user.open_formatted_phrases>:
    user.emacs_command("comint-show-maximum-output")
    # TODO: Maybe clear?
    user.insert_many_formatted(open_formatted_phrases)
(clear | kill) input: user.emacs_command("comint-kill-input")
interrupt [shell]: user.emacs_command("comint-interrupt-subjob")
stop shell: user.emacs_command("comint-stop-subjob")
kill shell: user.emacs_command("comint-quit-subjob")
(kill | clear) output: user.emacs_command("comint-delete-output")
output start: user.emacs_command("comint-show-output")
save output: user.emacs_command("comint-write-output")
# FIXME: Doesn't work on Windows
set [shell] (dir | directory): user.emacs_command("dirs")
(silent | invisible) [input]: user.emacs_command("send-invisible")
truncate [(buffer | shell)]: user.emacs_command("comint-truncate-buffer")

# TODO: safe newline
