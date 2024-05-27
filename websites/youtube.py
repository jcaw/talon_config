import re

from talon import Module, Context, actions, clip, cron


module = Module()
module.tag(
    "youtube",
    "Active when the browser is focussed and on YouTube.",
)


@module.action_class
class Actions:
    def youtube_toggle_short() -> None:
        """Switch between a short and the video player, for the same video."""
        # Get the URL
        # HACK: Not implemented at time of writing - instead do it manually.
        # url = actions.browser.address()
        url = actions.user.browser_address_backup()

        short_regex = r"www.youtube.com\/shorts/"
        video_regex = r"www.youtube.com\/watch\?v\="
        if re.search(short_regex, url):
            new_url = url.replace("/shorts/", r"/watch?v=")
        elif re.search(video_regex, url):
            new_url = url.replace("/watch?v=", "/shorts/")
        else:
            RuntimeError("YouTube video not detected in URL.")

        # Navigate to the newer version of the URL
        # HACK: Not implemented at time of writing - instead do it manually.
        # actions.browser.go(current_url)
        clip.set_text(new_url)
        actions.edit.paste()
        actions.key("enter")


context = Context()
context.matches = r"""
tag: user.browser
title: / - YouTube/
"""
context.tags = ["user.youtube"]


def bind_vimfinity_keys():
    actions.user.vimfinity_bind_keys(
        {
            "p s": (actions.user.youtube_toggle_short, "Switch between Video & Short"),
        },
        context,
    )


cron.after("50ms", bind_vimfinity_keys)
