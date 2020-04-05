from talon import Module, actions

emacs_fallbacks = actions.user.emacs_fallbacks


module = Module()


@module.action_class
class Actions:
    def emacs_describe_key() -> None:
        """Describe a key binding."""
        emacs_fallbacks(["helpful-key", "describe-key"])

    def emacs_describe_function() -> None:
        """Describe a function."""
        emacs_fallbacks(["helpful-function", "describe-function"])

    def emacs_describe_command() -> None:
        """Describe a command."""
        emacs_fallbacks(
            [
                "helpful-command",
                # There's no inbuilt `describe-command`, use approximation.
                "describe-function",
            ]
        )

    def emacs_describe_variable() -> None:
        """Describe a variable."""
        emacs_fallbacks(["helpful-variable", "describe-variable"])

    def emacs_apropos() -> None:
        """Perform the best available apropos command."""
        emacs_fallbacks(["helm-apropos", "helpful-symbol", "apropos"])

    def emacs_describe_thing_at_point() -> None:
        """Describe the thing under point."""
        emacs_fallbacks(["helpful-at-point", "helm-info-at-point"])
