---
name: session-status
description: Display session health metrics and optimization recommendations
allowed-tools: Bash, Read
---

# Session Health Status

Analyze the current session health and provide optimization recommendations.

## Steps

1. **Calculate Session Duration**
   Check how long the current session has been active by examining recent activity patterns.

2. **Estimate Context Usage**
   Analyze the session's context consumption:
   - Count of files read this session
   - Number of tool invocations
   - Complexity of operations performed

3. **Assess Health Level**
   Based on session duration and activity:
   - **Healthy** (0-2 hours, low activity): Continue working normally
   - **Moderate** (2-4 hours, medium activity): Consider creating a checkpoint
   - **Elevated** (4-6 hours, high activity): Recommend running /session-optimize
   - **Critical** (6+ hours, heavy activity): Strongly recommend optimization or restart

4. **Display Health Dashboard**
   Present a clear summary:
   ```
   SESSION HEALTH DASHBOARD
   ========================
   Duration:     [estimated]
   Activity:     [low/medium/high/very high]
   Health:       [Healthy/Moderate/Elevated/Critical]
   Last Checkpoint: [timestamp or "None"]

   Recommendation: [specific action to take]
   ```

5. **Provide Actionable Recommendations**
   Based on health level, suggest:
   - `/session-checkpoint <name>` - Save current state
   - `/session-optimize` - Get pruning recommendations
   - `/compact` - Run compaction with focus guidance
   - Restart session - For critical health levels

## Notes

This command helps you proactively manage long coding sessions before performance degrades.
