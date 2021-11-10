tag: user.emacs
user.emacs-major-mode: python-mode
-
blacken [buffer]: user.emacs_command("blacken-buffer")

self: "self."
self <user.complex_phrase>$:
    insert("self.")
    user.insert_complex(complex_phrase, "snake")


conda [activate] [<user.complex_phrase>]:
    user.emacs_command("conda-env-activate")
    user.insert_complex(complex_phrase or "", "lowercase")
conda [activate] [for] (buff | buffer) [<user.complex_phrase>]:
    user.emacs_command("conda-env-activate-for-buffer")
    user.insert_complex(complex_phrase or "", "lowercase")
conda deactivate: user.emacs_command("conda-env-deactivate")


send (buff | buffer): user.emacs_command("python-shell-send-buffer")
send file: user.emacs_command("python-shell-send-file")
send def: user.emacs_command("python-shell-send-defun")
send statement: user.emacs_command("python-shell-send-statement")
send string: user.emacs_command("python-shell-send-string")
# TODO: Actual dwim command? Maybe add a "dwim highlight" command that highlight
#   iff region inactive
send (that | thing | region):
    user.emacs_command("python-shall-send-region")

pytest: user.emacs_command("python-pytest")
(test | pytest) file: user.emacs_command("python-pytest-file")
(test | pytest) open: user.emacs_command("python-pytest-files")
(test | pytest) function: user.emacs_command("python-pytest-function")
# TODO: Test the class? Is that covered by -function?
(test | pytest) failed: user.emacs_command("python-pytest-last-failed")
#
((test | pytest) repeat | repeat (test | pytest)):
    user.emacs_command("python-pytest-repeat")

nose [all]: user.emacs_command("nosetests-all")
nose one: user.emacs_command("nosetests-one")
nose again: user.emacs_command("nosetests-again")
nose module: user.emacs_command("nosetests-module")
nose failed: user.emacs_command("nosetests-failed")
nose debug [all]: user.emacs_command("nosetests-pdb-all")
nose debug one: user.emacs_command("nosetests-pdb-one")
nose debug module: user.emacs_command("nosetests-pdb-module")
