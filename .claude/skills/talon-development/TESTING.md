# Command-Line Testing for Talon

This document covers how to test Talon configuration changes from the command line.

## Test Script

Use `test_talon.sh` in the user directory root to test changes:

```bash
# Default 10 second timeout
./test_talon.sh

# Custom timeout (in seconds)
./test_talon.sh 15
```

The script:
1. Launches `talon_console.exe` (must be on PATH)
2. Captures log output from `$APPDATA/talon/talon.log`
3. Saves output to `../user_test.log`
4. Only kills Talon processes started during the test (preserves existing instances)
5. Terminates after the timeout period

## Testing Actions with Cron

**Critical:** Actions aren't available until after the file finishes loading. Use `cron.after()` for deferred execution:

```python
from talon import cron, actions

@module.action_class
class Actions:
    def my_action():
        """Do something."""
        print("Action executed")

# WRONG - action not yet available:
# actions.user.my_action()

# CORRECT - deferred execution:
cron.after("1ms", lambda: actions.user.my_action())
```

## Test Code Template

```python
from talon import cron, actions

# ... your action definitions ...

# Test code (REMOVE BEFORE COMMITTING)
def run_tests():
    print("=== TESTING STARTED ===")
    try:
        result = actions.user.my_action("test input")
        assert result == "expected", f"Got: {result}"
        print("=== ALL TESTS PASSED ===")
    except Exception as e:
        import traceback
        print(f"=== TEST FAILED ===")
        traceback.print_exc()

cron.after("1ms", run_tests)
```

## Common Test Patterns

### Testing OCR Functions

```python
def test_ocr():
    print("=== TESTING OCR ===")
    results = actions.user.ocr_window()
    print(f"Found {len(results)} OCR results")
    print("=== OCR TEST PASSED ===")

cron.after("1ms", test_ocr)
```

### Testing Icon Detection

```python
def test_icon():
    print("=== TESTING ICON DETECTION ===")
    coords = actions.user.find_icon_in_window("user/assets/icons/test.png")
    if coords:
        print(f"Icon found at {coords}")
        print("=== ICON TEST PASSED ===")
    else:
        print("=== ICON TEST FAILED: Icon not found ===")

cron.after("1ms", test_icon)
```

### Testing Mouse Actions

```python
def test_mouse():
    print("=== TESTING MOUSE ACTION ===")
    original = ctrl.mouse_pos()
    actions.user.click_point(100, 100)
    restored = ctrl.mouse_pos()
    if original == restored:
        print("=== MOUSE TEST PASSED ===")
    else:
        print(f"=== MOUSE TEST FAILED: Position not restored ===")

cron.after("1ms", test_mouse)
```

## Testing Tips

- Use clear markers (`=== TEST NAME ===`) for easy log searching
- Print intermediate values liberally for debugging
- Check `../user_test.log` after test runs
- **Remove test code before committing**
- If testing UI actions, increase cron delay (e.g., `"500ms"`) for elements to appear
- Running Talon instances will auto-reload modified files and fire test code

## Interpreting Output

### Success Indicators
- No Python tracebacks
- Test markers appear (`TEST PASSED`, etc.)
- Actions execute without errors

### Failure Indicators
- Python tracebacks with line numbers
- `TEST FAILED` markers
- Missing expected output
- Talon fails to load entirely

## Debugging Failed Tests

1. **Import errors** - Prevent file from loading entirely
2. **Action name typos** - Check exact spelling in error message
3. **Timing issues** - Increase `cron.after()` delay
4. **Missing context** - Verify `.matches` pattern is active
5. **Syntax errors** - Check Python syntax; errors prevent file loading
6. **File paths** - Relative paths may not resolve as expected

## Viewing Logs

```python
# In code - print statements go to talon.log
print("Debug: value =", some_value)
```

Via voice command: `talon show log`
