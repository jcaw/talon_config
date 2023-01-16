app: jetbrains

# Pycharm title just has the project & file - but it'll end in .py when a python
# file is in focus.
# title: /.py/


exe: /pycharm/
-
pytest: insert("hello")
# requires plug-in: black-pycharm
blacken: user.idea("action BLACKReformatCode")
