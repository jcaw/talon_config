tag: browser
-
# Browser GUI
# TODO: Optional dictation
address [bar]: browser.focus_address()
# TODO: Optional dictation
search [bar]: browser.focus_search()
[focus] page: browser.focus_page()
# TODO: Copy address?
# TODO: Copy page title?


# Navigation
go back: browser.go_back()
go forward: browser.go_forward()
go home | homepage: browser.go_home()
go blank [page]: browser.go_blank()
(refresh | reload) [light]: browser.reload()
(refresh | reload) medium: browser.reload_hard()
(refresh | reload) hard: browser.reload_hardest()
# TODO: Go to a page, browser.go() - should probably be global


# Bookmarks, History, etc.
(bookmark page | add bookmark): browser.bookmark()
bookmark (all | tabs | all tabs): browser.bookmark_tabs()
# Bookmarks & bookmarks bar are different
show bookmarks: browser.bookmarks()
bookmarks bar: browser.bookmarks_bar()
[show] history [bar]: browser.show_history()
[show] (downloads | download) [bar]: browser.show_downloads()
[show] extensions: browser.show_extensions()
(clear | delete) (cache | cached data): browser.show_clear_cache()


# Unsorted
[open] private [(window | browsing)]: browser.open_private_window()
(dev | developer) tools: browser.toggle_dev_tools()
submit [form]: browser.submit_form()
