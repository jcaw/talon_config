# # File from knausj_talon:
# #
# # https://github.com/knausj85/knausj_talon/blob/5e599b2f7633d6aeba18603b3911e4def760bfed/code/history.py

# import threading

# from talon import imgui, Module, Context, speech_system, actions, app, cron

# DEFAULT_MESSAGE = "< Listening... >"
# HISTORY_SIZE = 400
# history = []
# history_lock = threading.Lock()

# module = Module()
# context = Context()

# n_items = module.setting(
#     "command_history_items",
#     int,
#     desc="Number of items to display in the command history window.",
#     default=30,
# )
# auto_hide_delay = module.setting(
#     "command_history_auto_hide",
#     int,
#     desc="Time in seconds do display the command history window before hiding.",
#     default=10,
# )

# # Whether the gui should currently be shown or not. Shouldn't access this
# # directly - use the actions for enabling & disabling.
# gui_enabled = False

# # Tracks the last phrase for auto-hide
# phrase_nonce = 0


# def maybe_hide(nonce):
#     """Hide the GUI if the last phrase matches `nonce`.

#     Run this on a timer to auto-hide the gui.

#     """
#     if nonce == phrase_nonce:
#         gui.hide()


# def reset_gui_timer():
#     global phrase_nonce
#     if gui_enabled:
#         phrase_nonce += 1
#         nonce = phrase_nonce
#         gui.show()
#         # NOTE: Commented out so there's no auto-hide. I'm also not sure
#         #   auto-hiding even works.
#         # cron.after(f"{auto_hide_delay.get()}s", lambda: maybe_hide(nonce))


# def on_phrase(j):
#     global history, history_lock

#     try:
#         word_list = getattr(j["parsed"], "_unmapped", j["phrase"])
#     except:
#         word_list = j["phrase"]

#     if word_list:
#         # Strip Dragon formatting
#         # TODO: Is stripping Dragon formatting still necessary?
#         phrase = " ".join(word.split("\\")[0] for word in word_list)
#         with history_lock:
#             history = [phrase] + history
#             history = history[:HISTORY_SIZE]
#         reset_gui_timer()


# # todo: dynamic rect?
# @imgui.open()
# def gui(gui: imgui.GUI):
#     global history, history_lock
#     print(gui)
#     with history_lock:
#         text = history[: n_items.get()]
#     for i, line in enumerate(text or [DEFAULT_MESSAGE]):
#         # TODO: Show later history items with a paler color?
#         # Add 1 to i because "prior" will increase by 1?
#         gui.text(f"{i+1}: {line}")


# speech_system.register("phrase", on_phrase)


# @module.action_class
# class Actions:
#     def command_history_toggle():
#         """Toggles viewing the command history"""
#         if gui_enabled:
#             actions.self.command_history_disable()
#         else:
#             actions.self.command_history_enable()

#     def command_history_enable():
#         """Shows the command_history"""
#         global gui_enabled
#         gui_enabled = True
#         reset_gui_timer()

#     def command_history_disable():
#         """Hides the command_history"""
#         global gui_enabled
#         gui_enabled = False
#         gui.hide()

#     def command_history_clear():
#         """Clear the command_history"""
#         global history, history_lock
#         with history_lock:
#             history = []

#     def command_history_set_size(n: int):
#         """Set number of items displayed in the command history."""
#         context.settings["user.command_history_items"] = n


# # Enable command history by default.
# #
# # Commented out because subtitles perform this functionality
# # app.register("launch", lambda: actions.self.command_history_enable())
