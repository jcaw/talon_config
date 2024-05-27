import re

from talon import Module, Context, actions, clip, cron, ui

from user.plugins.accessibility_automator.accessibility_automator import (
    AutomationOverlay,
    Spec,
    ElementNotFoundError,
)

user = actions.user
key = actions.key


module = Module()
module.tag(
    "youtube",
    "Active when the browser is focussed and on YouTube.",
)


def add_video_to_yt_dlg():
    # The yt-dlg GUI seems to have no heirarchy - every element is top-level so we search for elements from top-level.
    url = user.browser_address_backup()
    started_new = user.switch_or_start("yt-dlg", focus_name="YouTube Downloader GUI")
    if not started_new:
        # Focussed existing instance - so we need to ensure it's in the correct
        # state to receive input.
        actions.sleep("200ms")
        if ui.active_window().title == "Info":
            key("enter")
        user.automator_click_element([Spec(name="Enter URLs below", class_name="Edit")])
    user.paste_insert(url)
    # HACK: It's faster to just backtab once, even though that might be janky.
    key("shift-tab")
    key("enter")
    # user.automator_click_element([Spec(name="Add", class_name="Button")])


@module.action_class
class Actions:
    def youtube_toggle_short() -> None:
        """Switch between a short and the video player, for the same video."""
        # Get the URL
        # HACK: Not implemented at time of writing - instead do it manually.
        # url = actions.browser.address()
        url = user.browser_address_backup()

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
        key("enter")

    def youtube_queue_with_yt_dlg():
        """Download the current YouTube video using `yt-dlg`."""
        with AutomationOverlay():
            original_window = ui.active_window()

            add_video_to_yt_dlg()

            original_window.focus()

    def youtube_download_with_yt_dlg():
        """Download the current YouTube video using `yt-dlg`, to the default yt-dlg folder."""
        with AutomationOverlay():
            original_window = ui.active_window()

            add_video_to_yt_dlg()

            # HACK: The download button is labelled extremely generically
            #  (name="", class_name="Button"), so we can't really get it with
            #  the UI automator. It's labelled too ambiguously. Instead we'll
            #  try tabbing to it.
            key("shift-tab:3")
            key("enter")

            original_window.focus()


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
            "p d": (
                actions.user.youtube_download_with_yt_dlg,
                "Download Video With yt-dlg",
            ),
            "p q": (
                actions.user.youtube_queue_with_yt_dlg,
                "Add Video to yt-dlg Queue",
            ),
        },
        context,
    )


cron.after("50ms", bind_vimfinity_keys)
