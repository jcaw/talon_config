#!/bin/bash
# Bash script to run talon_console.exe with a timeout and capture log output
# Usage: ./test_talon.sh [timeout_seconds]
# Default timeout: 10 seconds

TIMEOUT=${1:-10}
TALON_LOG="${APPDATA}/talon/talon.log"
OUTPUT_LOG="$(dirname "$0")/../user_test.log"

# Convert Windows path if needed (for Cygwin/MSYS)
[[ "$TALON_LOG" == *"\\"* ]] && TALON_LOG=$(cygpath -u "$APPDATA/talon/talon.log" 2>/dev/null || echo "../talon.log")

echo "================================================"
echo "Starting Talon console with ${TIMEOUT}s timeout..."
echo "================================================"
echo ""

# Record start state
LOG_START_SIZE=$([ -f "$TALON_LOG" ] && wc -c < "$TALON_LOG" || echo 0)
START_TIME=$(date +%s)

# Start talon_console.exe in the background
talon_console.exe &
TALON_PID=$!
sleep 1

# Function to kill test processes
kill_test_processes() {
    # Kill talon_console if still running
    kill -0 $TALON_PID 2>/dev/null && { kill $TALON_PID 2>/dev/null; sleep 0.3; kill -9 $TALON_PID 2>/dev/null; }

    # Kill talon.exe processes started during this test (leaves existing instances alone)
    powershell -Command '$st = (Get-Date "1970-01-01").AddSeconds('"$START_TIME"'); Get-Process -Name talon,talon_console -ErrorAction SilentlyContinue | Where-Object { $_.StartTime -gt $st } | ForEach-Object { wmic process where "ProcessId=$($_.Id)" delete }' 2>/dev/null
}

# Set up timeout
(sleep $TIMEOUT && kill_test_processes) &
KILLER_PID=$!

# Wait for talon to exit
wait $TALON_PID 2>/dev/null
EXIT_CODE=$?

# Clean up
kill $KILLER_PID 2>/dev/null
wait $KILLER_PID 2>/dev/null
sleep 0.5
kill_test_processes

# Extract and save log output
echo "=== TALON LOG OUTPUT ==="
if [ -f "$TALON_LOG" ]; then
    NEW_BYTES=$(($(wc -c < "$TALON_LOG") - LOG_START_SIZE))
    [ $NEW_BYTES -gt 0 ] && tail -c $NEW_BYTES "$TALON_LOG" | tee "$OUTPUT_LOG" || echo "(no new log output)" | tee "$OUTPUT_LOG"
    echo ""
    echo "(Output also saved to $OUTPUT_LOG)"
else
    echo "(log file not found at $TALON_LOG)" | tee "$OUTPUT_LOG"
fi

# Show result
echo ""
echo "================================================"
ps -p $TALON_PID > /dev/null 2>&1 && echo "Talon is still running (shouldn't happen)" || { [ $EXIT_CODE -eq 0 ] && echo "Talon exited cleanly" || echo "*** KILLED DUE TO TIMEOUT (${TIMEOUT}s) ***"; }
echo "================================================"
