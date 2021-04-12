tag: user.browser
title: /- YouTube/
-
play [(video | vid)]: key("k")
pause [(video | vid)]: key("k")
# TODO: Extract for twitch? (. and ,)
speed up: key(">")
(speed | slow) down: key("<")
(max | full) speed:
    # Will hit the max regardless
    key(">:7")
reset speed | speed reset:
    # Go to min, then max
    key("<:7")
    key(">:3")
(subtitles | subs | captions): key("c")
(subtitles | subs | captions) size up: key("+")
(subtitles | subs | captions) size down: key("-")
(video | vid) volume up: key("up")
(video | vid) volume down: key("down")
(next | neck) (video | vid): key("shift-n")
(last | larse) (video | vid): key("shift-p")
search (box | bar): key("/")
fullscreen: key("f")
mute (video | vid): key("m")
theater [mode]: key("t")
mini player [mode] | pop out: key("i")
