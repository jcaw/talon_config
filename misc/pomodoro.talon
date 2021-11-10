# Pass time in seconds
[start] (timer | pomodoro):            user.pomodoro_start("W", 25 * 60)
[start] (timer | pomodoro) <number>:   user.pomodoro_start("W", number * 60)
start (rest | break):                  user.pomodoro_start("B", 5 * 60)
start (rest | break) <number>:       user.pomodoro_start("B", number * 60)

pause (timer | pomodoro):              user.pomodoro_pause()
(unpause | resume) (timer | pomodoro): user.pomodoro_unpause()
(cancel | stop) (timer | pomodoro):    user.pomodoro_cancel()
