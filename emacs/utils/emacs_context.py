from talon import Context


emacs_context = Context()
emacs_context.matches = """
# Most OSes
app: /emacs/

# Cygwin X on Windows, displaying WSL Emacs
app: /XWin/
and title: /^emacs@/
"""
emacs_context.tags = ["emacs"]
