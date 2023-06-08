# Global commands for manipulating active Talon modes
mode: all
-
(snore | sleep)$:
    user.sleep()
    user.play_thunk()
