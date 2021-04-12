# Window managemnt commands available in all window managers.
-
# See `window_manager_not_tiling.talon` for commands that are active outside
# tiling WMs like i3. The ones here are global.
quit program: app.window_close()
[show] programs: user.all_programs()
fullscreen: user.toggle_fullscreen()

(focus | cooss | kiss | cuss | curse) <user.running_applications>:
    user.switcher_focus(running_applications)
running (apps | applications) | show [running] (apps | applications):
    user.switcher_list_running()
(kill | close | hide) running [apps | applications]:
    user.switcher_hide_running()

lock screen: user.lock_screen()
