# It's useful to store some misrecognitions, e.g. for frequent issues.
nope [<number>]:
    user.quarantine_speech_recording(number or 1)
    # user.cancel()
    user.command_history_show()
# Sometimes I don't want to store what has been recorded, or I just want to
# clear out multiple recordings.
nuke [<number>]:
    user.delete_last_speech_recording(number or 1)
    user.command_history_show()
wrong [<number>]:
    user.delete_last_speech_recording(number or 1)
    edit.undo()
    # TODO: Undo *and* cancel?
    user.cancel()
    user.command_history_show()
# To establish what needs to be deleted
# prior [<number>]: user.show_last_speech_recordings(number or 5)
prior: user.command_history_show()
(play | replay) last [recording] [<number>]: user.play_last_speech_recording(number or 1)
(edit | audacity) last [recording] [<number>]: user.audacity_last_speech_recording(number or 1)
