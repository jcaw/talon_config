os: windows
-
## Note caps lock is mapped to F16 on my Windows machine.
key(f16): user.vimfinity_start_sequence()
# Some windows disable the rebind, so reactivate it here.
key(capslock):
    user.vimfinity_start_sequence()
    # HACK: Undo the capslock state on Windows
    key(capslock)
