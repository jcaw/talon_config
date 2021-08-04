[start] pomodoro:                user.pomodoro_start("W", 25 * 60)
[start] pomodoro <number>:       user.pomodoro_start("W", number * 60)
start (rest | break):            user.pomodoro_start("B", 5 * 60)
[start] (rest | break) <number>: user.pomodoro_start("B", number * 60)

pause pomodoro:                  user.pomodoro_pause()
(unpause | resume) pomodoro:     user.pomodoro_unpause()
(cancel | stop) pomodoro:        user.pomodoro_cancel()
