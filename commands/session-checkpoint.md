---
name: session-checkpoint
description: Save current session context as a compressed checkpoint for later restoration
argument-hint: <checkpoint-name>
allowed-tools: Write, Bash, Read
---

# Create Session Checkpoint

Save the current session context with auto-captured metrics and a summary.

## Checkpoint Name

Use: `$ARGUMENTS` (if not provided, ask user for a name)

## Process

### 1. Get Current Metrics

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/metrics-tracker.py export
```

Parse the JSON to identify:
- Files recently read/written (from `metrics.files_read`, `metrics.files_written`)
- Session duration and health score
- Tool usage patterns

### 2. Create Summary

Based on metrics AND the current conversation context, create:

- **Current Task**: What is being actively worked on
- **Key Decisions**: Important decisions made this session (2-3 bullet points)
- **Active Files**: Top 5 most relevant files from metrics
- **Context Hints**: Critical context needed for restoration

### 3. Save Checkpoint

Write the checkpoint file:

```bash
mkdir -p "${CLAUDE_PLUGIN_ROOT}/data/checkpoints"
```

Then use Write tool to create `${CLAUDE_PLUGIN_ROOT}/data/checkpoints/$ARGUMENTS.json` with:

```json
{
  "name": "<checkpoint-name>",
  "timestamp": "<current ISO timestamp>",
  "auto_captured": true,
  "summary": "<2-3 sentence summary of session state>",
  "current_task": "<what is being worked on>",
  "decisions": ["decision 1", "decision 2"],
  "active_files": ["file1.py", "file2.md"],
  "context_hints": ["important context 1", "important context 2"],
  "metrics_snapshot": {
    "duration_minutes": <from metrics>,
    "health_score": <from metrics>,
    "files_read_count": <count>,
    "tool_calls": <count>
  }
}
```

### 4. Update Metrics Counter

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/metrics-tracker.py checkpoint
```

### 5. Confirm

Report to user:
- Checkpoint saved: `$ARGUMENTS`
- To restore: `/session-restore $ARGUMENTS`

## Examples

- `/session-checkpoint before-refactor` - Save before major changes
- `/session-checkpoint milestone-1` - Save at completion point
- `/session-checkpoint end-of-day` - Save before ending work
