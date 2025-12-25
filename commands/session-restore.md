---
name: session-restore
description: Restore session context from a previously saved checkpoint
argument-hint: <checkpoint-name>
allowed-tools: Read, Bash
---

# Restore Session Checkpoint

Load a previously saved checkpoint to restore session context.

## Checkpoint Name

Restoring checkpoint: `$ARGUMENTS` (or "default" if not specified)

## Steps

1. **List Available Checkpoints** (if no name provided)
   Check `${CLAUDE_PLUGIN_ROOT}/data/checkpoints/` for available checkpoints.
   Display: name, timestamp, summary preview for each.

2. **Load Checkpoint File**
   Read from: `${CLAUDE_PLUGIN_ROOT}/data/checkpoints/<name>.json`

3. **Restore Context**
   Parse the checkpoint and internalize:

   **Immediate Context:**
   - Current task/goal we were working on
   - Active files that need attention
   - Where we left off

   **Background Context:**
   - Key decisions made (and why)
   - Patterns/conventions established
   - Approaches that were tried/rejected

   **Action Items:**
   - Pending TODOs to address
   - Any blockers that need resolution
   - Next steps to take

4. **Display Restoration Summary**
   ```
   CHECKPOINT RESTORED
   ===================
   Name:      <checkpoint-name>
   Saved:     <timestamp>

   Current Task: <what we were working on>

   Key Context:
   - <decision 1>
   - <decision 2>

   Active Files:
   - <file 1>
   - <file 2>

   Pending Items:
   - <todo 1>
   - <todo 2>

   Ready to continue from where you left off.
   ```

5. **Offer to Read Active Files**
   Suggest reading the active files to fully restore working context.

## Usage Examples

- `/session-restore` - List available checkpoints
- `/session-restore before-refactor` - Restore specific checkpoint
- `/session-restore end-of-day` - Resume previous day's work

## Notes

Restoration provides semantic context, not exact state. Use this after starting a fresh session to quickly get back up to speed.
