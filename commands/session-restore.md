---
name: session-restore
description: Restore session context from a previously saved checkpoint
argument-hint: [checkpoint-name]
allowed-tools: Read, Bash
---

# Restore Session Checkpoint

Load a previously saved checkpoint to restore session context.

## Process

### 1. List or Load Checkpoint

**If no argument provided**, list available checkpoints:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py list
```

Then ask user: "Which checkpoint would you like to restore?"

**If argument provided** (`$ARGUMENTS`), load the checkpoint:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py load "$ARGUMENTS"
```

Or directly read: `${CLAUDE_PLUGIN_ROOT}/data/checkpoints/$ARGUMENTS.json`

### 2. Parse and Display

Parse the checkpoint JSON and display:

```
CHECKPOINT RESTORED
===================
Name:       <name>
Saved:      <timestamp>
Health:     <health_score>/100 at save time

CONTEXT SUMMARY
---------------
<summary field>

CURRENT TASK
------------
<current_task field>

KEY DECISIONS
-------------
- <decision 1>
- <decision 2>

ACTIVE FILES
------------
- <file 1>
- <file 2>
```

### 3. Internalize Context

State your understanding:
"Based on this checkpoint, I understand that:
- We were working on: [current_task]
- Key decisions made: [list decisions]
- The context hints suggest: [context_hints]"

### 4. Offer File Loading

If the checkpoint contains `active_files`, offer:
"Would you like me to read any of these active files to restore full context?"

List the files for user selection.

## Examples

- `/session-restore` - List available checkpoints
- `/session-restore milestone-1` - Restore specific checkpoint
- `/session-restore before-refactor` - Resume from save point
