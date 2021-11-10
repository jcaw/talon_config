# Generic commands for any terminal
os: windows
os: mac
os: linux
tag: terminal
-
repeat:
    key(up)
    key(enter)
# "can"?
actions(user.cancel): key(ctrl-c)
# For things like Python
other cancel: key(ctrl-d)
(kill | exit) python: key(ctrl-d)
restart:
    key(ctrl-c)
    key(up)
    key(enter)

list:
    insert("ls -a")
    key(enter)
parent:
    insert("cd ../")
    key(enter)
CD: "cd "
CD <user.complex_phrase>:
    insert("cd ")
    user.complex_insert(complex_phrase)
