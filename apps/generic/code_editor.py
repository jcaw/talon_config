from talon import Module, actions


module = Module()
module.tag("code_editor", desc="Enabled when a code editor is the active application.")


class DocumentPositionInfo:
    """Information about cursor position in a document."""
    def __init__(self, path=None, row=None, column=None, offset=None):
        self.path = path       # File path
        self.row = row         # Line number (0-based)
        self.column = column   # Column number (0-based)
        self.offset = offset   # Byte offset in file (0-based)


@module.action_class
class NavigationActions:
    def find_definition() -> None:
        """Navigate to the definition of the symbol under point."""

    def find_implementations() -> None:
        """Find implementations of the symbol under point."""

    def find_references() -> None:
        """Find references to the symbol under point."""

    def show_documentation() -> None:
        """Show documentation for the symbol under point."""

    def next_error() -> None:
        """Navigate to the next error or diagnostic."""

    def previous_error() -> None:
        """Navigate to the previous error or diagnostic."""

    def document_start() -> None:
        """Jump to the start of the document."""

    def document_end() -> None:
        """Jump to the end of the document."""

    def next_fold() -> None:
        """Navigate to the next fold."""

    def previous_fold() -> None:
        """Navigate to the previous fold."""

    def search(text: str = None) -> None:
        """Search for text in the current project or directory."""


@module.action_class
class EditorActions:
    def open_file() -> None:
        """Open a file dialog to open a file."""

    def toggle_comment() -> None:
        """Toggle comment on the current line or selection."""


@module.action_class
class ViewActions:
    def toggle_fold() -> None:
        """Toggle visibility folding for the current item."""

    def fold() -> None:
        """Fold (hide) the current item."""

    def unfold() -> None:
        """Unfold (show) the current item."""

    def fold_all() -> None:
        """Fold all items (meaning depends on context)."""

    def unfold_all() -> None:
        """Unfold all items in the document."""

    def zoom_in() -> None:
        """Increase the font size in the editor."""

    def zoom_out() -> None:
        """Decrease the font size in the editor."""


@module.action_class
class UnsortedActions:
    def current_row() -> int:
        """Get the current cursor row/line in the document (1-based)."""
    
    def current_column() -> int:
        """Get the current cursor column in the document (0-based)."""

    def current_offset() -> int:
        """Get the current cursor offset in the document - the point position."""

    def document_position() -> DocumentPositionInfo:
        """Get document position including file path, row, column, and offset."""
        # Maybe override this if the info can be gotten in a single call, 
        # otherwise it'll default to using the individual calls.
        return DocumentPositionInfo(path=actions.app.path(),
                                    row=actions.user.current_row(), 
                                    column=actions.user.current_column(), 
                                    offset=actions.user.current_offset())