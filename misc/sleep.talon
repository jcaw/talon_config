mode: sleep
-
^<phrase>$: user.play_thunk()
# TODO: Visual indicator when asleep?
^[talon] wake$:
    user.wake()
    user.play_glass_tap()
