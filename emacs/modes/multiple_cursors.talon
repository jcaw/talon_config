tag: user.emacs
user.emacs-minor-mode: multiple-cursors-mode
-
exit: user.emacs_command("mc/keyboard-quit")
multi: user.emacs_command("mc/mark-next-like-this")

(necks | next): user.emacs_command("mc/mark-next-like-this")
(last | larse): user.emacs_command("mc/mark-previous-like-this")
skip [(down | neck | neck)]: user.emacs_command("mc/skip-to-next-like-this")
skip (up | last | larse): user.emacs_command("mc/skip-to-previous-like-this")

numbers: user.emacs_command("mc/insert-numbers")
letters: user.emacs_command("mc/insert-letters")
sort: user.emacs_command("mc/sort-regions")
reverse: user.emacs_command("mc/reverse-regions")
