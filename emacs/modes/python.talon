tag: user.emacs
user.emacs-major-mode: python-mode
-
blacken [buffer]: user.emacs_command("blacken-buffer")

self: "self."
self <user.complex_phrase>$:
    insert("self.")
    user.insert_complex(complex_phrase, "snake")

pytest: user.emacs_command("python-pytest")
(test | pytest) file: user.emacs_command("python-pytest-file")
(test | pytest) open: user.emacs_command("python-pytest-files")
(test | pytest) function: user.emacs_command("python-pytest-function")
# TODO: Test the class? Is that covered by -function?
(test | pytest) failed: user.emacs_command("python-pytest-last-failed")
#
(pytest repeat | repeat pytest): user.emacs_command("python-pytest-repeat")
