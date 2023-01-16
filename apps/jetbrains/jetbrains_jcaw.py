"""Separate action implementations for jetbrains products"""

from typing import Optional

from talon import Context, actions

idea = actions.user.idea
sleep = actions.sleep


context = Context()
context.matches = r"""
app: jetbrains
"""


@context.action_class("user")
class UserActions:
    def rename():
        idea("action RenameElement")

    def find_definition() -> None:
        # FIXME: This seems wrong
        idea("action GotoAction")

    def show_autocomplete() -> None:
        idea("action CodeCompletion")

    def typecomplete() -> None:
        idea("action SmartTypeCompletion")

    def find_implementations() -> None:
        idea("action GotoImplementation")

    def find_references() -> None:
        idea("action FindUsages")

    def find_type_declaration() -> None:
        idea("action FindTypeDeclaration")

    def find_tests() -> None:
        idea("action GotoTest")

    def show_documentation() -> None:
        raise NotImplementedError()
        idea("action FindDocumentation")

    def wrap(wrapper: Optional[str] = None) -> None:
        idea("action SurroundWith")
        sleep("500ms")
        if wrapper:
            insert(wrapper)

    def inline_code() -> None:
        idea("action Inline")

    def extract_variable() -> None:
        idea("action IntroduceVariable")

    def extract_method() -> None:
        idea("action ExtarctMethod")

    def extract_parameter() -> None:
        idea("action IntroduceParameter")

    def extract_constant() -> None:
        idea("action IntroduceConstant")

    def extract_interface() -> None:
        idea("action ExtractInterface")

    def refactor_move() -> None:
        idea("action Move")
