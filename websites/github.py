from talon import actions, Context, clip

import re
from user.plugins.vimfinity.vimfinity import vimfinity_bind_keys


browser_context = Context()
browser_context.matches = r"""
tag: user.browser
"""


def github_switch_between_repo_and_io_page():
    url = actions.user.browser_address_backup()

    io_regex = r"([a-zA-Z0-9-_]+).github.io\/([a-zA-Z0-9-_]+)"
    com_regex = r"github.com\/([a-zA-Z0-9-_]+)\/([a-zA-Z0-9-_]+)"

    io_result = re.search(io_regex, url)
    if io_result:
        new_url = f"github.com/{io_result.group(1)}/{io_result.group(2)}"
    else:
        com_result = re.search(com_regex, url)
        if com_result:
            new_url = f"{com_result.group(1)}.github.io/{com_result.group(2)}"
        else:
            raise RuntimeError("No compatible github URL found.")

    # HACK: Not implemented at time of writing - instead do it manually.
    # actions.browser.go(current_url)
    with clip.revert():
        clip.set_text(new_url)
        actions.edit.paste()
        actions.sleep("300ms")
        actions.key("enter")


vimfinity_bind_keys(
    {
        "p -": (github_switch_between_repo_and_io_page, "Github toggle IO page"),
    }
)
