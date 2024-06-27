import re

from talon import Module, Context, actions, clip, cron, ui


user = actions.user
key = actions.key
automator_overlay = actions.user.automator_overlay
automator_spec = actions.user.automator_spec
automator_find_elements = actions.user.automator_find_elements


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
        user.automator_click_element(
            [automator_spec(name="Enter URLs below", class_name="Edit")]
        )
    user.paste_insert(url)
    # HACK: It's faster to just backtab once, even though that might be janky.
    #   Another theoretical option is to use ocr - `user.ocr_click_in_window("^Add$")`
    user.ocr_click_in_window("^Add$")
    # key("shift-tab")
    # key("enter")
    # user.automator_click_element([automator_spec(name="Add", class_name="Button")])


@module.action_class
class Actions:
    def youtube_toggle_short() -> None:
        """Switch between a short and the video player, for the same video."""
        with automator_overlay():
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
        with automator_overlay():
            original_window = ui.active_window()

            add_video_to_yt_dlg()

            original_window.focus()

    def youtube_download_with_yt_dlg():
        """Download the current YouTube video using `yt-dlg`, to the default yt-dlg folder."""
        with automator_overlay():
            original_window = ui.active_window()

            add_video_to_yt_dlg()

            # HACK: The download button is labelled extremely generically
            #  (name="", class_name="Button"), so we can't really get it with
            #  the UI automator. It's labelled too ambiguously. Instead we'll
            #  try tabbing to it.
            key("shift-tab:3")
            key("enter")

            original_window.focus()

    # TODO: Extract
    def video_2x_speed():
        """Set the current video to play at 2x speed."""

    # TODO: Extract
    def video_1x_speed():
        """Set the current video to play at normal, 1x speed."""

    def video_1halfx_speed():
        """Set the video to 1.5x speed."""

    def youtube_save_to_watch_later():
        """Save the current video to the `Watch Later` playlist."""
        # Firefox path to the YouTube video page.
        with automator_overlay():
            title = ui.active_window().title
            tab_title = title[: -len(" - Mozilla Firefox")]
            page_specs = [
                automator_spec(
                    # name="Mozilla Firefox$",
                    name=title,
                    class_name="MozillaWindowClass",
                    search_indirect=False,
                ),
                automator_spec(name=tab_title, class_name="^$", search_indirect=True),
            ]
            page_elements = list(automator_find_elements(page_specs))
            if not page_elements:
                raise RuntimeError(title)
            save_to_playlist_specs = [
                automator_spec(
                    name="Save to playlist", class_name="^$", search_indirect=True
                )
            ]
            save_to_playlist_element = next(
                iter(automator_find_elements(save_to_playlist_specs, page_elements))
            )


context = Context()
context.matches = r"""
tag: user.browser
title: / - YouTube/
"""
context.tags = ["user.youtube"]


@context.action_class("user")
class YouTubeActions:
    def video_2x_speed():
        # Will hit the max regardless
        key(">:7")

    def video_1x_speed():
        # Go to min, then max
        key("<:7")
        key(">:3")

    def video_1halfx_speed():
        actions.user.video_normal_speed()
        key(">:2")


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
            "p .": (actions.user.video_2x_speed, "2x Video Speed"),
            "p ,": (actions.user.video_1x_speed, "1x Video Speed"),
            "p m": (actions.user.video_1halfx_speed, "1.5x Video Speed"),
            "p w": (actions.user.youtube_save_to_watch_later, "Save to Watch Later"),
        },
        context,
    )


cron.after("50ms", bind_vimfinity_keys)
