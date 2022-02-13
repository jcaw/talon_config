os: windows
-
run <user.dictation>:
    key(super-s)
    sleep(200ms)
    insert(dictation)

key(ctrl-win-t):  user.quit_talon()
key(ctrl-alt-t):  user.restart_talon()
quit talon:       user.quit_talon()
restart talon:    user.restart_talon()
