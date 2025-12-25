---
name: session-optimize
description: Analyze session context and provide optimization recommendations
allowed-tools: Read, Bash
---

# Session Optimization Analysis

Analyze the current session to identify what context can be pruned vs. what must be preserved.

## Steps

1. **Analyze Context Composition**
   Review what types of content are consuming context:
   - File reads (which files, how large, still relevant?)
   - Tool outputs (resolved errors, old build outputs?)
   - Exploration paths (dead ends, superseded approaches?)
   - Conversation history (key decisions vs. routine exchanges?)

2. **Identify Safe-to-Prune Content**

   **High Confidence Prune:**
   - Old tool outputs no longer relevant (e.g., old `git status` results)
   - File contents that were read then edited (superseded by newer versions)
   - Exploratory code paths that were explicitly abandoned
   - Verbose error messages that have been resolved
   - Repeated similar queries/responses

   **Medium Confidence Prune:**
   - Files read for reference but not actively being modified
   - Background context gathered early in session
   - Detailed implementation discussions for completed features

3. **Identify Must-Preserve Content**

   **Critical - Never Prune:**
   - Current active task and immediate goals
   - Recent architectural/design decisions and their rationale
   - Active file states (files being edited now)
   - User preferences established this session
   - Unresolved errors or blockers
   - Pending TODOs and action items

   **Important - Preserve Summary:**
   - Overall project context
   - Key patterns/conventions established
   - Major milestones reached

4. **Generate Optimization Recommendations**

   ```
   SESSION OPTIMIZATION ANALYSIS
   =============================

   SAFE TO PRUNE:
   - [specific content type]: [reason it's safe]
   - [specific content type]: [reason it's safe]

   MUST PRESERVE:
   - [specific content]: [why it's critical]
   - [specific content]: [why it's critical]

   ESTIMATED IMPACT:
   Context reduction: ~[X]%

   RECOMMENDED ACTION:
   Run: /compact [focus phrase based on must-preserve items]

   Or create checkpoint first: /session-checkpoint before-optimize
   ```

5. **Provide Compact Command**
   Generate a specific `/compact` invocation with a focus phrase that emphasizes preserving critical context.

## Usage

Run this command when:
- Session feels slow or responses are degrading
- You've been working for 3+ hours continuously
- Before a major context switch (new feature, different area of code)

## Notes

This analysis helps you make informed decisions about what to preserve during compaction. Always create a checkpoint before aggressive optimization.
