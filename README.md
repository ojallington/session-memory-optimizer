# Session Memory Optimizer

A Claude Code plugin that solves performance degradation in long coding sessions through real-time metrics tracking, automated health monitoring, and intelligent context optimization.

## The Problem

Claude Code experiences significant performance degradation after 2-5 hours of continuous work:
- Response times increase noticeably
- Context confusion (mixing up details from different files)
- Repetition (asking about things already discussed)
- Pro Max subscribers ($199/mo) getting worse results than expected

This is documented across GitHub issues #7769, #10881, #4511 with 15+ reactions each.

## The Solution

This plugin provides **real-time, automated** session management:

1. **Live Metrics Tracking** - PostToolUse hooks track every file read, write, and tool call
2. **Health Score Algorithm** - 0-100 score based on duration, activity, and estimated context usage
3. **Smart Checkpoints** - Auto-capture metrics + Claude summarizes context
4. **Optimization Guidance** - Data-driven recommendations for what to prune
5. **Analytics Dashboard** - Historical session patterns (30-day retention)
6. **PreCompact Hook** - Automatic optimization hints during compaction

## Installation

### From GitHub (Recommended)
```bash
claude plugins add github:ojallington/session-memory-optimizer
```

### From Claude Code Marketplace
```bash
# Search for the plugin
claude plugins search session-memory-optimizer

# Install by name
claude plugins add session-memory-optimizer
```

### Local Development
```bash
git clone https://github.com/ojallington/session-memory-optimizer.git
claude --plugin-dir /path/to/session-memory-optimizer
```

## Commands

### `/session-status`
Display real-time health dashboard with live metrics.

```
SESSION HEALTH DASHBOARD
========================
Session ID:      a1b2c3d4
Duration:        47m
Health Score:    72/100 [=======   ] MODERATE

ACTIVITY METRICS
----------------
Files Read:      12
Files Written:   3
Tool Calls:      45 (Bash: 18, Read: 12, Edit: 8, Grep: 7)
Checkpoints:     1

HEALTH BREAKDOWN
----------------
Duration:        -4 pts (47m)
Tool Activity:   -5 pts (45 calls)
File Load:       -6 pts (12 files)

RECOMMENDATIONS
---------------
[!] Consider /session-checkpoint to preserve current progress
[!] Use /session-optimize for pruning recommendations
```

### `/session-checkpoint <name>`
Save current session context with auto-captured metrics.

```bash
/session-checkpoint before-refactor
/session-checkpoint milestone-1
/session-checkpoint end-of-day
```

Auto-captures:
- Health score and all metrics at save time
- Files recently read/written
- Tool usage patterns
- Claude-generated summary of current task and key decisions

### `/session-restore [name]`
List available checkpoints or restore a specific one.

```bash
/session-restore              # List available checkpoints
/session-restore milestone-1  # Restore specific checkpoint
```

Displays checkpoint context and offers to read active files for full restoration.

### `/session-optimize`
Analyze current session and generate optimization recommendations.

```
SESSION OPTIMIZATION ANALYSIS
==============================
Health Score: 58/100
Duration: 2h 15m
Total Tool Calls: 89

CONTEXT CATEGORIZATION
----------------------
MUST PRESERVE (Recent/Active):
  - src/api/routes.py (5m ago)
  - src/models/user.py (12m ago)

SAFE TO PRUNE (Older Reads):
  - README.md (2h ago)
  - package.json (1h 45m ago)

RECOMMENDED ACTIONS
-------------------
[!] Create checkpoint: /session-checkpoint before-optimize
[!] Run: /compact Focus on API routes and user model...
```

## Health Score Algorithm

The health score (0-100) is calculated based on:

| Factor | Penalty | Max |
|--------|---------|-----|
| Duration | -1 per 12 minutes | -30 |
| Tool Calls | -1 per 10 calls | -25 |
| Files Read | -1 per 2 files | -20 |
| Est. Tokens | -1 per 4k tokens | -25 |

**Score Interpretation:**
- **80-100**: Healthy - continue working
- **60-79**: Moderate - consider checkpoint
- **40-59**: Warning - optimization recommended
- **0-39**: Critical - immediate action needed

## Automatic Features

### PostToolUse Tracking
Every Read, Write, Edit, Bash, Grep, and Glob call is tracked automatically to build accurate session metrics.

### PreCompact Hook
When Claude Code auto-compacts, this plugin injects guidance to:
- **Preserve**: Current task, recent decisions, active files, unresolved errors, pending TODOs
- **Compress**: Old tool outputs, resolved issues, abandoned exploration paths

### Session Start
- Initializes fresh metrics
- Notifies of available checkpoints from previous sessions

### Session End
- Records session to analytics (30-day history)
- Auto-saves checkpoint for sessions > 30 minutes

## Analytics

View historical session patterns:

```bash
python3 scripts/analytics-manager.py dashboard
```

```
SESSION ANALYTICS DASHBOARD
========================================
Total Sessions Tracked: 15
Data Retention: Last 30 days

AVERAGES
----------------------------------------
  Duration:     68 minutes
  Health Score: 71/100
  Tool Calls:   52
  Files Read:   14

TRENDS (Recent vs Older)
----------------------------------------
  Health:   improving (+5.2)
  Duration: longer (+12 min)
```

## File Structure

```
session-memory-optimizer/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── session-status.md
│   ├── session-checkpoint.md
│   ├── session-restore.md
│   └── session-optimize.md
├── hooks/
│   ├── hooks.json
│   └── scripts/
│       ├── post-tool-tracker.sh
│       ├── session-start-loader.sh
│       └── session-end-saver.sh
├── scripts/
│   ├── metrics-tracker.py
│   └── analytics-manager.py
├── skills/
│   └── context-management/
└── data/
    ├── metrics.json
    ├── analytics.json
    └── checkpoints/
```

## Best Practices

1. **Check health regularly**: `/session-status` every 1-2 hours
2. **Checkpoint at milestones**: Before major refactors or feature completion
3. **Optimize proactively**: Don't wait for degradation
4. **Trust the metrics**: The health score reflects real activity

## License

MIT License - See LICENSE file.

## Contributing

Issues and PRs welcome at: https://github.com/ojallington/session-memory-optimizer
