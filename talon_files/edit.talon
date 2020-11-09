file start: edit.file_start()
file end: edit.file_end()
(sell | select) (file | all): edit.select_all()

(page up | jup): edit.page_up()
(page down | jown | jan): edit.page_down()

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

# Declared separately to allow for a default implementation with only find() defined.
#
# TODO: Probably pull the <dictation> ones out into just emacs? Just have a
#   <complex> implementation.
find [<user.dictation>]$: edit.find(dictation or "")
find <user.complex_phrase>$:
    user.search()
    sleep(500ms)
    user.insert_complex(complex_phrase, "lowercase")
search [<user.dictation>]$: user.search(dictation or "")
search <user.complex_phrase>$:
    user.search()
    sleep(500ms)
    user.insert_complex(complex_phrase, "lowercase")


comment: user.toggle_comment()
comment <user.complex_phrase>$:     user.insert_comment(complex_phrase)
comment <user.complex_phrase> over: user.insert_comment(complex_phrase)
