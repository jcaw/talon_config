from typing import List

from talon import Module, Context, actions

from user.plugins.accessibility_automator import accessibility_automator
from user.plugins.accessibility_automator.accessibility_automator import Spec
from user.plugins.vimfinity.vimfinity import vimfinity_bind_keys


key = actions.key


module = Module()
module.tag("firefox", "Enabled when firefox is in focus.")


context = Context()
context.matches = r"""
app: /firefox/
"""
context.tags = ["user.firefox"]


def right_click_action(*sections: List[Spec]):
    key("menu")
    actions.sleep("200ms")

    def click_section(section):
        actions.user.automator_click_element(
            [
                Spec(name="", class_name="MozillaDropShadowWindowClass"),
                *section,
            ]
        )

    for section in sections[:-1]:
        click_section(section)
        actions.sleep("200ms")
    click_section(sections[-1])


@module.action_class
class Action:
    def rango_toggle_keyboard_clicking():
        """Rango browser extension - toggle keyboard clicking on/off."""
        key("ctrl-shift-5")

    def rango_disable():
        """Disable Rango browser extension and stop showing labels."""
        key("ctrl-shift-4")

    def rango_enable():
        """Enable Rango browser extension and start showing labels."""
        key("ctrl-shift-6")

    def instapaper_save_page():
        """Save current page to instapaper."""
        with actions.user.automator_overlay("Saving Page to Instapaper"):
            # HACK: This shortcut doesn't work in firefox, it opens a developer mode
            #   prompt, so we need to manually save. We'll use the right-click menu.
            # key("ctrl-shift-i")
            right_click_action([Spec(name="Save to Instapaper", class_name="")])

    def summarise_page_with_chatgpt():
        """Summarise the current page with ChatGPT."""
        with actions.user.automator_overlay("Instigating ChatGPT Summary"):
            right_click_action(
                [Spec(name="Ask ChatGPT", class_name="")],
                [Spec(name="Summarise Page", class_name="")],
            )

    # TODO: Read aloud


# TODO: Vimfinity shortcuts for rango and read aloud.
vimfinity_bind_keys(
    {
        "e i": (actions.user.instapaper_save_page, "Save Page in Instapaper"),
        "e s": (
            actions.user.summarise_page_with_chatgpt,
            "Summarise Page With ChatGPT",
        ),
    },
    context,
)
