# UI Automation

Talon provides access to the Windows UI Automation API (and macOS Accessibility API) for inspecting and interacting with application UI elements.

## Entry Point

```python
from talon import ui
```

## Core Functions

| Function | Description |
|----------|-------------|
| `ui.active_window()` | Currently focused window |
| `ui.active_app()` | Currently focused application |
| `ui.focused_element()` | Currently focused UI element |
| `ui.element_at(x, y)` | Element at screen coordinates |
| `ui.windows()` | All windows |
| `ui.apps()` | All applications |
| `ui.screens()` | All screens/monitors |

## Key Types

### Window

```python
window = ui.active_window()
window.title        # Window title
window.rect         # Bounds (Rect)
window.app          # Parent App
window.element      # Root UI element
window.focus()      # Focus this window
```

### Element

The core class for UI automation. Access UI elements through `window.element` or `ui.focused_element()`.

```python
element = ui.focused_element()

# Properties
element.name            # Element name/label
element.control_type    # "Button", "Edit", etc.
element.automation_id   # Unique identifier
element.rect            # Bounding rectangle
element.children        # Child elements
element.parent          # Parent element

# Search
buttons = element.find(control_type='Button')
ok_btn = element.find_one(control_type='Button', name='OK')

# Patterns (for interaction)
element.invoke_pattern.invoke()      # Click buttons
element.value_pattern.value          # Get/set text values
element.toggle_pattern.toggle()      # Toggle checkboxes
```

### Common Patterns

| Pattern | Use Case |
|---------|----------|
| `invoke_pattern` | Click buttons, links |
| `value_pattern` | Read/write text values |
| `toggle_pattern` | Checkboxes, toggle buttons |
| `scroll_pattern` | Scroll containers |
| `expandcollapse_pattern` | Expand/collapse menus, trees |
| `text_pattern` | Read document text content |
| `selection_pattern` | Get selected items |

**Important**: Patterns can return error strings instead of None when not supported. Always check:
```python
pattern = element.invoke_pattern
if pattern and not isinstance(pattern, str):
    pattern.invoke()
```

## Events

Register handlers for UI state changes:

```python
def on_focus(window):
    print(f"Focused: {window.title}")

ui.register("win_focus", on_focus)
ui.unregister("win_focus", on_focus)
```

| Event | Description |
|-------|-------------|
| `win_focus` | Window gained focus |
| `win_open` / `win_close` | Window opened/closed |
| `win_title` | Window title changed |
| `app_activate` / `app_deactivate` | App focus changed |
| `screen_change` | Screen configuration changed |

## Common Patterns

### Find and Click a Button

```python
window = ui.active_window()
btn = window.element.find_one(control_type='Button', name='OK')
if btn:
    invoke = btn.invoke_pattern
    if invoke and not isinstance(invoke, str):
        invoke.invoke()
```

### Walk UI Tree

```python
def walk(element, depth=0):
    print("  " * depth + f"{element.control_type}: {element.name}")
    try:
        for child in element.children:
            walk(child, depth + 1)
    except (OSError, RuntimeError):
        pass  # Element became stale

walk(ui.active_window().element)
```

## Detailed Reference

See `settings/api_exploration/ui_automation/UI_AUTOMATION_API_EXPLORATION.md` for complete API documentation including:
- All 103 Element attributes
- All pattern types and their methods
- Control type reference
- Error handling patterns
- Text location and character bounds
- Mac-specific notes

See `settings/api_exploration/ui_automation/EVENTS.md` for event handling details.
