from talon import Module, Context, registry, clip


module = Module()
context = Context()


def _action_declarations():
    """Generate all defined actions, as strings."""
    for decl in registry.decls.actions.values():
        yield str(decl)


def _capture_declarations():
    # TODO: Switch this back to values once the upstream issue is fixed in Talon
    # for decl in registry.decls.captures.values():
    for decl in registry.decls.captures.keys():
        yield str(decl)


def _print_and_copy(string):
    print(string)
    clip.set(string)
    print("String copied to clipboard.")


@module.action_class
@context.action_class
class Actions:
    def print_copy_actions() -> None:
        """Print & copy all declared actions."""
        _print_and_copy("\n".join(_action_declarations()))

    def print_copy_captures() -> None:
        """Print & copy all declared captures."""
        _print_and_copy("\n".join(_capture_declarations()))
