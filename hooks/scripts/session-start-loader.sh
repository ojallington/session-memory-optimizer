#!/bin/bash
# Session Start Loader
# Checks for recent checkpoints and notifies user of restoration options

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(dirname "$(dirname "$(dirname "$0")")")}"
CHECKPOINT_DIR="$PLUGIN_ROOT/data/checkpoints"

# Create checkpoint directory if it doesn't exist
mkdir -p "$CHECKPOINT_DIR"

# Check for recent checkpoints (within last 24 hours)
if [ -d "$CHECKPOINT_DIR" ]; then
    RECENT_CHECKPOINTS=$(find "$CHECKPOINT_DIR" -name "*.json" -mtime -1 2>/dev/null | wc -l)

    if [ "$RECENT_CHECKPOINTS" -gt 0 ]; then
        echo "SESSION MEMORY OPTIMIZER"
        echo "========================"
        echo "Found $RECENT_CHECKPOINTS recent checkpoint(s)."
        echo ""
        echo "To restore previous session context:"
        echo "  /session-restore <name>"
        echo ""
        echo "Available checkpoints:"
        for checkpoint in "$CHECKPOINT_DIR"/*.json; do
            if [ -f "$checkpoint" ]; then
                name=$(basename "$checkpoint" .json)
                timestamp=$(stat -c %y "$checkpoint" 2>/dev/null | cut -d'.' -f1 || stat -f %Sm "$checkpoint" 2>/dev/null)
                echo "  - $name ($timestamp)"
            fi
        done
        echo ""
    fi
fi

# Record session start time
echo "$(date -Iseconds)" > "$PLUGIN_ROOT/data/.session_start"
