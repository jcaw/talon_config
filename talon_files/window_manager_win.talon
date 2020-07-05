os: windows
-
(next | neck) (window | win) <number>:  user.window_next_hold(number)
(last | larse) (window | win) <number>: user.window_previous_hold(number)

snap top:          user.maximize()
snap right:        user.snap_window_win("right right")
snap left:         user.snap_window_win("left left")
snap top right:    user.snap_window_win("right right up")
snap top left:     user.snap_window_win("left left up")
snap bottom right: user.snap_window_win("right right down")
snap bottom left:  user.snap_window_win("left left down")

screen left:       user.snap_screen_win("left")
screen right:      user.snap_screen_win("right")
