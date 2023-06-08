mode: sleep
-
# TODO: Visual indicator when asleep? Like thunk?
^<phrase>$: user.play_thunk()
^[talon] wake$:
    user.wake()
    user.play_glass_tap()
