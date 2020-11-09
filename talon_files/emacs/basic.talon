tag: user.emacs
# HACK: Tag extraction like this doesn't override OS based stuff, so manually
#   specify it.
os: windows
os: linux
os: mac
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
meta <user.complex_phrase>$:
    key(alt-x)
    user.insert_complex(complex_phrase, "lowercase")


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
(buffer | buff):
    user.emacs_switch_buffer()
(buffer | buff) <user.complex_phrase>$:
    user.emacs_switch_buffer()
    user.insert_complex(complex_phrase, "lowercase")
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


# Indentation
dent [<number>]: user.emacs_prefix_command("voicemacs-relative-indent", number or 0)
indent [<number>]: user.emacs_prefix_command("voicemacs-indent-rigidly-right", number or 1)
dedent [<number>]: user.emacs_prefix_command("voicemacs-indent-rigidly-left", number or 1)


# ---------------------------------------------------------------------------

# Unsorted

# TODO: Stuff to sort elsewhere
pop (message | messages): user.emacs_command("popwin:messages")
(close | kill) pop (win | window): user.emacs_command("popwin:close-popup-window")

set theme [<user.dictation>]:
    user.emacs_switch_theme()
    user.insert_lowercase(dictation or "")

# TODO: Stuff to pull to more generic modules.
open [file]: user.open_file()
open [file] <user.dictation>:
    user.open_file()
    insert(dictation)
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
save and kill:
    edit.save()
    user.emacs_command("kill-this-buffer")
# TODO: save as
# action(edit.save_as): user.emacs_command("")
# FIXME: Doesn't work, "wrong type argument, listp". RPC problem?
# action(edit.save_all): user.emacs_command("save-some-buffers")
# Fall back to keypress for now. Should work everywhere anyway, who rebinds
# this?
action(edit.save_all): key(ctrl-x s)

# TODO: Fallbacks
[show] kill ring: user.emacs_command("helm-show-kill-ring")

# Wav2letter has trouble with "dired". Add alternate pronunciation.
(dired | dyad | folder): user.emacs_command("dired-jump")
(dired | dyad | folder) other: user.emacs_command("dired-jump-other-window")

# TODO: Perform the next "switch-to-buffer" command in the other window.
# with other: user.emacs_command("")

# Double `ctrl-c` means "submit", but the specific command varies based on
# context. Easier to just bind the keypress than try and bind each
# implementation.
submit:  key(ctrl-c ctrl-c)
discard: key(ctrl-c ctrl-k)

(next | neck) error | nerror:  user.next_error()
(last | larse) error | larror: user.previous_error()

(rectangle | rect): user.emacs_command("rectangle-mark-mode")


# Kill to a specific character
zap <user.character> [<number>]:
    user.emacs_prefix_command("zap-up-to-char", number or 1)
    key(character)
zapley <user.character> [<number>]:
    user.emacs_prefix_command("zap-to-char", number or 1)
    key(character)
bazap <user.character> [<number>]:
    number = number or 1
    user.emacs_prefix_command("zap-up-to-char", number * -1)
    key(character)
bazapley <user.character> [<number>]:
    number = number or 1
    user.emacs_prefix_command("zap-to-char", number * -1)
    key(character)


[toggle] debug on error: user.emacs_command("toggle-debug-on-error")

# Add trailing comment
trail [<user.complex_phrase>]$:
    user.emacs_command("comment-indent")
    user.insert_complex(complex_phrase or "", "capitalized_sentence")

shell command: user.emacs_command("async-shell-command")

# Break out & insert a block, in languages like Java & C++
bleak: key(home end space { enter)
