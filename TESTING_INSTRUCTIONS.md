# Command-Line Testing Instructions

## Overview

This document is designed to explain to an LLM how to check (some of) the config via the command line.

## Running Tests

Use the `test_talon.sh` script to test Talon changes:

```bash
# Run with default 10 second timeout
./test_talon.sh

# Run with custom timeout (in seconds)
./test_talon.sh 15
```

The script:
1. Launches `talon_console.exe` (assumes it's on PATH)
2. Reads from Talon's log file (`$APPDATA/talon/talon.log`)
3. Displays all errors, warnings, and debug output
4. Saves the output to `../user_test.log` for easy access
5. Only kills Talon processes created during the test run (preserves your existing Talon instance)
6. Terminates after the timeout period

## Testing Actions

### Important: Use Cron for Testing Actions

When testing actions defined in a file, you **cannot** call them directly at the bottom of the file. Actions are not accessible until after the entire file is loaded.

**Incorrect:**
```python
@module.action_class
class MyActions:
    def my_test_action():
        print("Testing...")

# This won't work - action will not yet be available
actions.user.my_test_action()
```

**Correct:**
```python
from talon import cron

@module.action_class
class MyActions:
    def my_test_action():
        print("Testing...")

# This should work - action call won't fire until the file has been fully loaded
cron.after("1ms", lambda: actions.user.my_test_action())
```

### Example Testing Workflow

1. **Add test code to your module:**
   ```python
   from talon import cron

   # Your action definitions here...

   # Test code at bottom of file
   def test_my_changes():
       print("=== TESTING STARTED ===")
       try:
           actions.user.my_action()
           print("=== TEST PASSED ===")
       except Exception as e:
           print(f"=== TEST FAILED: {e} ===")

   cron.after("1ms", test_my_changes)
   ```

   (Note any active instances of Talon running will auto-reload the file and fire the action, which may be undesirable.)

2. **Run the test script:**
   ```bash
   ./test_talon.sh
   ```

3. **Check the output** for your test markers (`TESTING STARTED`, `TEST PASSED`, etc.) or read `../user_test.log`

4. **Remove test code** before committing (keep production code clean)

### Testing Tips

- Use clear markers like `=== TEST NAME ===` to find your output easily
- Print liberally - console output is your main debugging tool

## Common Testing Scenarios

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

Note how this test is imperfect - it doesn't actually test the click location.

## Interpreting Output

### Success Indicators
- No Python tracebacks
- Your test markers appear (`TEST PASSED`, etc.)
- Actions execute without errors

### Failure Indicators
- Python tracebacks with line numbers
- `TEST FAILED` markers
- Missing expected output
- Talon fails to load entirely

## Debugging Failed Tests

1. **Check for import errors** - these prevent file loading
2. **Verify action names** - typos in action calls are common
3. **Check timing** - increase cron delay if UI elements aren't ready
4. **Look for syntax errors** - Python errors prevent file loading
5. **Verify file paths** - relative paths may not work as expected

## Notes

- The test script kills Talon after the timeout, so don't use it for interactive testing
