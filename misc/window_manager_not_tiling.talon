# Window manager bindings that should be global, except in tiling WMs like i3.
not tag: user.i3
-
(minimize | mini): app.window_hide()
(maximize | maxi): user.maximize()
(next | neck) (window | win): app.window_next()
(last | larse) (window | win): app.window_previous()
(new | open) (window | win): app.window_open()


snap <user.window_snap_position>: user.snap_window(window_snap_position)
[snap] screen left: user.move_window_next_screen()
[snap] screen right: user.move_window_previous_screen()
[snap] screen <number>: user.move_window_to_screen(number)
swap [screen] <number>: user.swap_screens(number)
swap [screens] <number> and <number>: user.swap_screens(number_1, number_2)
<user.running_applications> snap <user.window_snap_position>:
    user.snap_app(running_applications, window_snap_position)
<user.running_applications> [screen] <number>:
    user.move_app_to_screen(running_applications, number)
