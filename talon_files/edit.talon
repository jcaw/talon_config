cut: edit.cut()
copy: edit.copy()
paste: edit.paste()
(undo | scrap): edit.undo()
redo: edit.redo()

(page up | jup): edit.page_up()
(page down | jown): edit.page_down()

# TODO: Extract these long-form actions
# Declared separately to allow for a default implementation with only find() defined.
find: edit.find()
find <user.dictation>:
    edit.find()
    sleep(500ms)
    insert(dictation)
search: user.search()
search <user.dictation>: user.search_text(dictation)
