from talon import Module, actions

emacs_command = actions.user.emacs_command
insert = actions.insert
key = actions.key

module = Module()


@module.action_class
class Actions:
    def spacemacs_align(symbol: str) -> None:
        """Align by a particular symbol."""
        align_commands = {
            ",": "spacemacs/align-repeat-comma",
            ";": "spacemacs/align-repeat-semicolon",
            ":": "spacemacs/align-repeat-colon",
            "=": "spacemacs/align-repeat-equal",
            "&": "spacemacs/align-repeat-ampersand",
            "|": "spacemacs/align-repeat-bar",
            "(": "spacemacs/align-repeat-left-paren",
            ")": "spacemacs/align-repeat-right-paren",
            "\\": "spacemacs/align-repeat-backslash",
        }
        if symbol in align_commands:
            emacs_command(align_commands[symbol])
        else:
            emacs_command("spacemacs/align-repeat")
            # This regexp should work for arbitrary symbols
            insert(f"[{symbol}]")
            key("enter")
