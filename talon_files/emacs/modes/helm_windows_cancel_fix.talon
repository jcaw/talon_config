# TODO: Does the helm cancel bug occur on other OSes?
os: windows
app: /emacs/
user.emacs-in-helm-prompt: True
-
# On Windows, regular keyboard interrupt has to be pressed twice for Helm to
# recognize it and terminate. Emulating the keypress (within Emacs) fixes the
# behavior.
cancel: user.emacs_command("my-simulate-C-g")
