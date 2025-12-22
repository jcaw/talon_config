# Programmatic Access to Talon

How to interact with a running Talon instance programmatically.

## Direct REPL Access

**Not available.** Talon's REPL is a GUI window with no socket/IPC interface.

## Write-and-Reload Pattern

Talon auto-reloads Python files when they change. Use this for programmatic interaction:

1. Write Python code to a `.py` file in the user directory
2. Use `cron.after()` to defer execution until after file load
3. Read results from `$APPDATA/talon/talon.log`

### Example: Execute Code and Capture Output

```python
# scratch.py - write this file, Talon executes it automatically
from talon import cron, actions

def run():
    print("=== START ===")
    # Your code here
    result = actions.user.some_action()
    print(f"Result: {result}")
    print("=== END ===")

cron.after("1ms", run)
```

Then read `talon.log` for output between the markers.

### Gotchas

- **Running Talon instances** will reload immediately when you save
- **Remove scratch files** after use to avoid repeated execution
- **No return values** - communicate via print statements to the log
- **Timing** - increase cron delay if actions need UI elements to be ready

## File-Based RPC (VSCode Only)

The [command-server](https://github.com/pokey/command-server) pattern enables VSCode-Talon communication via JSON files:

1. External program writes `request.json` with command to execute
2. VSCode extension reads and executes the command
3. Extension writes `response.json` with results

This is specifically for VSCode integration, not general Talon access.

## Practical Workflow for Claude

To launch a dedicated talon instance to test or execute Talon code:

1. Write a Python file with test code using `cron.after()`
2. Write changes and inspect the log from a running talon instance, or run `./test_talon.sh` to launch a new instance of Talon and capture logs
3. Parse the log output for results
4. Delete the test file when done

See [TESTING.md](TESTING.md) for detailed testing instructions.
