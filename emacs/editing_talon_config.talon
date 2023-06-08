# Active when editing files in the talon config, in Emacs (assumes talon config is stored under "talon" or ".talon")
user.emacs-buffer-file-name: /\/talon\/user\//
# TODO: Double check this works on Linux - possible paths will differ.
# TODO: Double check this works on Mac - possible paths will differ.
user.emacs-buffer-file-name: /\/.talon\/user\//
-
# Switch between the ".talon" and ".py" versions of a file. This assumes they have the same file path.
switch: user.emacs_command("jcaw-talon-config-switch-filetype")
