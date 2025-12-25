#!/bin/bash
# Pre-Compact Optimizer
# Provides optimization hints before compaction
# Note: The main optimization is done via the prompt hook in hooks.json

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(dirname "$(dirname "$(dirname "$0")")")}"

# Log compaction event for analytics (future use)
ANALYTICS_DIR="$PLUGIN_ROOT/data/analytics"
mkdir -p "$ANALYTICS_DIR"

echo "$(date -Iseconds): PreCompact triggered" >> "$ANALYTICS_DIR/compaction.log"

# Output nothing - let the prompt hook handle the guidance
exit 0
