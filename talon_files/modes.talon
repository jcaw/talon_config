# Global commands for manipulating active Talon modes
mode: all
-
(snore | snow):
    user.sleep()
    user.play_thunk()
^wake$:
    user.wake()
    user.play_glass_tap()
