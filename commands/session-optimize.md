---
name: session-optimize
description: Analyze session context and provide optimization recommendations
allowed-tools: Bash, Read
---

# Session Optimization Analysis

Analyze the current session metrics and provide specific optimization recommendations.

## Execute

### 1. Get Analysis

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/metrics-tracker.py analyze
```

Display the output exactly as shown. The analysis includes:
- Health score with penalty breakdown
- Files accessed (for pruning consideration)
- Tool usage patterns
- Specific recommendations

### 2. Enhance Recommendations

Based on the metrics output, provide additional context-aware recommendations:

**If health score < 40 (Critical):**
- Strongly recommend immediate checkpoint: `/session-checkpoint before-optimize`
- Suggest aggressive compaction with focus on current task only

**If health score 40-60 (Warning):**
- Recommend checkpoint before optimization
- Suggest targeted compaction preserving key decisions

**If health score 60-80 (Moderate):**
- Optimization is optional
- Light compaction may help responsiveness

**If health score > 80 (Healthy):**
- No optimization needed
- Session is running efficiently

### 3. Generate Compact Command

Based on the analysis, construct a specific `/compact` command:

```
/compact Focus on: [current active task]. Preserve: [2-3 key items from metrics].
Prune: old file reads, resolved errors, superseded tool outputs.
```

### 4. Offer Actions

Present these options to the user:

1. **Safe approach**: `/session-checkpoint pre-optimize` then `/compact`
2. **Quick approach**: `/compact` with the generated focus phrase
3. **Manual review**: Show me the specific files/content to consider pruning

## When to Use

- Session health score drops below 60
- Responses feel slower or less coherent
- Working for 3+ hours continuously
- Before switching to a different area of the codebase
