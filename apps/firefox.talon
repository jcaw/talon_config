app: /firefox/
-
# Requires the "Dark Reader" addon to be installed
dark (mode | reader): key(alt-shift-d)
# Requires the "spritzlet" bookmark to be present, with the "spritzlet" keyword
# registered to it.
(spritz | spritzlet | spreed):
    browser.focus_address()
    insert("spritzlet")
    key("enter")
    # The url will be changed, prestore the original
    sleep(50ms)
    browser.focus_address()
    edit.undo()
    edit.undo()
    browser.focus_page()
read (aloud | it):
    key(alt-p)


(open in chrome | chrome it): user.open_current_page_in_chrome()
