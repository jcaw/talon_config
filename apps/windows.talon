os: windows
-
run <user.dictation>:
    key(super-s)
    sleep(200ms)
    insert(dictation)

# Shows the Windows Task View (virtual desktops and open windows)
(panel|panels): key("win-tab")

# TODO: Maybe generalise these keypresses, make them universal across platforms?
#   Not sure if there would be any conflicts doing that.
# NOTE: For now, it's disabled due to frequent keybind conflict messages
# key(ctrl-win-t):  user.quit_talon_with_sound()
key(ctrl-alt-win-t):   user.quit_talon_with_sound()
key(ctrl-alt-t):  user.restart_talon_with_sound()
