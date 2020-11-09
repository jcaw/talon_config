from talon import Module, actions


module = Module()
module.list("active_symbols", desc='List of symbols "active" in the current context.')
module.list(
    "active_symbol_sections", desc="List of all components of all active symbols."
)


@module.capture(rule="{user.active_symbols}")
def active_symbol(m) -> str:
    """One of the active symbols."""
    return m.active_symbols


@module.capture(rule="{user.active_symbol_sections}")
def active_symbol_section(m) -> str:
    """A section from an active symbol."""
    return m.active_symbol_sections


@module.action_class
class Actions:
    def insert_symbol(symbol: str) -> None:
        """Insert a `symbol`."""
        # Default behaviour is simple but this is its own action so it can be
        # overridden.
        actions.insert(symbol)

    def insert_symbol_from_section(symbol_section: str) -> None:
        """Insert the symbol that includes `symbol_section`.

        Additional selection may be required if multiple symbols include
        `symbol_section`.

        """
        # TODO: Maybe a default implementation using imgui?
