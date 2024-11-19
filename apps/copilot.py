from typing import Optional, Tuple

from talon import Module, Context, actions, cron
from user.plugins.vimfinity.vimfinity import vimfinity_bind_keys


user = actions.user


module = Module()


COPILOT_EXPLAIN_CODE_TEMPLATE = """Please explain this code:

```{language}
{code_text}
```"""

# FIXME: Including the compilation bug causes a weird error, seemingly caused by
#   exceeding the max tokens. For now, just don't include it.
COPILOT_EXPLAIN_COMPILATION_ERROR_COMPLEX = """I'm getting an error that I don't understand. I will list the compilation output, then the error, then the line the compiler claims is causing trouble.

This is the compilation output:
```
{compilation_output}
```

This is the error I would like explained:
```
{error_message}
```

This is the first line of the code that the compiler claims is causing the problem:
```
{code_responsible}
```

Explain why I'm getting this error."""

COPILOT_EXPLAIN_COMPILATION_ERROR = """I'm getting a compilation error I that I don't understand. This is the error:
```
{error_message}
```

This is the first line of the code that the compiler claims is causing the problem:
```
{code_responsible}
```

Explain why I'm getting this error."""

COPILOT_QUOTE_MESSAGE = """

```
{text}
```

"""


@module.action_class
class CopilotActions:
    def copilot_open_chat():
        """Open copilot chat."""

    def copilot_chat_message(message: str, submit: bool = True):
        """Type (and optionally send) a specific message in Copilot Chat."""

    def copilot_chat_command(command: str):
        """Run a specific command in copilot chat."""
        # TODO: Probably extract to jetbrains.

    def copilot_generate_docs():
        """Generate docs at point with copilot."""
        actions.self.copilot_chat_command("/doc")

    def copilot_explain():
        """Explain the current file with copilot."""
        actions.self.copilot_chat_command("/explain")

    def copilot_explain_highlighted():
        """Explain the highlighted code in the current file with copilot."""
        text = user.get_highlighted()
        if " " in text.strip():
            # TODO: language
            message = COPILOT_EXPLAIN_CODE_TEMPLATE.format(language="", code_text=text)
        else:
            message = f"Explain `{text.strip()}`"
        actions.user.copilot_chat_message(message)

    def copilot_get_compilation_error() -> Tuple[str, str, Optional[str]]:
        """Get information about the compilation error at point.

        This must be implemented individually for each editor, in order for
        `copilot_explain_compilation_error` to work.

        """

    def copilot_explain_compilation_error():
        """Explain the currently selected error in the build window."""
        (
            error_message,
            code_responsible,
            compilation_output,
        ) = actions.self.copilot_get_compilation_error()
        if compilation_output == None:
            text = COPILOT_EXPLAIN_COMPILATION_ERROR.format(
                error_message=error_message,
                code_responsible=code_responsible,
            )
        else:
            text = COPILOT_EXPLAIN_COMPILATION_ERROR_COMPLEX.format(
                compilation_output=compilation_output,
                error_message=error_message,
                code_responsible=code_responsible,
            )
        actions.self.copilot_chat_message(text)

    def copilot_quote_highlighted():
        """Open the Copilot Chat window, and quote the highlighted text in a block.

        You can then fill in the rest of the query, and submit it.

        """
        text = user.get_highlighted()
        # DWIM behaviour based on what we're copying
        if " " in text.strip():
            # For code snippets, use a block quote
            message = COPILOT_QUOTE_MESSAGE.format(text=text)
        else:
            # If it's just a name, use a short quoting style.
            message = f" `{text.strip()}`"
        actions.self.copilot_chat_message(message, submit=False)
        # Go back to the very start of the message.
        # NOTE: Assumes the copilot chat input is some kind of normal document.
        actions.user.document_start()

    def copilot_fix():
        """Fix the current thing with copilot."""
        actions.self.copilot_chat_command("/fix")

    def copilot_simplify():
        """Simplify the current thing with copilot."""
        actions.self.copilot_chat_command("/simplify")

    def copilot_generate_tests():
        """Generate tests for the thing at point with copilot."""
        actions.self.copilot_chat_command("/tests")

    def copilot_reference_file():
        """Reference the current file in Copilot Chat."""

    def copilot_full_suggestions():
        """Generate a full list of suggestions from GitHub Copilot."""

    def copilot_explain_current_function():
        """Ask GitHub Copilot to explain the function that's being edited (not the function being called)."""
        actions.user.copilot_explain(actions.user.get_current_function())


copilot_chat_ide_context = Context()
# Add any copilot-enabled IDEs here to get e.g. keyboard shortcut bindings.
copilot_chat_ide_context.matches = r"""
tag: user.jetbrains
# tag: user.vscode
# tag: user.visual_studio
# tag: user.emacs
"""


# Bind Copilot Chat actions
vimfinity_bind_keys(
    {
        "p": "GitHub Copilot",
        "p p": (actions.user.copilot_open_chat, "Open Copilot Chat"),
        "p q": (actions.user.copilot_explain, "Explain File"),
        "p e": (
            actions.user.copilot_explain_highlighted,
            "Explain Highlighted",
        ),
        # TODO: "x" for "exception"
        "p x": (
            actions.user.copilot_explain_compilation_error,
            "Explain Compilation Error",
        ),
        "p w": (actions.user.copilot_quote_highlighted, "Quote Highlighted"),
        "p f": (actions.user.copilot_fix, "Fix This"),
        "p s": (actions.user.copilot_simplify, "Simplify This"),
        "p d": (actions.user.copilot_generate_docs, "Generate Docs"),
        "p t": (actions.user.copilot_generate_tests, "Generate Tests"),
        "p r": (actions.user.copilot_reference_file, "Reference File in Chat"),
        "p c": (
            actions.user.copilot_full_suggestions,
            "List Completions",
        ),
        "p u": (
            actions.user.copilot_explain_current_function,
            "Explain Current Function",
        ),
    },
    copilot_chat_ide_context,
)
