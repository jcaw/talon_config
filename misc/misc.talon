# Ignore repeats that occur as the first element, to stop hallucinated repeats.

^<number>: user.opening_number_action(number)

# TODO: Extract to Windows module
(start | search ) program | search windows [<phrase>]:
    key(win-s)
    insert(phrase)

(refresh | reload) words: user.update_custom_words()

<user.file_suffix>: insert(file_suffix)

# We'll want to use this in all sorts of places
(interrupt | cease): key(ctrl-c)

go back:    user.go_back()
go forward: user.go_forward()

cancel: user.cancel()

# Record all voice clips
settings(): speech.record_all = 1


# Discarding Recordings
nope [<number>]:
    user.delete_last_speech_recording(number or 1)
    # user.cancel()
wrong [<number>]:
    user.delete_last_speech_recording(number or 1)
    edit.undo()
    # TODO: Undo *and* cancel?
    user.cancel()
# To establish what needs to be deleted
prior [<number>]: user.last_speech_recordings(number or 5)
(play | replay) last [recording]: user.play_last_speech_recording()
(edit | audacity) last [recording]: user.audacity_last_speech_recording()

scroll top:    user.document_start()
scroll bottom: user.document_end()

# Don't tell Aegis (use this when Voicemacs deadlocks)
restart talon: user.restart_talon_with_sound()
exit talon:    user.quit_talon_with_sound()

key(ctrl-shift-enter): user.toggle_mic_off()
