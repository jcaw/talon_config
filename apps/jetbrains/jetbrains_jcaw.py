"""Separate action implementations for jetbrains products"""

import re
from typing import Optional, List, Dict

from talon import Context, actions, Module, cron
from talon.ui import Rect

from user.utils.formatting import SurroundingText
from user.settings.test.clickable_overlay import Clickable


idea = actions.user.idea
sleep = actions.sleep
key = actions.key
insert = actions.insert
jetbrains_rpc_call = actions.user.jetbrains_rpc_call
jetbrains_action = actions.user.jetbrains_action


module = Module()
module.tag("jetbrains", "Active when JetBrains products are focused.")


jetbrains_context = Context()
jetbrains_context.matches = r"tag: user.jetbrains"


module.tag("pycharm", "Active when PyCharm is focused.")
pycharm_context = Context()
pycharm_context.matches = r"""
app: /pycharm/
# TODO: Remove once testing is done
app: /OpenJDK Platform binary/
"""
pycharm_context.tags = ["user.jetbrains", "user.pycharm"]


module.tag("rider", "Active when JetBrains Rider is focused.")
rider_context = Context()
rider_context.matches = r"""
app: /rider/
"""
rider_context.tags = ["user.jetbrains", "user.rider"]


module.tag("idea", "Active when IntelliJ IDEA is focussed.")
idea_context = Context()
idea_context.matches = r"""
app: /idea/

# When testing the RPC plugin, this is the editor that will be launched.
app: /OpenJDK Platform binary/
and title: /Jetbrains-RPC-Server/
"""
idea_context.tags = ["user.jetbrains", "user.idea"]


def find_element(text=None, component_class=None):
    """Find element by matching properties. Case-sensitive."""
    flat_ui_tree = actions.user.jetbrains_ui_tree_flat()
    # Go top-first
    flat_ui_tree.reverse()
    for element in flat_ui_tree:
        if "GitHub Copilot" in (element["name"] or "") and element["croppedBounds"]:
            print(
                f'  Actions: {element["actions"]},  Class: {element["componentClass"]},  Name: {element["name"]}'
            )
        if (
            element["croppedBounds"]
            and (not text or re.match(text, (element["name"] or "").strip()))
            and (
                not component_class
                # Check the last element of the component class
                or re.match(
                    component_class,
                    (element["componentClass"] or "").split(".")[-1].strip(),
                )
            )
        ):
            return element
    raise RuntimeError(f'Could not find an element matching text "{text}"')


def get_bounds(element) -> Rect:
    """Get the cropped bounds from a UI element dict, as a Rect"""
    bounds = element["croppedBounds"]
    return Rect(bounds["x"], bounds["y"], bounds["width"], bounds["height"])


def hover_button(text=None, component_class=None):
    actions.mouse_move(
        *get_bounds(find_element(text=text, component_class=component_class)).center
    )
    actions.user.shake_mouse(0.1)


def copilot_click(text):
    """Open the GitHub Copilot right-click menu and click a subsection."""
    actions.key("menu")
    sleep("200ms")
    hover_button(text="GitHub Copilot", component_class="ActionMenu")
    sleep("200ms")
    hover_button(text=text)
    actions.mouse_click(button=0)
    sleep("100ms")
    actions.self.copilot_open_chat()


def copilot_chat_command(command):
    # In case the chat is already open
    actions.key("escape")
    actions.self.copilot_open_chat()
    sleep("50ms")
    key("ctrl-a")
    sleep("50ms")
    # Add a space after so "enter" doesn't just select the autocomplete candidate.
    actions.insert(f"{command} ")
    sleep("50ms")
    key("enter")
    # actions.insert("test")


@module.action_class
class Actions:
    def copilot_open_chat():
        """Open copilot chat."""

    def copilot_generate_docs():
        """Generate docs at point with copilot."""

    def copilot_explain():
        """Explain the current file with copilot."""

    def copilot_fix():
        """Fix the current thing with copilot."""

    def copilot_simplify():
        """Simplify the current thing with copilot."""

    def copilot_generate_tests():
        """Generate tests for the thing at point with copilot."""

    def copilot_reference_file():
        """Generate tests for the thing at point with copilot."""

    def copilot_full_suggestions():
        """Generate a full list of suggestions from GitHub Copilot."""


@jetbrains_context.action_class("user")
class JetbrainsCopilotActions:
    def copilot_open_chat():
        jetbrains_action("ActivateGitHubCopilotChatToolWindow")

    def copilot_generate_docs():
        copilot_chat_command("/doc")

    def copilot_explain():
        copilot_chat_command("/explain")

    def copilot_fix():
        copilot_chat_command("/fix")

    def copilot_simplify():
        copilot_chat_command("/simplify")

    def copilot_generate_tests():
        copilot_chat_command("/tests")

    def copilot_reference_file():
        # Use the convoluted menu approach, because it allows files to be more
        # easily added from any context - e.g. the file list, editor, etc.
        copilot_chat_click("Reference File in Chat")

    def copilot_full_suggestions():
        jetbrains_action("copilot.openCopilot")


# TODO: Pull the rider-specific methods into the Rider context. Test them first though.
@module.action_class
class RefactorActions:
    def use_base_type_where_possible():
        """Refactor to use the base type wherever possible."""
        # TODO: Is this right?
        jetbrains_action("RiderBackendAction-UseBaseTypeAction")

    def refactor_copy():
        """Refactor to copy the current thing."""
        # TODO: Is this right?
        jetbrains_action("CopyReference")

    def refactor_safe_delete():
        """Safely delete this thing."""
        jetbrains_action("SafeDelete")

    def extract_members_to_partial():
        """TODO"""
        # TODO: Is this right?
        jetbrains_action("RiderBackendAction-Type2Partial")

    def extract_variable():
        """TODO"""
        # TODO: extract variable
        raise NotImplementedError()

    def extract_method():
        """Extract the current lines into a dedicated method."""
        jetbrains_action("ExtractMethod")

    def extract_interface():
        """Extract into a dedicated interface."""
        jetbrains_action("ExtractInterface")

    def extract_superclass():
        """Extract a superclass."""
        jetbrains_action("ExtractSuperclass")

    def extract_class():
        """Extract into a dedicated class."""
        jetbrains_action("ExtractClass")

    def extract_global_using():
        """TODO"""
        # TODO: Is this right?
        jetbrains_action("ExtractGlobalUsing")

    def extract_content_placeholder():
        """TODO"""
        # TODO: Is this right?
        jetbrains_action("ExtractContentPlaceholder")

    def move_types_into_matching_files():
        """TODO"""
        raise NotImplementedError()

    def refactor_inline():
        """TODO"""
        jetbrains_action("Inline")

    def inline_master_page_content():
        """TODO"""
        jetbrains_action("RiderBackendAction-InlineContent")

    def inline_global_using():
        """TODO"""
        jetbrains_action("RiderBackendAction-InlineGlobalUsing")

    def invert_boolean():
        """TODO"""
        jetbrains_action("RiderBackendAction-InvertBool")

    def introduce_namespace_alias():
        """TODO"""
        jetbrains_action("RiderBackendAction-CppIntroduceNamespaceAlias")

    def introduce_using_enum():
        """TODO"""
        jetbrains_action("RiderBackendAction-CppIntroduceUsingEnum")

    def introduce_field():
        """TODO"""
        jetbrains_action("IntroduceField")

    def introduce_parameter():
        """TODO"""
        jetbrains_action("IntroduceParameter")

    def introduce_typedef():
        """TODO"""
        jetbrains_action("RiderBackendAction-CppIntroduceType")

    def introduce_variable():
        """TODO"""
        jetbrains_action("RiderBackendAction-CppIntroduceType")

    def refactor_move():
        """TODO"""
        jetbrains_action("Move")

    def make_method_non_static():
        """TODO"""
        jetbrains_action("RiderBackendAction-MakeNonStatic")

    def convert_method_to_property():
        """TODO"""
        jetbrains_action("RiderBackendAction-Function2Property")

    def convert_property_to_method():
        """TODO"""
        jetbrains_action("RiderBackendAction-Property2Function")

    def convert_method_to_indexer():
        """TODO"""
        jetbrains_action("RiderBackendAction-Function2Indexer")

    def convert_indexer_to_method():
        """TODO"""
        jetbrains_action("RiderBackendAction-Indexer2Function")

    def convert_abstract_class_to_interface():
        """TODO"""
        jetbrains_action("RiderBackendAction-Abstract2Interface")

    def convert_interface_to_abstract_class():
        """TODO"""
        jetbrains_action("RiderBackendAction-Interface2Abstract")

    def convert_static_to_extension_method():
        """TODO"""
        jetbrains_action("RiderBackendAction-Static2ExtensionAction")

    def convert_extension_method_to_plain_static():
        """TODO"""
        jetbrains_action("RiderBackendAction-Extension2StaticAction")

    def convert_constructor_to_factory_method():
        """TODO"""
        jetbrains_action("RiderBackendAction-Constructor2FactoryMethodAction")

    def jetbrains_transform_parameters():
        """TODO"""
        jetbrains_action("RiderBackendAction-TransformParameters")

    def convert_property_to_auto_property():
        """TODO"""
        jetbrains_action("RiderBackendAction-Property2Auto")

    def convert_anonymous_to_named_type():
        """TODO"""
        jetbrains_action("RiderBackendAction-Anonymous2Declared")

    def jetbrains_change_nullability():
        """TODO"""
        jetbrains_action("RiderBackendAction-ChangeNullability")

    def convert_unscoped_enum_to_scoped_enum():
        """TODO"""
        jetbrains_action("RiderBackendAction-CppConvertToScopedEnumAction")

    def pull_members_up():
        """TODO"""
        jetbrains_action("MembersPullUp")

    def rename():
        """TODO"""
        jetbrains_action("RenameElement")

    def make_method_static():
        """TODO"""
        jetbrains_action("RiderBackendAction-MakeStatic")

    def jetbrains_generic_refactor():
        """TODO"""
        jetbrains_action("Refactorings.QuickListPopupAction")

    def push_members_down():
        """TODO"""
        jetbrains_action("MemberPushDown")

    def encapsulate_field():
        """TODO"""
        jetbrains_action("RiderBackendAction-EncapsulateField")

    def adjust_namespaces():
        """TODO"""
        jetbrains_action("RiderBackendAction-Refactorings.AdjustNamespaces")

    def refactor_change_signature():
        """TODO"""
        jetbrains_action("ChangeSignature")

    def jetbrains_find_with_navigation_bar():
        """TODO"""
        # TODO: Does this work? There's also "ViewMembersInNavigationBar".
        jetbrains_action("ShowMembersInNavigationBar")

    def find_declaration_or_usages():
        """TODO"""
        # TODO: Is this right? Finds the usages?
        jetbrains_action("GotoDeclaration")

    def find_derived_symbols():
        """TODO"""
        # TODO: Is this right? Used twice.
        jetbrains_action("GotoSymbol")

    def find_type_declaration():
        """TODO"""
        jetbrains_action("GotoTypeDeclaration")

    def find_base_symbols():
        """TODO"""
        # TODO: Is this right? Used twice.
        # Is this "GotoClass"?
        jetbrains_action("GotoSymbol")

    def find_related_symbol():
        """TODO"""
        jetbrains_action("GotoRelated")

    # TODO: Keybind
    def goto_test():
        """TODO"""
        jetbrains_action("GotoTest")

    # TODO: Keybind
    def goto_class():
        """TODO"""
        jetbrains_action("GotoClass")


@jetbrains_context.action_class("app")
class AppActions:
    def path() -> str:
        return jetbrains_rpc_call("currentFile")


def to_clickables(jetbrains_ui_elements: List[Dict]) -> List[Clickable]:
    result = []
    for element in jetbrains_ui_elements:
        bounds_dict = element["croppedBounds"]
        if bounds_dict:
            bounds = Rect(
                bounds_dict["x"],
                bounds_dict["y"],
                bounds_dict["width"],
                bounds_dict["height"],
            )
            # uuid = element["uuid"]

            def focus_callback(bounds=bounds):
                # FIXME: I really want to bake the platform into this callback
                actions.user.jetbrains_rpc_call(
                    "uiElementAction",
                    [bounds.x, bounds.y, bounds.width, bounds.height, "focus"],
                )

            clickable = Clickable(bounds, focus_callback)

            result.append(clickable)
    return result


# TODO: Implement most of these at module level and bind them to speech
# commands, so they can be
@jetbrains_context.action_class("user")
class UserActions:
    def rename():
        jetbrains_action("RenameElement")

    def find_definition() -> None:
        # FIXME: This seems wrong
        # jetbrains_action("GotoAction")
        jetbrains_action("GotoDeclarationOnly")

    # def show_autocomplete() -> None:
    #     jetbrains_action("CodeCompletion")

    # def typecomplete() -> None:
    #     jetbrains_action("SmartTypeCompletion")

    def find_implementations() -> None:
        jetbrains_action("GotoImplementation")

    def find_references() -> None:
        jetbrains_action("FindUsages")

    # def find_type_declaration() -> None:
    #     jetbrains_action("FindTypeDeclaration")

    # def find_tests() -> None:
    #     jetbrains_action("GotoTest")

    def show_documentation() -> None:
        # raise NotImplementedError()
        # This doesn't work. Neither does `GotoDocumentation` or `QuickDocumentation`
        # jetbrains_action("ShowDocumentation")
        key("ctrl-q")

    # def wrap(wrapper: Optional[str] = None) -> None:
    #     jetbrains_action("SurroundWith")
    #     sleep("500ms")
    #     if wrapper:
    #         insert(wrapper)

    # def inline_code() -> None:
    #     jetbrains_action("Inline")

    # def extract_variable() -> None:
    #     jetbrains_action("IntroduceVariable")

    # def extract_method() -> None:
    #     jetbrains_action("ExtarctMethod")

    # def extract_parameter() -> None:
    #     jetbrains_action("IntroduceParameter")

    # def extract_constant() -> None:
    #     jetbrains_action("IntroduceConstant")

    # def extract_interface() -> None:
    #     jetbrains_action("ExtractInterface")

    # def refactor_move() -> None:
    #     jetbrains_action("Move")

    def project_root() -> str:
        return jetbrains_rpc_call("projectRoot")

    def surrounding_text() -> Optional[SurroundingText]:
        # TODO: If the voicemacs server is inactive, return nothing.
        raw_info = jetbrains_rpc_call("surroundingText", [30000, 30000])
        return SurroundingText(
            text_before=raw_info["textBefore"], text_after=raw_info["textAfter"]
        )

    def open_file_in_jetbrains(
        filename: str,
        start_name: str,
        focus_name: Optional[str] = None,
        focus_title: Optional[str] = None,
    ):
        """Open a specific file in a jetbrains product."""
        user.start_or_switch(start_name, focus_name, focus_title)
        jetbrains_action("openFile", [filename, True])

    def open_current_file_in_jetbrains(
        start_name: str,
        focus_name: Optional[str] = None,
        focus_title: Optional[str] = None,
    ):
        """Open the current file in a jetbrains product."""
        actions.self.open_file_in_jetbrains(
            app.path(), start_name, focus_name, focus_title
        )

    # TODO: Open the current project in jetbrains

    def open_current_file_in_rider():
        """Open the current file in JetBrains Rider."""
        actions.self.open_current_file_in_jetbrains("rider")

    def open_current_file_in_idea():
        """Open the current project in IntelliJ IDEA."""
        actions.self.open_current_file_in_jetbrains("idea")

    # TODO: Click buttons by index
    # TODO: Focus by index
    # TODO: Ace-jump from internal char positions

    def clickable_get_clickables() -> List[Clickable]:
        return to_clickables(actions.user.jetbrians_clickable_elements())

    def clickable_get_focusables() -> List[Clickable]:
        return to_clickables(actions.user.jetbrains_focusable_sections())


def bind_keys():
    try:
        actions.user.vimfinity_bind_keys(
            {
                "c": (actions.user.clickable_start_clickables, "Click by Keyboard"),
                "f": (actions.user.clickable_start_focusables, "Focus by Keyboard"),
                "p": "GitHub Copilot",
                "p p": (actions.user.copilot_chat, "Open Copilot Chat"),
                "p e": (actions.user.copilot_explain, "Explain This"),
                "p f": (actions.user.copilot_fix, "Fix This"),
                "p s": (actions.user.copilot_simplify, "Simplify This"),
                "p d": (actions.user.copilot_generate_docs, "Generate Docs"),
                "p t": (actions.user.copilot_generate_tests, "Generate Tests"),
                "p r": (actions.user.copilot_reference_file, "Reference File in Chat"),
                "p c": (
                    actions.user.copilot_full_suggestions,
                    "List Completions",
                ),
                "r": "Refactor",
                "r b": actions.user.use_base_type_where_possible,
                "r c": (actions.user.refactor_copy, "Copy"),
                "r d": (actions.user.refactor_safe_delete, "Safe Delete"),
                "r e": "Extract",
                "r e p": actions.user.extract_members_to_partial,
                # TODO: Does this exist?
                "r e v": actions.user.extract_variable,
                "r e m": actions.user.extract_method,
                "r e i": actions.user.extract_interface,
                "r e s": actions.user.extract_superclass,
                "r e c": actions.user.extract_class,
                "r e g": actions.user.extract_global_using,
                "r e c": actions.user.extract_content_placeholder,
                "r f": actions.user.move_types_into_matching_files,
                "r i": "Inline",
                "r i i": actions.user.inline,
                "r i m": actions.user.inline_master_page_content,
                "r i g": actions.user.inline_global_using,
                "r k": actions.user.invert_boolean,
                # TODO: Should this just be under extract?
                "r a": "Introduce",
                "r a a": actions.user.introduce_namespace_alias,
                "r a e": actions.user.introduce_using_enum,
                "r a f": actions.user.introduce_field,
                "r a p": actions.user.introduce_parameter,
                "r a t": actions.user.introduce_typedef,
                "r a v": actions.user.introduce_variable,
                "r m": (actions.user.refactor_move, "Move"),
                "r n": actions.user.make_method_non_static,
                "r o": "Convert",
                "r o p": actions.user.convert_method_to_property,
                "r o m": actions.user.convert_property_to_method,
                "r o d": actions.user.convert_method_to_indexer,
                "r o h": actions.user.convert_indexer_to_method,
                "r o i": actions.user.convert_abstract_class_to_interface,
                "r o a": actions.user.convert_interface_to_abstract_class,
                "r o e": actions.user.convert_static_to_extension_method,
                "r o s": actions.user.convert_extension_method_to_plain_static,
                "r o f": actions.user.convert_constructor_to_factory_method,
                "r o r": actions.user.jetbrains_transform_parameters,
                "r o u": actions.user.convert_property_to_auto_property,
                "r o t": actions.user.convert_anonymous_to_named_type,
                "r o n": actions.user.jetbrains_change_nullability,
                "r o c": actions.user.convert_unscoped_enum_to_scoped_enum,
                # TODO: Convert methods
                "r p": actions.user.pull_members_up,
                "r r": actions.user.rename,
                "r s": actions.user.make_method_static,
                "r t": (actions.user.jetbrains_generic_refactor, "Generic Refactor"),
                "r u": actions.user.push_members_down,
                "r w": actions.user.encapsulate_field,
                "r z": actions.user.adjust_namespaces,
                "r y": (actions.user.refactor_change_signature, "Change Signature"),
                "s": "Search/Lookup",
                "s n": actions.user.jetbrains_find_with_navigation_bar,
                "s d": actions.user.find_definition,
                "s u": actions.user.find_declaration_or_usages,
                "s f": actions.user.find_derived_symbols,
                "s i": actions.user.find_implementations,
                "s t": actions.user.find_type_declaration,
                "s b": actions.user.find_base_symbols,
                "s e": actions.user.find_related_symbol,
                "s r": actions.user.find_references,
            },
            context=jetbrains_context,
        )
    except KeyError:
        print("Failed to bind jetbrains vimfinity keys. Retrying in 1s.")
        cron.after("1s", bind_keys)


cron.after("50ms", bind_keys)
