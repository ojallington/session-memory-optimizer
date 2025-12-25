#!/bin/bash
# Session End Saver
# Automatically saves a quick checkpoint when session ends

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(dirname "$(dirname "$(dirname "$0")")")}"
CHECKPOINT_DIR="$PLUGIN_ROOT/data/checkpoints"
SESSION_START_FILE="$PLUGIN_ROOT/data/.session_start"

# Create checkpoint directory if it doesn't exist
mkdir -p "$CHECKPOINT_DIR"

# Calculate session duration
if [ -f "$SESSION_START_FILE" ]; then
    START_TIME=$(cat "$SESSION_START_FILE")
    START_EPOCH=$(date -d "$START_TIME" +%s 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%S" "$START_TIME" +%s 2>/dev/null || echo 0)
    NOW_EPOCH=$(date +%s)
    DURATION_SECS=$((NOW_EPOCH - START_EPOCH))
    DURATION_MINS=$((DURATION_SECS / 60))
else
    DURATION_MINS=0
fi

# Only auto-save if session was longer than 30 minutes
if [ "$DURATION_MINS" -gt 30 ]; then
    AUTO_CHECKPOINT="$CHECKPOINT_DIR/auto-$(date +%Y%m%d-%H%M%S).json"

    cat > "$AUTO_CHECKPOINT" << EOF
{
  "name": "auto-save",
  "timestamp": "$(date -Iseconds)",
  "type": "automatic",
  "duration_minutes": $DURATION_MINS,
  "note": "Automatically saved at session end. Use /session-restore to view details."
}
EOF

    echo "Session Memory Optimizer: Auto-checkpoint saved ($DURATION_MINS min session)"
fi

# Clean up old auto-checkpoints (keep last 5)
if [ -d "$CHECKPOINT_DIR" ]; then
    ls -t "$CHECKPOINT_DIR"/auto-*.json 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null
fi
