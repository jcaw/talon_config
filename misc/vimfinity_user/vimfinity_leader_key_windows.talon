os: windows
-
## Note caps lock is mapped to F16 on my Windows machine.
key(f16): user.vimfinity_start_sequence()
# Some windows disable the rebind, so reactivate it here.
key(capslock):
    user.vimfinity_start_sequence()
    # HACK: Talon doesn't prevent the capslock state from changing on Windows
    #   when it consumes the keypress, so reset it back.
    key(capslock)
