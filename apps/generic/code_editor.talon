app: code_editor
-
(follow | definition | nishion): user.find_definition()
(impal | implementations): user.find_implementations()
(refer | refs | references | usage | usages): user.find_references()

backtrack:              user.editor_go_back()

(docs | documentation): user.show_documentation()



CODE TEST: insert("working")
