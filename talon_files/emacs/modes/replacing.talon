# Active during a find/replace session

tag: user.emacs
# This covers projectile-replace too.
user.emacs-current-message: /Query replacing /
# erefactor
user.emacs-current-message: /Rename? (y or n)/
-
# Pop to replace, hiss to skip
action(user.on_pop):  key("y")
action(user.on_hiss): key("n")
