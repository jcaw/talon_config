file start: edit.file_start()
file end: edit.file_end()
(sell | select) (file | all): edit.select_all()

(page up | jup): edit.page_up()
# Removed: jown
(page down | jan): edit.page_down()

(sell | select) line: edit.select_line()
kill line: edit.delete_line()

cut: edit.cut()
copy: edit.copy()
paste: edit.paste()

(undo | scrap | scrub): edit.undo()
redo: edit.redo()

# TODO: Doc, file - common language here?
print doc: edit.print()
save doc | disk: edit.save()
(save [doc] | disk) as: edit.save_as()
(save | disk) all: edit.save_all()

zoom in: edit.zoom_in()
zoom out: edit.zoom_out()

# Declared separately to allow for a default implementation with only find() defined.
#
# TODO: Probably pull the <dictation> ones out into just emacs? Just have a
#   <complex> implementation.
find [<user.dictation>]$: edit.find(dictation or "")
find (that | thing)$: edit.find(user.get_that_dwim())
find <user.complex_phrase>$:
    edit.find()
    sleep(500ms)
    user.insert_complex(complex_phrase, "lowercase")
search [<user.dictation>]$: user.search(dictation or "")
search (that | thing)$: user.search(user.get_that_dwim())
search <user.complex_phrase>$:
    user.search()
    sleep(500ms)
    user.insert_complex(complex_phrase, "lowercase")


comment: user.toggle_comment()
comment <number>: user.toggle_comment_lines(number)
comment <user.complex_phrase>$:     user.insert_comment(complex_phrase)
comment <user.complex_phrase> over: user.insert_comment(complex_phrase)

(rename | run me) [<user.complex_phrase>$]:   user.rename_with_phrase(complex_phrase or "")
(rename | run me) <user.complex_phrase> over: user.rename_with_phrase(complex_phrase or "")


# TODO: Combine properly with Emacs editing commands
(bird | backurd):        key(ctrl-left)
(furd | frurd | forurd): key(ctrl-right)
bassurd: key(ctrl-shift-left)
fossurd: key(ctrl-shift-right)
lasserd: key(ctrl-backspace)
neckerd: key(ctrl-delete)
