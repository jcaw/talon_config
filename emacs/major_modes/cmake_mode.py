from talon import Context

from user.misc.chunked_phrase import chainable_formatters


context = Context()
context.matches = """
tag: user.emacs
user.emacs-major-mode: cmake-mode
"""
context.lists["user.chainable_formatters"] = {
    **chainable_formatters,
    # TODO: easy way to type vars in cmake
    # "var": "format_cmake_var",
}
