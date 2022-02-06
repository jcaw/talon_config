# Active when editing unity game code or shaders (in Emacs)

tag: user.emacs
user.emacs-major-mode: csharp-mode
user.emacs-major-mode: hlsl-mode
user.emacs-major-mode: glsl-mode
# TODO: Improve unity.el, create an explicit minor mode for it
or user.emacs-minor-mode: unity-mode
-
# Recompile in Unity
recheck: self.switcher_focus_temporarily("unity editor")
# HACK: Disk changes take a while to follow through before Unity can detect
#   them, so add an artificial delay when something is saved and checked
#   immediately.
disk recheck:
    edit.save()
    sleep(1s)
    self.switcher_focus_temporarily("unity editor")
