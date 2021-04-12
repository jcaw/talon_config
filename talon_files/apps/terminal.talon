# Generic commands for any terminal

tag: terminal
-
repeat:
    key(up)
    key(enter)
# "can"?
(cancel | cell): key(ctrl-c)
# For things like Python
other cancel: key(ctrl-d)
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
