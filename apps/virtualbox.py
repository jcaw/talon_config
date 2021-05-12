from talon import Context

windows_input_context = Context()
windows_input_context.matches = r"""
os: windows
app: /VirtualBoxVM/
"""

windows_input_context.settings["key_hold"] = 50
windows_input_context.settings["key_wait"] = 20
