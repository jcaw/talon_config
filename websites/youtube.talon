tag: user.browser
title: /- YouTube/
# Homepage
title: YouTube/
# Not every command will work on other players, but it's an easy way to enable
# them.
title: /- Vimeo/
-
play [(video | vid)]: key("k")
pause [(video | vid)]: key("k")
# TODO: Extract for twitch? (. and ,)
speed up: key(">")
(speed | slow) down: key("<")
(max | full) speed: user.video_2x_speed()
reset speed | speed reset: user.video_1x_speed()
(mid | medium) speed: user.video_1halfx_speed()
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
