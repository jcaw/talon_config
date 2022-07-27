tag: user.emacs
# HACK: Tag extraction like this doesn't override OS based stuff, so manually
#   specify it.
os: windows
os: linux
os: mac
-
# TODO: Avoid races with keyboard input and remote input via Voicemacs.
# settings:
#    key_wait = 100


# Fundamental Commands

# "c-g" is the interrupt command. It's hardcoded in C - can't remap it.
action(user.cancel): key(ctrl-g)
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
# cursor top [<number>]:
#     user.emacs_prefix_command("evil-scroll-line-to-top", number or 0)
cursor top [<number>]: user.emacs_prefix_command("recenter", number or 1)
# cursor bottom [<number>]:
#     user.emacs_prefix_command("evil-scroll-line-to-bottom", number or 0)
cursor bottom [<number>]:
    pos = number or 1
    pos = -1 * pos
    user.emacs_prefix_command("recenter", pos)
cursor (middle | center) [<number>]:
    user.emacs_prefix_command("evil-scroll-line-to-center", number or 0)
# TODO: Scroll up/down by single lines


# Windows
other [(window | win)]: user.emacs_command("other-window")
(close | kill) (window | win): user.emacs_command("delete-window")
single: user.emacs_command("delete-other-windows")
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


# Macros
record [macro]: user.emacs_command("kmacro-start-macro")
finish [macro]: user.emacs_command("kmacro-end-macro")
# Macros are slow. Might cause RPC to become unresponsive. Use prefix to repeat
# rather than repeating the call, otherwise later calls could time out.
[call] macro [<number>]:
    user.emacs_prefix_command("kmacro-end-or-call-macro", number or 0)
(last | larse) macro: user.emacs_command("kmacro-cycle-ring-previous")
(next | neck) macro: user.emacs_command("kmacro-cycle-ring-next")
store macro: user.emacs_command("kmacro-to-register")


# Indentation
dent [<number>]: user.emacs_prefix_command("voicemacs-relative-indent", number or 0)
indent [<number>]: user.emacs_prefix_command("voicemacs-indent-rigidly-right", number or 1)
dedent [<number>]: user.emacs_prefix_command("voicemacs-indent-rigidly-left", number or 1)


# Folding
fold: user.emacs_toggle_fold()
hide: user.emacs_fold()
show: user.emacs_unfold()
hide all: user.emacs_fold_all()
show all: user.emacs_unfold_all()
(next | neck) fold: user.emacs_next_fold()
(last | lass) fold: user.emacs_previous_fold()


# ---------------------------------------------------------------------------

# Unsorted

# TODO: Stuff to sort elsewhere
[pop] (message | messages): user.emacs_command("popwin:messages")
(close | kill) pop (win | window): user.emacs_command("popwin:close-popup-window")

restart voicemacs:
    key(alt-x)
    insert("voicemacs-mode")
    sleep(1s)
    key(enter)
    key(alt-x)
    insert("voicemacs-mode")
    sleep(1s)
    key(enter)

(set | load) theme [<user.dictation>]:
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
tight [reflow | flow]: user.emacs_command("jcaw-fill-this-line")
action(edit.zoom_in): user.emacs_command("voicemacs-increase-text")
action(edit.zoom_out): user.emacs_command("voicemacs-decrease-text")
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

# TODO 1: Just use ferror/berror for these?
(next | neck) error:  user.next_error()
(last | larse) error: user.previous_error()

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

# Break out & insert a {} block, in languages like Java & C++
bleak:
    key(home end)
    user.emacs_command("just-one-space")
    key("{ enter")

action(edit.undo): user.emacs_command("undo-fu-only-undo")
action(edit.redo): user.emacs_command("undo-fu-only-redo")

^restart emacs$: user.emacs_restart()

move up:   user.emacs_command("drag-stuff-up")
move down: user.emacs_command("drag-stuff-down")

(switch | toggle) (quotes | string): user.emacs_command("jcaw-toggle-string-quotes")
# TODO: What's the command to join across lines like this?
flush: user.emacs_command("just-one-space")

(tran | transpose): user.emacs_command("transpose-chars")

ediff [buffers]: user.emacs_command("ediff-buffers")

# Jump to the last stacktrace link
comper [<number>]: user.emacs_prefix_command("jcaw-jump-to-compile-hyperlink", number or 1)

ferror: user.emacs_command("next-error")
berror: user.emacs_command("previous-error")
first error: user.emacs_command("first-error")

highlight:               user.emacs_command("highlight-symbol-at-point")
(unhighlight | unlight): user.emacs_command("unhighlight-regexp")
