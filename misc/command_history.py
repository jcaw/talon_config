# File from knausj_talon:
#
# https://github.com/knausj85/knausj_talon/blob/5e599b2f7633d6aeba18603b3911e4def760bfed/code/history.py

from talon import imgui, Module, Context, speech_system, actions, app, cron

DEFAULT_MESSAGE = "< Listening... >"
HISTORY_SIZE = 400
history = []

module = Module()
context = Context()

n_items = module.setting(
    "command_history_items",
    int,
    desc="Number of items to display in the command history window.",
    default=1,
)
auto_hide_delay = module.setting(
    "command_history_auto_hide",
    int,
    desc="Time in seconds do display the command history window before hiding.",
    default=10,
)

# Whether the gui should currently be shown or not. Shouldn't access this
# directly - use the actions for enabling & disabling.
gui_enabled = False

# Tracks the last phrase for auto-hide
phrase_nonce = 0


def maybe_hide(nonce):
    """Hide the GUI if the last phrase matches `nonce`.

    Run this on a timer to auto-hide the gui.

    """
    if nonce == phrase_nonce:
        gui.hide()


def reset_gui_timer():
    global phrase_nonce
    if gui_enabled:
        phrase_nonce += 1
        nonce = phrase_nonce
        gui.show()
        cron.after(f"{auto_hide_delay.get()}s", lambda: maybe_hide(nonce))


def on_phrase(j):
    global history

    try:
        word_list = getattr(j["parsed"], "_unmapped", j["phrase"])
    except:
        word_list = j["phrase"]

    if word_list:
        # Strip Dragon formatting
        # TODO: Is stripping Dragon formatting still necessary?
        phrase = " ".join(word.split("\\")[0] for word in word_list)
        history.append(phrase)
        history = history[-HISTORY_SIZE:]
        reset_gui_timer()


# todo: dynamic rect?
@imgui.open(y=0)
def gui(gui: imgui.GUI):
    global history
    text = history[-n_items.get() :] or [DEFAULT_MESSAGE]
    for line in text:
        gui.text(line)


speech_system.register("phrase", on_phrase)


@module.action_class
class Actions:
    def command_history_toggle():
        """Toggles viewing the command history"""
        if gui_enabled:
            actions.self.command_history_disable()
        else:
            actions.self.command_history_enable()

    def command_history_enable():
        """Shows the command_history"""
        global gui_enabled
        gui_enabled = True
        reset_gui_timer()

    def command_history_disable():
        """Hides the command_history"""
        global gui_enabled
        gui_enabled = False
        gui.hide()

    def command_history_clear():
        """Clear the command_history"""
        global history
        history = []

    def command_history_set_size(n: int):
        """Set number of items displayed in the command history."""
        context.settings["user.command_history_items"] = n


# Enable command history by default.
app.register("launch", lambda: actions.self.command_history_enable())
