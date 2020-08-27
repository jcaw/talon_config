# Global commands for manipulating active Talon modes
mode: all
-
(snore | snow):
    speech.disable()
    user.play_thunk()
^wake$:
    speech.enable()
    user.play_glass_tap()
