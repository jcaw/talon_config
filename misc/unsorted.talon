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


scroll top:    user.document_start()
scroll bottom: user.document_end()


# Huion tablet stuff
#
# This is the default key bind to open the tablet "driver" (settings menu)
(hwyon | tablet) settings: key(ctrl-alt-h)


# Don't tell Aegis (use this when Voicemacs deadlocks)
restart talon: user.restart_talon_with_sound()
exit talon:    user.quit_talon_with_sound()

key(ctrl-shift-enter): user.toggle_mic_off()


# Open with commands
with chrome:             user.open_current_page_in_chrome()

with emacs:              user.open_current_file_in_emacs()
project [to] emacs:      user.open_current_project_in_emacs()

with (idea | intelli J): user.open_current_file_in_idea()
# project to (idea | intelli J): user.open_current_project_in_idea()
with rider:              user.open_current_file_in_rider()
# project to rider:        user.open_current_project_in_rider()
