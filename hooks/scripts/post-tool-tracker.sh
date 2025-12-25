#!/bin/bash
# Post-tool tracker hook for Session Memory Optimizer
# Records tool usage to metrics for health calculation

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(dirname "$(dirname "$(dirname "$0")")")}"
METRICS_SCRIPT="$PLUGIN_ROOT/scripts/metrics-tracker.py"

# Read the hook input from stdin
input=$(cat)

# Extract tool name from the input JSON
tool_name=$(echo "$input" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name','Unknown'))" 2>/dev/null)

# Record the tool usage
if [ -f "$METRICS_SCRIPT" ]; then
    echo "$input" | python3 "$METRICS_SCRIPT" record "$tool_name" 2>/dev/null
fi

# Exit cleanly (don't block the tool)
exit 0
