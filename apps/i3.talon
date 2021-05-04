tag: user.i3
-
(work | wok) <user.digit>:
    key("super-{digit}")
    sleep(100ms)
# Move window to workspace and switch to it
move (work | wok) <user.digit>:
    key("super-shift-{digit}")
    sleep(100ms)
# Move window to workspace without switching to it
throw (work | wok) <user.digit>:
    key("super-ctrl-{digit}")
flip [work | wok]:
    key("super-tab")
    sleep(100ms)
(win | window) <user.arrow>:
    key("super-{arrow}")
# Compensate for common mishearing
^one <user.arrow>:   key("super-{arrow}")
# Provide "snap" to match regular WM commands
(move (win | window) | snap) <user.arrow>: key("super-shift-{arrow}")


run <user.dictation>:
    key("super-d")
    sleep(200ms)
    insert(dictation)
run program:
    key("super-d")
    sleep(200ms)

resize [win | window]:  key("super-r")

(I three help | [I three] cheatsheet): key("super-f1")

restart I three:        key("super-R")
reload I three:         key("super-C")
exit I three:           key("super-E")
confirm logout:         key("super-E")
new term:               key("super-enter")
[split] vertical:       key("super-h")
[split] horizontal:     key("super-v")
layout stacking:        key("super-s")
layout tabbed:          key("super-w")
layout (split | tiled): key("super-e")
([toggle] borders | toggle title):  key("ctrl-shift-x")
[toggle] (floating | tiling):       key("super-shift-space")
(focus | kiss) (floating | tiling): key("super-space")


action(user.toggle_fullscreen): key(f11)
action(app.window_close):       key(super-shift-q)
action(user.lock_screen):       key(super-x)
# Special command, switch between this and the other window. Only going to work
# if there's two windows.
switch:
     key(super-right)
     # Do this in case they're vertically stacked.
     key(super-down)

# Don't tell Aegis (use this when Voicemacs deadlocks)
restart talon:       key("super-shift-t")
(exit | kill) talon: key("super-ctrl-t")
