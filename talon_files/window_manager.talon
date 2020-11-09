(minimize | mini): app.window_hide()
(maximize | maxi): user.maximize()
quit program: app.window_close()
(next | neck) (window | win): app.window_next()
(last | larse) (window | win): app.window_previous()
(new | open) (window | win): app.window_open()
[show] programs: user.all_programs()
fullscreen: user.toggle_fullscreen()

(focus | cooss | kiss | cuss | curse) <user.running_applications>:
    user.switcher_focus(running_applications)
(list | show) running: user.switcher_list_running()
(kill | close | hide) running: user.switcher_hide_running()


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
