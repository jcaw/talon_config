"""Default edit actions for all platforms"""

import time
from typing import Optional, List

from talon import Module, Context, actions, clip, ctrl

from user.utils import PreserveClipboard
from user.misc import chunked_phrase

key = actions.key
edit = actions.edit
user = actions.user


module = Module()


@module.action_class
class Actions:
    def start_extend_selection():
        """Start extending a selection (or start a new selection)."""
        # TODO: Swap to newapi once I know the interface
        ctrl.key("shift", down=True)

    def end_extend_selection():
        """Finish extending a selection."""
        # TODO: Swap to newapi once I know the interface
        ctrl.key("shift", up=True)

    def search(text: str = None) -> None:
        """Perform some generic "search". Behavior depends on the program.

        Provide `text` to search for some text.

        """
        actions.user.search()
        actions.sleep("500ms")
        if text:
            actions.insert(text)

    def toggle_comment() -> None:
        """Toggle whether the current line/region is commented."""

    def toggle_comment_lines(num_lines: int) -> None:
        """Toggle multiple lines after point to be commented/uncommented."""
        # TODO: Maybe default implementation using something a `select-line`
        #   action?

    def insert_comment(complex_phrase: List[chunked_phrase.BasePhraseChunk]) -> None:
        """Add a comment and insert `complex_phrase` into it."""
        user.toggle_comment()
        actions.sleep("500ms")
        user.insert_complex(complex_phrase, "capitalized_sentence")


# We use this abstraction to allow for mark-based selection, e.g. Emacs.
class ExtendSelection:
    def __init__(self):
        pass

    def __enter__(self):
        actions.user.start_extend_selection()

    def __exit__(self, *_):
        actions.user.end_extend_selection()


context = Context()


@context.action_class("edit")
class Actions:
    def delete():
        key("backspace")

    def delete_line():
        edit.select_line()
        edit.delete()

    def delete_paragraph():
        edit.select_paragraph()
        edit.delete()

    def delete_sentence():
        edit.select_sentence()
        edit.delete()

    def delete_word():
        edit.select_word()
        edit.delete()

    def down():
        key("down")

    def extend_down():
        with ExtendSelection():
            edit.down()

    def extend_file_end():
        with ExtendSelection():
            edit.file_end()

    def extend_file_start():
        with ExtendSelection():
            edit.file_start()

    def extend_left():
        with ExtendSelection():
            edit.left()

    # def extend_line(n:int):
    #     raise NotImplementedError()

    def extend_line_down():
        with ExtendSelection():
            edit.line_down()

    def extend_line_end():
        with ExtendSelection():
            edit.line_end()

    def extend_line_start():
        with ExtendSelection():
            edit.line_start()

    def extend_line_up():
        with ExtendSelection():
            edit.line_up()

    def extend_page_down():
        with ExtendSelection():
            edit.page_down()

    def extend_page_up():
        with ExtendSelection():
            edit.page_up()

    def extend_paragraph_end():
        with ExtendSelection():
            edit.paragraph_end()

    def extend_paragraph_previous():
        with ExtendSelection():
            edit.paragraph_previous()

    def extend_paragraph_next():
        with ExtendSelection():
            edit.paragraph_next()

    def extend_paragraph_start():
        with ExtendSelection():
            edit.paragraph_start()

    def extend_right():
        with ExtendSelection():
            edit.right()

    # def extend_sentence_end():
    #     raise NotImplementedError()

    def extend_sentence_next():
        for i in range(2):
            edit.extend_sentence_end()

    def extend_sentence_previous():
        for i in range(2):
            edit.extend_sentence_start()

    # def extend_sentence_start():
    #     raise NotImplementedError()

    def extend_up():
        with ExtendSelection():
            edit.up()

    def extend_word_left():
        with ExtendSelection():
            edit.word_left()

    def extend_word_right():
        with ExtendSelection():
            edit.word_right()

    # def find_next():
    #     raise NotImplementedError()

    # def find_previous():
    #     raise NotImplementedError()

    def indent_less():
        key("shift-tab")

    def indent_more():
        key("tab")

    # def jump_column():
    #     raise NotImplementedError()
    # def jump_line():
    #     raise NotImplementedError()

    def left():
        key("left")

    def line_down():
        key("down")

    def line_end():
        key("end")

    def line_insert_down():
        key("enter")

    def line_insert_up():
        key("enter")
        edit.line_up()
        edit.line_end()

    def line_start():
        key("home")

    def line_up():
        key("up")

    def page_down():
        key("pagedown")

    def page_up():
        key("pageup")

    def paragraph_next():
        edit.paragraph_start()
        for i in range(2):
            edit.paragraph_end()

    def paragraph_previous():
        edit.paragraph_end()
        for i in range(2):
            edit.paragraph_start()

    def paste_match_style():
        clip.set_text(clip.get())
        time.sleep(0.1)
        actions.paste()

    def right():
        key("right")

    def select_line(n: int = None):
        if n is not None:
            raise NotImplementedError()
        edit.line_start()
        edit.extend_line_end()

    # def select_lines(a:int, b:int):
    #     raise NotImplementedError()

    def select_none():
        key("esc")

    def select_paragraph():
        edit.paragraph_start()
        edit.extend_paragraph_end()

    def select_sentence():
        edit.sentence_start()
        edit.extend_sentence_end()

    def select_word():
        edit.word_start()
        edit.extend_word_end()

    def selected_text():
        with PreserveClipboard():
            edit.copy()
            time.sleep(0.1)
            return clip.get()

    # def sentence_end():
    #     raise NotImplementedError()

    def sentence_next():
        edit.sentence_start()
        for i in range(2):
            edit.sentence_end()

    def sentence_previous():
        edit.sentence_end()
        for i in range(2):
            edit.sentence_start()

    # def sentence_start():
    #     raise NotImplementedError()

    def up():
        key("up")
