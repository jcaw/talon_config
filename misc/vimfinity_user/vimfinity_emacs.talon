# This is separate because Emacs uses the leader key for its own actions.
tag: user.emacs
-
# Note caps lock is mapped to F16 on my Windows machine.
key(ctrl-f16):      user.vimfinity_start_sequence()
key(ctrl-capslock): user.vimfinity_start_sequence()


# This hack allows the leader to be double pressed in Emacs, to bypass Emacs'
# leader system and revert back to Vimfinity in Talon.
key(f16):      user.emacs_leader_doublepress_handler()
key(capslock): user.emacs_leader_doublepress_handler()
