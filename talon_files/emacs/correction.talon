tag: user.emacs
-
# Two methods to correct misrecognitions:

(fix | correct) [<number>] <user.letter>:
    user.emacs_prefix_command("voicemacs-correct-n-words-avy", number or 1)
    key(letter)
(fix | correct) <user.letter> <user.letter>:
    user.emacs_command("voicemacs-correct-words-avy")
    key(letter_1)
    key(letter_2)
