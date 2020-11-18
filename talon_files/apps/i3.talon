tag: user.i3
-
(work | wok) <number>:       key("super-{number}")
move (work | work) <number>: key("super-shift-{number}")
flip [wok | work]:           key("super-tab")
(win | window) <user.arrow>: key("super-{arrow}")
move (win | window) <user.arrow>: key("super-shift-{arrow}")

run <user.dictation>:
    key("super-d")
    sleep(200ms)
    insert(dictation)
run program:
    key("super-d")
    sleep(200ms)

resize [win | window]: key("super-r")

(I three help | [I three] cheatsheet): key("super-f1")

restart I three:    key("super-R")
reload I three:     key("super-C")
exit I three:       key("super-E")
confirm logout:     key("super-E")
new term:           key("super-enter")
[split] vertical:   key("super-h")
[split] horizontal: key("super-v")
layout stacking:    key("super-s")
layout tabbed:      key("super-w")
layout split:       key("super-e")
lock screen:        key("super-x")
[toggle] borders:   key("ctrl-shift-x")
[toggle] (floating | tiling): key("super-shift-space")
(focus | kiss) (floating | tiling): key("super-space")

# TODO: Probably extract this
update packages:    key("super-shift-u")

action(user.toggle_fullscreen): key(f11)
action(app.window_close):       key(super-shift-q)
