os: windows
-
run <user.dictation>:
    key(super-s)
    sleep(200ms)
    insert(dictation)

# TODO: Maybe generalise these keypresses, make them universal across platforms?
#   Not sure if there would be any conflicts doing that.
key(ctrl-win-t):  user.quit_talon_with_sound()
key(ctrl-alt-t):  user.restart_talon_with_sound()
