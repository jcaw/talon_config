os: windows
os: linux
os: mac
tag: user.tiling_window_manager
-
(work | wok) <user.digit>:                  user.tiling_switch_workspace(digit)
move (work | wok) <user.digit>:             user.tiling_move_workspace_and_switch(digit)
throw (work | wok) <user.digit>:            user.tiling_move_workspace_no_switch(digit)
flip [work | wok]:                          user.tiling_flip_workspace()

(win | window) <user.arrow>:                user.tiling_focus_direction(arrow)
# Compensate for common mishearing
^one <user.arrow>:                          user.tiling_focus_direction(arrow)
switch:                                     user.tiling_switch_window()
# Provide "snap" to match regular WM commands
(move (win | window) | snap) <user.arrow>:  user.tiling_move_direction(arrow)
[split] vertical:                           user.tiling_split_vertical()
[split] horizontal:                         user.tiling_split_horizontal()

resize [win | window]:                      user.tiling_resize_mode()
[toggle] (floating | tiling):               user.tiling_toggle_floating()
# TODO: Decide whether these are generic or i3-specific
# layout stacking:        key("super-s")
# layout tabbed:          key("super-w")
# layout (split | tiled): key("super-e")
