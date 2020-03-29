(sell | select) (file | all): edit.select_all()

(page up | jup): edit.page_up()
(page down | jown | jan): edit.page_down()

(sell | select) line: edit.select_line()
kill line: edit.delete_line()

cut: edit.cut()
copy: edit.copy()
paste: edit.paste()
(undo | scrap): edit.undo()
redo: edit.redo()

# TODO: Doc, file - common language here?
print doc: edit.print()
save doc: edit.save()
save [doc] as: edit.save_as()
save all: edit.save_all()

# TODO: Extract these long-form actions
# Declared separately to allow for a default implementation with only find() defined.
find: edit.find()
find <user.dictation>:
    edit.find()
    sleep(500ms)
    insert(dictation)
search: user.search()
search <user.dictation>: user.search_text(dictation)


comment: user.toggle_comment()
comment <user.dictation>:
    user.toggle_comment()
    sleep(500ms)
    user.insert_capitalized(dictation)
