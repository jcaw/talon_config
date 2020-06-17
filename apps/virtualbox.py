from talon import Context

from user.games.utils import switch_input

windows_input_context = Context()
windows_input_context.matches = r"""
os: windows
app: /VirtualBoxVM/
"""

switch_input.switch_to_keyboard_module(windows_input_context)
