from talon import Context, Module, actions

from user.misc.chunked_phrase import chainable_formatters

emacs_command = actions.self.emacs_command


context = Context()
context.matches = """
tag: user.emacs
user.emacs-major-mode: python-mode
"""
context.lists["user.chainable_formatters"] = {
    **chainable_formatters,
    "private": "python_private",
    "dot": "dot_prefix_snake",
    "lub": "rparen_prefix_snake",
}


module = Module()


@module.action_class
class Actions:
    def emacs_python_shell_command(command: str) -> None:
        """Run `command` in the Python shell, then show the shell."""
        emacs_command("run_python")
        emacs_command(command)
        emacs_command("jcaw-python-show-shell")
