app: /emacs/
-
# Fundamental Commands

# "c-g" is the interrupt command. It's hardcoded in C - can't remap it.
(cancel | can): key(ctrl-g)
# Triple esc will get us out of any context
# TODO: Settle on one of these
(reset | rescue): key(esc esc esc)
prefix: user.emacs_prefix()
prefix <number>: user.emacs_prefix(number)
prefix dash: user.emacs_prefix("-")
meta: key(alt-x)
meta <user.chunked_phrase>$:
    key(alt-x)
    user.insert_chunked(chunked_phrase, "lowercase")


# Mark ring
mark: user.emacs_command("set-mark-command")
(park | pop mark): user.emacs_prefix_command("set-mark-command")
swark: user.emacs_command("exchange-point-and-mark")
[pop] glock: user.emacs_command("pop-global-mark")
region: user.emacs_command("voicemacs-toggle-region")
(mark | park) ring: user.emacs_command("helm-all-mark-rings")
glock ring: user.emacs_command("helm-global-mark-ring")


# Scrolling
cursor top <user.optional_number>:
    user.emacs_prefix_command("evil-scroll-line-to-top", optional_number)
cursor bottom <user.optional_number>:
    user.emacs_prefix_command("evil-scroll-line-to-bottom", optional_number)
cursor (middle | center) <user.optional_number>:
    user.emacs_prefix_command("evil-scroll-line-to-center", optional_number)
scroll top: user.emacs_command("beginning-of-buffer")
scroll bottom: user.emacs_command("end-of-buffer")
# TODO: Scroll up/down by single lines


# Windows
other [(window | win)]: user.emacs_command("other-window")
(close | kill) (window | win): user.emacs_command("delete-window")
(close | kill) other (windows | wins): user.emacs_command("delete-other-windows")
balance [(windows | wins)]: user.emacs_command("balance-windows")
# TODO: Fallbacks
split horizontal: user.emacs_command("spacemacs/split-window-horizontally-and-switch")
split vertical: user.emacs_command("spacemacs/split-window-vertically-and-switch")
toggle (windows | wins): user.emacs_command("spacemacs/window-layout-toggle")
# TODO: Extract window directions
move (window | win) left: user.emacs_command("evil-window-move-far-left")
move (window | win) right: user.emacs_command("evil-window-move-far-right")
move (window | win) top: user.emacs_command("evil-window-move-very-top")
move (window | win) bottom: user.emacs_command("evil-window-move-very-bottom")


# Buffers
# TODO: Fallbacks
[switch] (buffer | buff): user.emacs_command("spacemacs-layouts/non-restricted-buffer-list-helm")
[switch] (buffer | buff) <user.chunked_phrase>$:
    user.emacs_command("spacemacs-layouts/non-restricted-buffer-list-helm")
    user.insert_chunked(chunked_phrase, "lowercase")
(close | kill) (buffer | buff): user.emacs_command("kill-this-buffer")
(close | kill) other (buffer | buff): user.emacs_command("kill-this-buffer")
(next | neck) (buffer | buff): user.emacs_command("next-buffer")
(last | larse) (buffer | buff): user.emacs_command("previous-buffer")

# Macros
record [macro]: user.emacs_command("kmacro-start-macro")
finish [macro]: user.emacs_command("kmacro-finish-macro")
# Macros are slow. Might cause RPC to become unresponsive. Use prefix to repeat
# rather than repeating the call, otherwise later calls could time out.
[call] macro <user.optional_number>:
    user.emacs_command("kmacro-call-macro", optional_number)
(last | larse) macro: user.emacs_command("kmacro-cycle-ring-previous")
(next | neck) macro: user.emacs_command("kmacro-cycle-ring-next")
store macro: user.emacs_command("kmacro-to-register")


# TODO: Stuff to sort elsewhere
pop (message | messages): user.emacs_command("popwin:messages")
(close | kill) pop (win | window): user.emacs_command("popwin:close-popup-window")

set theme: user.emacs_command("spacemacs/helm-themes")


# TODO: Stuff to pull to more generic modules.
open [file]: user.open_file()
action(edit.select_all):
    user.emacs_command("mark-whole-buffer")


# TODO: Generic Unsorted
#
# TODO: Fallbacks
action(user.toggle_comment): user.emacs_command("spacemacs/comment-or-uncomment-lines")
reflow:
    user.emacs_command("end-of-line")
    user.emacs_command("fill-paragraph")
tight reflow: user.emacs_command("jcaw-fill-this-line")
action(edit.zoom_in): user.emacs_command("voicemacs-increase-text")
action(edit.zoom_out): user.emacs_command("voicemacs-dencrease-text")
action(edit.save): user.emacs_command("save-buffer")
# TODO: save as
# action(edit.save_as): user.emacs_command("")
action(edit.save_all): user.emacs_command("save-some-buffers")

# TODO: Fallbacks
[show] kill ring: user.emacs_command("helm-show-kill-ring")

dired: user.emacs_command("dired-jump")
dired other: user.emacs_command("dired-jump-other-window")

# TODO: Perform the next "switch-to-buffer" command in the other window.
# with other: user.emacs_command("")

# Double ctrl-c means "submit", but the binding is context dependent. Easier to
# just bind the keypress than try and bind each implementation.
submit: key(ctrl-c ctrl-c)
discard: key(ctrl-c ctrl-k)

(next | neck) error | nerror: user.next_error()
(last | larse) error | larror: user.previous_error()

scratch [(buff | buffer)]: user.emacs_command("spacemacs/switch-to-scratch-buffer")
messages [(buff | buffer)]: user.emacs_command("spacemacs/switch-to-messages-buffer")

(rectangle | rect): user.emacs_command("rectangle-mark-mode")
