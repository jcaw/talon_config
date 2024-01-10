from typing import Optional

from talon import Module, ui, actions, Context, app, clip

user = actions.user
edit = actions.edit
insert = actions.insert
key = actions.key
sleep = actions.sleep

CHATGPT_TITLE = "https://chat.openai.com/"


module = Module()


# TODO: Make these conditional on ChatGPT being active?
@module.action_class
class Actions:
    def chatgpt_ensure_focussed():
        """Ensure ChatGPT is currently focussed."""
        window = ui.active_window()
        assert CHATGPT_TITLE in window.title, window

    def chatgpt_focus_input():
        """When ChatGPT website is focussed, focus the input box."""
        key("shift-esc")

    def chatgpt_new_chat_shortcut():
        """When ChatGPT website is focussed, use this to start a new chat."""
        key("ctrl-shift-o")

    def chatgpt_custom_instructions_shortcut():
        """When ChatGPT website is focussed, open the custom instructions menu."""
        key("ctrl-shift-i")

    def chatgpt_set_specific_instructions(info: str = "", instructions: str = ""):
        """When ChatGPT website is focussed, set the instructions."""
        actions.self.chatgpt_ensure_focussed()
        actions.self.chatgpt_custom_instructions_shortcut()
        edit.select_all()
        user.paste_insert(info)
        key("tab")
        edit.select_all()
        user.paste_insert(instructions)
        key("tab:2")
        key("enter")
        # TODO: Condition on focussed accessible element?
        sleep("1s")

    def chatgpt_switch_start():
        """Switch to the dedicated ChatGPT window, or start a new one if it doesn't exist."""
        try:
            # Note there should be a dedicated ChatGPT window for all of this.
            # ChatGPT is so useful that's fine.
            actions.user.focus(app_name="firefox", title=CHATGPT_TITLE)
            sleep("200ms")
        except (IndexError, ui.UIErr) as e:
            user.open_firefox()
            # Open a new, dedicated ChatGPT window
            # FIXME: This is always starting a new window
            # key("ctrl-n")
            # TODO: Different on Mac?
            browser.focus_address()
            sleep("200ms")
            insert("https://chat.openai.com/")
            key("enter")
            sleep("2000ms")

    def chatgpt_send_message(text: str, submit: bool = True):
        """When ChatGPT website is focussed, send a message."""
        actions.self.chatgpt_focus_input()
        edit.select_all()

        # If there's already a message, store it on the clipboard.
        with clip.capture() as c:
            edit.copy()
        try:
            text = c.text()
            if text:
                app.notify(
                    "Talon - Existing Message Found",
                    "The existing message has been copied to the clipboard.",
                )
                clip.set_text(text)
        except clip.NoChange:
            pass

        user.paste_insert(text)
        if submit:
            key("enter")

    def chatgpt_submit_to_new_chat(
        text: str,
        submit: bool = True,
        info: Optional[str] = None,
        instructions: Optional[str] = None,
    ):
        """Create a new chat and send `text`."""
        actions.self.chatgpt_switch_start()
        if info or instructions:
            actions.self.chatgpt_set_specific_instructions(
                info or "", instructions or ""
            )
        actions.self.chatgpt_new_chat_shortcut()
        sleep("500ms")
        actions.self.chatgpt_send_message(text, submit)

    def chatgpt_submit_to_current_chat(text: str, submit: bool = True):
        """Open ChatGPT, and insert `text` into the current chat."""
        actions.self.chatgpt_switch_start()
        actions.self.chatgpt_send_message(text, submit)

    def chatgpt_explain_thing():
        """Explain the currently"""
        text = actions.user.get_that_dwim()
        actions.self.chatgpt_submit_to_new_chat(
            f"Please explain the following:\n\n```\n{text}\n```"
        )
