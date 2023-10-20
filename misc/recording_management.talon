# It's useful to store some misrecognitions, e.g. for frequent issues.
# nope [<number>]:
#     user.quarantine_speech_recordings(number or 1)
#     user.command_history_show()
nope [<user.ordinal>]:
    user.quarantine_speech_recording(ordinal or 1)
# Sometimes I don't want to store what has been recorded, or I just want to
# clear out multiple recordings.
#
# TODO: Remove "nuke", "bomb" is better
(nuke | bomb) [<number>]:
    user.delete_speech_recordings(number or 1)
(nuke | bomb) <user.ordinal>:
    user.delete_speech_recording(ordinal)
# TODO: Probably remove
# wrong [<number>]:
#     user.delete_last_speech_recordings(number or 1)
#     edit.undo()
#     # TODO: Undo *and* cancel?
#     user.cancel()
#     user.command_history_show()
# To establish what needs to be deleted
# prior [<number>]: user.show_last_speech_recordings(number or 5)
prior: user.command_history_show()
(play | replay) last [recording] [<number>]: user.play_last_speech_recording(number or 1)
(edit | audacity) last [recording] [<number>]: user.audacity_last_speech_recording(number or 1)
