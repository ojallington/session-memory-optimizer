---
name: Context Management
description: This skill should be used when the user mentions "context is full", "running slow", "session performance", "memory optimization", "context pruning", "session health", "optimize session", "long session", or when noticing degraded response quality. Provides guidance for efficient context management during extended coding sessions.
version: 1.0.0
---

# Context Management for Long Sessions

## Overview

This skill provides techniques for maintaining session performance during extended coding work. Proactive context management prevents degradation before it impacts productivity.

## Warning Signs

Watch for these indicators of context pressure:

1. **Response Time Increasing**: Noticeable delays in responses
2. **Repetition**: Claude asking about things already discussed
3. **Context Confusion**: Mixing up details from different files/features
4. **Session Duration**: Working for 3+ hours continuously

## Quick Actions

### Check Session Health
```
/session-status
```
Shows current session health metrics and recommendations.

### Create Checkpoint Before Major Work
```
/session-checkpoint <name>
```
Saves current context state for later restoration.

### Get Optimization Recommendations
```
/session-optimize
```
Analyzes what can be pruned vs. what must be preserved.

### Restore After Restart
```
/session-restore <name>
```
Loads checkpoint context after starting fresh session.

## Proactive Techniques

### 1. Targeted File Reading

Instead of reading entire files, be specific:

**Less Efficient:**
- "Read the entire config file"
- "Show me all the routes"

**More Efficient:**
- "Read lines 50-100 of config.py where the database settings are"
- "Search for the /api/users route definition"

### 2. Progressive Summarization

After completing each subtask:
1. Summarize what was accomplished
2. Note key decisions made
3. List any patterns established
4. Move forward without carrying full implementation details

### 3. Checkpoint at Transitions

Create checkpoints before:
- Switching to a different feature/area
- Taking a break
- Major refactoring work
- End of work session

### 4. Prune Dead Ends

When abandoning an approach:
- Explicitly state "I'm abandoning this approach because..."
- This signals context can be compressed
- Summarize learnings to preserve

### 5. Use Compact Strategically

When running `/compact`, provide focus:
```
/compact Focus on: current authentication refactoring task
```

This guides compaction to preserve relevant context.

## What to Preserve vs. Prune

### Always Preserve
- Current active task and goals
- Recent architectural decisions
- User preferences and conventions
- Unresolved errors/blockers
- Active file states

### Safe to Compress
- Old tool outputs (git status, ls, etc.)
- File contents that were later edited
- Resolved error messages
- Exploration paths that were abandoned
- Verbose intermediate outputs

## Recovery Strategies

### Mild Degradation (2-4 hours)
1. Run `/session-optimize`
2. Create checkpoint
3. Run `/compact` with focus

### Moderate Degradation (4-6 hours)
1. Create checkpoint
2. Consider session restart
3. Restore checkpoint in new session

### Severe Degradation (6+ hours)
1. Create checkpoint immediately
2. Start fresh session
3. Restore checkpoint
4. Re-read only essential files

## Best Practices Summary

1. **Check health every 2 hours**: `/session-status`
2. **Checkpoint at milestones**: `/session-checkpoint <milestone>`
3. **Read files on demand**: Not preemptively
4. **Summarize completed work**: Before moving on
5. **Abandon explicitly**: State when dropping an approach
6. **Compact with focus**: Guide what to preserve
