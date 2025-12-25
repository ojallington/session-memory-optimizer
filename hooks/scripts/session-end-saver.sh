#!/bin/bash
# Session End Saver
# Records session to analytics and optionally creates auto-checkpoint

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(dirname "$(dirname "$(dirname "$0")")")}"
CHECKPOINT_DIR="$PLUGIN_ROOT/data/checkpoints"
SESSION_START_FILE="$PLUGIN_ROOT/data/.session_start"
METRICS_SCRIPT="$PLUGIN_ROOT/scripts/metrics-tracker.py"
ANALYTICS_SCRIPT="$PLUGIN_ROOT/scripts/analytics-manager.py"

# Create checkpoint directory if it doesn't exist
mkdir -p "$CHECKPOINT_DIR"

# Record session to analytics
if [ -f "$METRICS_SCRIPT" ] && [ -f "$ANALYTICS_SCRIPT" ]; then
    python3 "$METRICS_SCRIPT" export 2>/dev/null | python3 "$ANALYTICS_SCRIPT" record 2>/dev/null
fi

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

# Only auto-save checkpoint if session was longer than 30 minutes
if [ "$DURATION_MINS" -gt 30 ]; then
    AUTO_CHECKPOINT="$CHECKPOINT_DIR/auto-$(date +%Y%m%d-%H%M%S).json"

    # Get health score from metrics
    HEALTH_SCORE=$(python3 "$METRICS_SCRIPT" export 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('health_score', 100))" 2>/dev/null || echo 100)

    cat > "$AUTO_CHECKPOINT" << EOF
{
  "name": "auto-save",
  "timestamp": "$(date -Iseconds)",
  "type": "automatic",
  "duration_minutes": $DURATION_MINS,
  "health_score": $HEALTH_SCORE,
  "note": "Automatically saved at session end. Use /session-restore to view details."
}
EOF

    echo "Session Memory Optimizer: Auto-checkpoint saved ($DURATION_MINS min session, health: $HEALTH_SCORE)"
fi

# Clean up old auto-checkpoints (keep last 5)
if [ -d "$CHECKPOINT_DIR" ]; then
    ls -t "$CHECKPOINT_DIR"/auto-*.json 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null
fi

# Clean up session start file
rm -f "$SESSION_START_FILE" 2>/dev/null
