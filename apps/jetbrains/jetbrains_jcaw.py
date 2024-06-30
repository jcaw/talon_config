"""Separate action implementations for jetbrains products"""

import re
from typing import Optional, List, Dict, Callable

from talon import Context, actions, Module, cron, app, ui
from talon.ui import Rect

from user.utils.formatting import SurroundingText
from user.misc.clickable_overlay.clickable_overlay import Clickable


user = actions.user
edit = actions.edit
idea = actions.user.idea
sleep = actions.sleep
key = actions.key
insert = actions.insert
jetbrains_rpc_call = actions.user.jetbrains_rpc_call
jetbrains_action = actions.user.jetbrains_action
automator_overlay = actions.user.automator_overlay


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


@module.action_class
class JetbrainsActions:
    def jetbrains_search_everywhere_menu():
        """Open the search everywhere (double shift) menu in Jetbrains IDEs."""
        jetbrains_action("SearchEverywhere")

    def jetbrains_hide_active_window():
        """Hide the active window."""
        jetbrains_action("HideActiveWindow")

    def jetbrains_hide_tools():
        """Hide all the tool windows."""
        jetbrains_action("HideAllWindows")

    def jetbrains_hide_side_windows():
        """Hide "minor" windows (this includes e.g. Copilot Chat, but excludes files)."""
        jetbrains_action("HideSideWindows")

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

    def search_thing_in_rider():
        """Search the current thing (dwim - usually the highlighted text) in the active Rider project."""
        text = actions.user.get_that_dwim()
        actions.user.open_rider()
        # Give it time for the Talon context to update.
        sleep("300ms")
        actions.self.jetbrains_search_everywhere_menu()
        sleep("100ms")
        user.paste_insert(text)

    def jetbrains_reopen_file():
        """Close, then reopen, the current file."""
        current_file = jetbrains_rpc_call("currentFile")
        jetbrains_action("CloseActiveTab")
        jetbrains_rpc_call("openFile", [current_file, False])

    def jetbrains_switch_header_and_source():
        """Switch between a source file and its header."""
        jetbrains_action("SwitchHeaderSource")


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


def copilot_chat_message(message, submit=True):
    actions.key("escape")
    actions.self.copilot_open_chat()
    key("ctrl-a")
    # TODO: Possibly copy what's already there?
    sleep("100ms")
    user.paste_insert(f"{message}")
    sleep("100ms")
    if submit:
        key("enter")


def copilot_chat_command(command):
    # In case the chat is already open
    actions.key("escape")
    actions.self.copilot_open_chat()
    key("ctrl-a")
    sleep("100ms")
    # Add a space after so "enter" doesn't just select the autocomplete candidate.
    actions.insert(f"{command} ")
    sleep("100ms")
    key("enter")
    # actions.insert("test")


# Old code explain wording - new wording below:
#
# COPILOT_EXPLAIN_CODE_TEMPLATE = """Please explain the following code:

# ```{language}
# {code_text}
# ```"""

COPILOT_EXPLAIN_CODE_TEMPLATE = """Please explain this code:

```{language}
{code_text}
```"""

# FIXME: Including the compilation bug causes a weird error, seemingly caused by
#   exceeding the max tokens. For now, just don't include it.
COPILOT_EXPLAIN_COMPILATION_ERROR_COMPLEX = """I'm getting an error I that I don't understand. I will list the compilation output, then the error, then the line the compiler claims is causing trouble.

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

COPILOT_EXPLAIN_COMPILATION_ERROR = """I'm getting a compilation error I that I don't understand:
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

    def copilot_generate_docs():
        """Generate docs at point with copilot."""

    def copilot_explain():
        """Explain the current file with copilot."""

    def copilot_explain_highlighted():
        """Explain the highlighted code in the current file with copilot."""

    def copilot_explain_error():
        """Explain the currently selected error in the build window."""

    def copilot_quote_highlighted():
        """Open the Copilot Chat window, and quote the highlighted text in a block.

        You can then fill in the rest of the query, and submit it.

        """

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

    def jetbrains_switch_and_ask_copilot(
        message: str, switch_function: Callable[[], None] = user.open_rider
    ):
        """Switch to (or start) a Jetbrains IDE and ask copilot a question"""
        switch_function()
        copilot_chat_message(message)

    def copilot_explain_current_function():
        """Ask GitHub Copilot to explain the function that's being edited (not the function being called)."""


@jetbrains_context.action_class("user")
class JetbrainsCopilotActions:
    def copilot_open_chat():
        # NOTE: For now, we assume it opens in a separate window. This method
        #   will always be slow if that assumption is wrong.
        try:
            # We want to disambiguate, only opening the current IDE's chat window
            actions.user.focus(
                app_name=ui.active_window().app.name, title="GitHub Copilot Chat"
            )
            sleep("200ms")
            # actions.user.focus_and_wait(
            #     focus_name=ide_app_name,
            #     focus_title="GitHub Copilot Chat",
            #     timeout="5s",
            #     start_delay="5s",
            # )
        except (IndexError, ui.UIErr):
            with automator_overlay("Opening Copilot Chat"):
                jetbrains_action("ActivateGitHubCopilotChatToolWindow")
                # jetbrains_action("copilot.chat.show")
                sleep("2s")

    def copilot_generate_docs():
        copilot_chat_command("/doc")

    def copilot_explain():
        copilot_chat_command("/explain")

    # TODO: Explain the current "thing", instead of just what's highlighted
    def copilot_explain_highlighted():
        text = user.get_highlighted()
        if " " in text.strip():
            # TODO: language
            message = COPILOT_EXPLAIN_CODE_TEMPLATE.format(language="", code_text=text)
        else:
            message = f"Explain `{text.strip()}`"
        copilot_chat_message(message)

    def copilot_explain_error():
        INCLUDE_COMPILATION_OUTPUT = False

        # Assumes the error is focussed.
        error_message = user.get_highlighted()

        if INCLUDE_COMPILATION_OUTPUT:
            # Grab the compilation output
            # HACK: I don't know the shortcut or action to jump to the compilation
            #   window, so just press tab twice.
            key("tab:2")
            edit.select_all()
            compilation_output = user.get_highlighted()
            # Dehighlight, jump to end
            key("right")
            key("shift-tab:2")

        # Jump to source
        key("f4")
        key("home")
        key("shift-end")
        code = user.get_highlighted()

        if INCLUDE_COMPILATION_OUTPUT:
            text = COPILOT_EXPLAIN_COMPILATION_ERROR_COMPLEX.format(
                compilation_output=compilation_output,
                error_message=error_message,
                code_responsible=code,
            )
        else:
            text = COPILOT_EXPLAIN_COMPILATION_ERROR.format(
                error_message=error_message,
                code_responsible=code,
            )
        copilot_chat_message(text)

    def copilot_quote_highlighted():
        text = user.get_highlighted()
        # DWIM behaviour based on what we're copying
        if " " in text.strip():
            # For code snippets, use a block quote
            message = COPILOT_QUOTE_MESSAGE.format(text=text)
        else:
            # If it's just a name, use a short quoting style.
            message = f" `{text.strip()}`"
        copilot_chat_message(message, submit=False)
        # Go back to the very start of the message
        key("ctrl-home")

    def copilot_fix():
        copilot_chat_command("/fix")

    def copilot_simplify():
        copilot_chat_command("/simplify")

    def copilot_generate_tests():
        copilot_chat_command("/tests")

    def copilot_reference_file():
        # Use the convoluted menu approach, because it allows files to be more
        # easily added from any context - e.g. the file list, editor, etc.
        copilot_click("Reference File in Chat")

    def copilot_full_suggestions():
        jetbrains_action("copilot.openCopilot")

    def copilot_explain_current_function():
        # TODO 1: Programmatically get current function name, and use that as the reference
        raise NotImplementedError()


# TODO: Pull the rider-specific methods into the Rider context. Test them first though.
@module.action_class
class RefactorActions:
    def use_base_type_where_possible():
        """Refactor to use the base type wherever possible."""

    def refactor_copy():
        """Refactor to copy the current thing."""
        # TODO: Is this right?
        jetbrains_action("CopyReference")

    def refactor_safe_delete():
        """Safely delete this thing."""
        jetbrains_action("SafeDelete")

    def extract_members_to_partial():
        """TODO"""

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

    def inline_global_using():
        """TODO"""

    def invert_boolean():
        """TODO"""

    def introduce_namespace_alias():
        """TODO"""

    def introduce_using_enum():
        """TODO"""

    def introduce_field():
        """TODO"""
        jetbrains_action("IntroduceField")

    def introduce_parameter():
        """TODO"""
        jetbrains_action("IntroduceParameter")

    def introduce_typedef():
        """TODO"""

    def introduce_variable():
        """TODO"""

    def refactor_move():
        """TODO"""
        jetbrains_action("Move")

    def make_method_non_static():
        """TODO"""

    def convert_method_to_property():
        """TODO"""

    def convert_property_to_method():
        """TODO"""

    def convert_method_to_indexer():
        """TODO"""

    def convert_indexer_to_method():
        """TODO"""

    def convert_abstract_class_to_interface():
        """TODO"""

    def convert_interface_to_abstract_class():
        """TODO"""

    def convert_static_to_extension_method():
        """TODO"""

    def convert_extension_method_to_plain_static():
        """TODO"""

    def convert_constructor_to_factory_method():
        """TODO"""

    def jetbrains_transform_parameters():
        """TODO"""

    def convert_property_to_auto_property():
        """TODO"""

    def convert_anonymous_to_named_type():
        """TODO"""

    def jetbrains_change_nullability():
        """TODO"""

    def convert_unscoped_enum_to_scoped_enum():
        """TODO"""

    def pull_members_up():
        """TODO"""
        jetbrains_action("MembersPullUp")

    def rename():
        """TODO"""
        jetbrains_action("RenameElement")

    def make_method_static():
        """TODO"""

    def jetbrains_generic_refactor():
        """TODO"""
        jetbrains_action("Refactorings.QuickListPopupAction")

    def push_members_down():
        """TODO"""
        jetbrains_action("MemberPushDown")

    def encapsulate_field():
        """TODO"""

    def adjust_namespaces():
        """TODO"""

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

    def jetbrains_build_project():
        """Build the current project."""
        jetbrains_action("BuildSolutionAction")

    def jetbrains_run_project():
        """Build and run the current project."""
        jetbrains_action("Run")

    def jetbrains_debug_project():
        """Build and run a debug build of the current project."""
        jetbrains_action("Debug")

    def jetbrains_terminate_build():
        """Terminate the current build."""
        jetbrains_action("CancelBuildAction")

    def jetbrains_compile_file():
        """Compile just the current file."""
        jetbrains_action("CompileFile")

    def jetbrains_delete_line():
        """Delete the entire current line."""
        jetbrains_action("EditorDeleteLine")


@module.action_class
class MarkerActions:
    # TODO: Remove
    # def push_or_toggle_marker():
    #     """Push the marker - if the cursor is over the marker, toggles it on/off instead."""
    #     jetbrains_rpc_call("pushOrToggleMarker")

    def push_marker():
        """Push the marker in the current editor."""
        jetbrains_rpc_call("pushMarker")

    def enable_and_push_marker():
        """Enable the marker selection, then push a new marker at the caret."""
        jetbrains_rpc_call("enableAndPushMarker")

    def pop_marker():
        """Pop the last marker off the current editor's stack, but don't move to it."""
        jetbrains_rpc_call("popMarker")

    def pop_and_move_to_marker():
        """Pop the last marker off the current editor's stack and jump to it."""
        jetbrains_rpc_call("popAndMoveToMarker")

    def pop_and_enable_marker():
        """Pop the last marker off the current stack, then enable the selection from the previous marker."""
        jetbrains_rpc_call("popAndEnableMarker")

    def enable_marker():
        """Enable the marker."""
        jetbrains_rpc_call("enableMarker")

    def disable_marker():
        """Disable the marker."""
        jetbrains_rpc_call("disableMarker")

    def pop_global_marker():
        """Pop the last marker off the global stack and jump to it."""
        jetbrains_rpc_call("popGlobalMarker")

    def enable_visual_markers():
        """Enable marker visualisations in the editor."""
        jetbrains_rpc_call("enableVisualMarkers")

    def disable_visual_markers():
        """Disable marker visualisations in the editor."""
        jetbrains_rpc_call("disableVisualMarkers")

    def toggle_visual_markers():
        """Toggle marker visualisations in the editor."""
        jetbrains_rpc_call("toggleVisualMarkers")

    def flash_visual_markers():
        """Show marker visualisations in the editor for just a short duration."""
        jetbrains_rpc_call("flashVisualMarkers")


@module.action_class
class GitActions:
    def jetbrains_include_changed_lines():
        """Include the current change in the next commit."""
        jetbrains_rpc_call("Vcs.Diff.IncludeChangedLinesIntoCommit")

    def jetbrains_exclude_changed_lines():
        """Include the current change in the next commit."""
        jetbrains_rpc_call("Vcs.Diff.ExcludeChangedLinesFromCommit")

    def jetbrains_revert_changed_lines():
        """Revert the current VCS change to the current head."""
        jetbrains_rpc_call("Vcs.RevertSelectedChanges")


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

    def search(text: str = None):
        actions.self.jetbrains_search_everywhere_menu()
        sleep("100ms")
        if text:
            insert(text)

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

    # TODO: Click buttons by index
    # TODO: Focus by index
    # TODO: Ace-jump from internal char positions

    def clickable_get_clickables() -> List[Clickable]:
        return to_clickables(actions.user.jetbrians_clickable_elements())

    def clickable_get_focusables() -> List[Clickable]:
        return to_clickables(actions.user.jetbrains_focusable_sections())


@jetbrains_context.action_class("edit")
class JetbrainsEditActions:
    # TODO: Zoom actions by action name, not just keys
    def zoom_in():
        key("alt-shift-+")

    def zoom_out():
        key("alt-shift--")


@rider_context.action_class("user")
class RiderActions:
    def use_base_type_where_possible():
        # TODO: Is this right?
        jetbrains_action("RiderBackendAction-UseBaseTypeAction")

    def inline_master_page_content():
        jetbrains_action("RiderBackendAction-InlineContent")

    def inline_global_using():
        jetbrains_action("RiderBackendAction-InlineGlobalUsing")

    def invert_boolean():
        jetbrains_action("RiderBackendAction-InvertBool")

    def introduce_namespace_alias():
        jetbrains_action("RiderBackendAction-CppIntroduceNamespaceAlias")

    def introduce_using_enum():
        jetbrains_action("RiderBackendAction-CppIntroduceUsingEnum")

    def introduce_typedef():
        jetbrains_action("RiderBackendAction-CppIntroduceType")

    def introduce_variable():
        jetbrains_action("RiderBackendAction-CppIntroduceType")

    def make_method_non_static():
        jetbrains_action("RiderBackendAction-MakeNonStatic")

    def extract_members_to_partial():
        # TODO: Is this right?
        jetbrains_action("RiderBackendAction-Type2Partial")

    def convert_method_to_property():
        jetbrains_action("RiderBackendAction-Function2Property")

    def convert_property_to_method():
        jetbrains_action("RiderBackendAction-Property2Function")

    def convert_method_to_indexer():
        jetbrains_action("RiderBackendAction-Function2Indexer")

    def convert_indexer_to_method():
        jetbrains_action("RiderBackendAction-Indexer2Function")

    def convert_abstract_class_to_interface():
        jetbrains_action("RiderBackendAction-Abstract2Interface")

    def convert_interface_to_abstract_class():
        jetbrains_action("RiderBackendAction-Interface2Abstract")

    def convert_static_to_extension_method():
        jetbrains_action("RiderBackendAction-Static2ExtensionAction")

    def convert_extension_method_to_plain_static():
        jetbrains_action("RiderBackendAction-Extension2StaticAction")

    def convert_constructor_to_factory_method():
        jetbrains_action("RiderBackendAction-Constructor2FactoryMethodAction")

    def convert_property_to_auto_property():
        jetbrains_action("RiderBackendAction-Property2Auto")

    def convert_anonymous_to_named_type():
        jetbrains_action("RiderBackendAction-Anonymous2Declared")

    def jetbrains_transform_parameters():
        jetbrains_action("RiderBackendAction-TransformParameters")

    def jetbrains_change_nullability():
        jetbrains_action("RiderBackendAction-ChangeNullability")

    def convert_unscoped_enum_to_scoped_enum():
        jetbrains_action("RiderBackendAction-CppConvertToScopedEnumAction")

    def make_method_static():
        jetbrains_action("RiderBackendAction-MakeStatic")

    def encapsulate_field():
        jetbrains_action("RiderBackendAction-EncapsulateField")

    def adjust_namespaces():
        jetbrains_action("RiderBackendAction-Refactorings.AdjustNamespaces")


MENU_NAME_RE = re.compile(r"[^()A-Za-z0-9 ]")


def make_inserter(text_to_insert: str, name_in_menu: Optional[str] = None):
    """Utility function to create an insertion binding for vimfinity."""
    if not isinstance(name_in_menu, str):
        name_in_menu = MENU_NAME_RE.sub("", text_to_insert).strip()
    return (lambda: insert(text_to_insert), name_in_menu)


def bind_keys():
    try:
        actions.user.vimfinity_bind_keys(
            {
                # General top-level actions
                "l": (actions.user.jetbrains_delete_line, "Delete Line"),
                "pagedown": (lambda: key("f7"), "Next Thing"),
                "pageup": (lambda: key("shift-f7"), "Previous Thing"),
                "end": (lambda: key("alt-shift-right"), "Next File"),
                "home": (lambda: key("alt-shift-left"), "Previous File"),
                "k": "Jetbrains",
                "k h": (actions.user.jetbrains_hide_tools, "Hide Tool Windows"),
                "k a": (actions.user.jetbrains_hide_active_window, "Hide Window"),
                "k s": (actions.user.jetbrains_hide_side_windows, "Hide Side Windows"),
                "k r": (actions.user.jetbrains_reopen_file, "Reopen File"),
                "c": (actions.user.clickable_start_clickables, "Click by Keyboard"),
                "f": (actions.user.clickable_start_focusables, "Focus by Keyboard"),
                "b": "Build",
                "b b": (actions.user.jetbrains_run_project, "Run Project"),
                "b c": (actions.user.jetbrains_build_project, "Build Project"),
                "b d": (actions.user.jetbrains_debug_project, "Debug Project"),
                "b t": (actions.user.jetbrains_terminate_build, "Terminate"),
                "b f": (actions.user.jetbrains_compile_file, "Compile File"),
                # TODO: Pull out to Rider-only actions?
                # "b a": (actions.user.jetbrains_attach_debugger, "Attach Debugger"),
                "p": "GitHub Copilot",
                "p p": (actions.user.copilot_open_chat, "Open Copilot Chat"),
                "p q": (actions.user.copilot_explain, "Explain File"),
                "p e": (
                    actions.user.copilot_explain_highlighted,
                    "Explain Highlighted",
                ),
                # "x" for "exception"
                "p x": (actions.user.copilot_explain_error, "Explain Error"),
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
                "r o p": (
                    actions.user.convert_method_to_property,
                    "Method to Property",
                ),
                "r o m": (
                    actions.user.convert_property_to_method,
                    "Property to Method",
                ),
                "r o d": (actions.user.convert_method_to_indexer, "Method to Indexer"),
                "r o h": (actions.user.convert_indexer_to_method, "Indexer to Method"),
                "r o i": (
                    actions.user.convert_abstract_class_to_interface,
                    "Abstract Class to Interface",
                ),
                "r o a": (
                    actions.user.convert_interface_to_abstract_class,
                    "Interface to Abstract Class",
                ),
                "r o e": (
                    actions.user.convert_static_to_extension_method,
                    "Static to Extension Method",
                ),
                "r o s": (
                    actions.user.convert_extension_method_to_plain_static,
                    "Extension Method to Plain Static",
                ),
                "r o f": (
                    actions.user.convert_constructor_to_factory_method,
                    "Constructor to Factory Method",
                ),
                "r o r": (
                    actions.user.jetbrains_transform_parameters,
                    "Transform Parameters",
                ),
                "r o u": (
                    actions.user.convert_property_to_auto_property,
                    "Property to Auto Property",
                ),
                "r o t": (
                    actions.user.convert_anonymous_to_named_type,
                    "Anonymous to Named Type",
                ),
                "r o n": (
                    actions.user.jetbrains_change_nullability,
                    "Change Nullability",
                ),
                "r o c": (
                    actions.user.convert_unscoped_enum_to_scoped_enum,
                    "Unscoped Enum to Scoped Enum",
                ),
                # TODO: Convert methods
                "r p": actions.user.pull_members_up,
                "r r": actions.user.rename,
                "r s": actions.user.make_method_static,
                "r t": (actions.user.jetbrains_generic_refactor, "Generic Refactor"),
                "r u": actions.user.push_members_down,
                "r w": actions.user.encapsulate_field,
                "r z": actions.user.adjust_namespaces,
                "r y": (actions.user.refactor_change_signature, "Change Signature"),
                "'": "Search/Lookup",
                "' n": (
                    actions.user.jetbrains_find_with_navigation_bar,
                    "Find with Navigation Bar",
                ),
                "' d": actions.user.find_definition,
                "' u": actions.user.find_declaration_or_usages,
                "' f": actions.user.find_derived_symbols,
                "' i": actions.user.find_implementations,
                "' t": actions.user.find_type_declaration,
                "' b": actions.user.find_base_symbols,
                "' e": actions.user.find_related_symbol,
                "' r": actions.user.find_references,
                "m": "Markers",
                "space": actions.user.enable_and_push_marker,
                "u": actions.user.pop_marker,
                "m e": actions.user.enable_marker,
                "m d": actions.user.disable_marker,
                "m p": actions.user.pop_and_move_to_marker,
                "m [": actions.user.pop_and_enable_marker,
                "m g": actions.user.pop_global_marker,
                "m space": actions.user.push_marker,
                "m v": actions.user.toggle_visual_markers,
                # These two bindings don't matter, they are arbitrary. Bump them if another is more important.
                "m i": actions.user.enable_visual_markers,
                "m o": actions.user.disable_visual_markers,
                "m f": actions.user.flash_visual_markers,
                "g": "Git/Version Control",
                "g s": (actions.user.jetbrains_include_changed_lines, "Stage Change"),
                "g u": (actions.user.jetbrains_exclude_changed_lines, "Unstage Change"),
                "g k": (
                    actions.user.jetbrains_discard_changed_lines,
                    "Discard Changes",
                ),
            },
            context=jetbrains_context,
        )

        actions.user.vimfinity_bind_keys(
            {
                # Insertion
                "i t": make_inserter("// TODO [jcaw]: "),
                "i f": make_inserter("// FIXME [jcaw]: "),
                "i h": make_inserter("// HACK [jcaw]: "),
                # Navigation
                "' h": (
                    actions.user.jetbrains_switch_header_and_source,
                    "Switch to Header/Source",
                ),
            },
            context=rider_context,
        )
    except KeyError:
        print("Failed to bind jetbrains vimfinity keys. Retrying in 1s.")
        cron.after("1s", bind_keys)


cron.after("50ms", bind_keys)
