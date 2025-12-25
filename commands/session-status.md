---
name: session-status
description: Display session health metrics and optimization recommendations
allowed-tools: Bash
---

# Session Health Status

Display the current session health dashboard with real metrics.

## Execute

Run the metrics tracker to get the current session status:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/metrics-tracker.py status
```

Display the output exactly as shown. The dashboard includes:
- Session ID and duration
- Health score (0-100) with visual indicator
- Activity breakdown (files read, tool calls, checkpoints)
- Health penalty breakdown
- Specific recommendations based on current state

If the health score is below 60, emphasize the recommendations to the user.
