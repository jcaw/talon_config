(print | copy | get) actions:  user.print_copy_actions()
(print | copy | get) captures: user.print_copy_captures()
(print | copy | get) settings: user.print_copy_settings()
(print | copy | get) mouse:    user.print_mouse_positions()

# Useful when dragon hangs. Say "mic check", it'll ping when it's ready.
(mic | mike) (test | check): user.mic_test()

(copy app | app info): user.copy_current_app_info()
