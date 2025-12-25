---
name: session-checkpoint
description: Save current session context as a compressed checkpoint for later restoration
argument-hint: <checkpoint-name>
allowed-tools: Write, Bash, Read
---

# Create Session Checkpoint

Save a summarized snapshot of the current session context that can be restored later.

## Checkpoint Name

The checkpoint will be saved as: `$ARGUMENTS` (or "default" if not specified)

## Steps

1. **Summarize Current Context**
   Capture the essential elements of this session:

   **Active Work:**
   - What files are being actively worked on?
   - What is the current task/goal?
   - What stage of completion are we at?

   **Key Decisions:**
   - What architectural/design decisions were made?
   - What approaches were tried and rejected?
   - What patterns/conventions were established?

   **Important State:**
   - Any unresolved errors or blockers?
   - Pending TODOs or follow-up items?
   - Critical context that must not be lost?

2. **Create Checkpoint File**
   Save to: `${CLAUDE_PLUGIN_ROOT}/data/checkpoints/<name>.json`

   Format:
   ```json
   {
     "name": "<checkpoint-name>",
     "timestamp": "<ISO timestamp>",
     "summary": "<2-3 paragraph summary of session state>",
     "active_files": ["list", "of", "key", "files"],
     "current_task": "<description of current goal>",
     "decisions": ["key decision 1", "key decision 2"],
     "patterns": ["established pattern 1", "pattern 2"],
     "todos": ["pending item 1", "pending item 2"],
     "blockers": ["any unresolved issues"],
     "context_hints": ["important context to preserve"]
   }
   ```

3. **Confirm Checkpoint Created**
   Report:
   - Checkpoint name and location
   - Summary of what was captured
   - Command to restore: `/session-restore <name>`

## Usage Examples

- `/session-checkpoint before-refactor` - Save before major changes
- `/session-checkpoint end-of-day` - Save before ending work
- `/session-checkpoint feature-complete` - Save at milestone

## Notes

Checkpoints capture semantic meaning, not raw context. They're designed to help you (and Claude) quickly restore mental state after a session restart.
