#!/usr/bin/env python3
"""
Session Metrics Tracker - Core metrics collection and health calculation.

Usage:
    python3 metrics-tracker.py init          # Initialize new session
    python3 metrics-tracker.py record <tool> # Record tool usage (reads JSON from stdin)
    python3 metrics-tracker.py status        # Display health dashboard
    python3 metrics-tracker.py export        # Export metrics as JSON
    python3 metrics-tracker.py analyze       # Analyze for optimization recommendations
"""

import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Resolve plugin root
PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", Path(__file__).parent.parent))
DATA_DIR = PLUGIN_ROOT / "data"
METRICS_FILE = DATA_DIR / "metrics.json"
SESSION_START_FILE = DATA_DIR / ".session_start"


def get_default_metrics():
    """Return default metrics structure."""
    return {
        "session_id": str(uuid.uuid4())[:8],
        "started_at": datetime.now().isoformat(),
        "metrics": {
            "files_read": [],
            "files_written": [],
            "tool_invocations": {},
            "total_tool_calls": 0,
            "estimated_tokens_in": 0,
            "estimated_tokens_out": 0,
            "checkpoints_created": 0,
            "compactions_triggered": 0,
        },
        "last_activity": datetime.now().isoformat(),
        "health_score": 100,
    }


def load_metrics():
    """Load metrics from file or return defaults."""
    if METRICS_FILE.exists():
        try:
            with open(METRICS_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return get_default_metrics()


def save_metrics(metrics):
    """Save metrics to file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    metrics["last_activity"] = datetime.now().isoformat()
    metrics["health_score"] = calculate_health_score(metrics)
    with open(METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=2)


def get_duration_minutes(metrics):
    """Calculate session duration in minutes."""
    try:
        started = datetime.fromisoformat(metrics["started_at"])
        return (datetime.now() - started).total_seconds() / 60
    except (KeyError, ValueError):
        # Fallback to .session_start file
        if SESSION_START_FILE.exists():
            try:
                started = datetime.fromisoformat(SESSION_START_FILE.read_text().strip())
                return (datetime.now() - started).total_seconds() / 60
            except (ValueError, IOError):
                pass
    return 0


def calculate_health_score(metrics):
    """
    Calculate health score 0-100 based on session activity.

    Penalties:
    - Duration: -1 point per 12 minutes (max -30)
    - Tool calls: -1 point per 10 calls (max -25)
    - Files read: -1 point per 2 files (max -20)
    - Estimated tokens: -1 point per 4000 tokens (max -25)
    """
    score = 100
    m = metrics.get("metrics", {})

    # Duration penalty (max -30 points)
    duration = get_duration_minutes(metrics)
    duration_penalty = min(30, duration / 12)
    score -= duration_penalty

    # Tool calls penalty (max -25 points)
    tool_calls = m.get("total_tool_calls", 0)
    tool_penalty = min(25, tool_calls / 10)
    score -= tool_penalty

    # Files read penalty (max -20 points)
    files_count = len(m.get("files_read", []))
    files_penalty = min(20, files_count / 2)
    score -= files_penalty

    # Token estimate penalty (max -25 points)
    tokens = m.get("estimated_tokens_in", 0) + m.get("estimated_tokens_out", 0)
    token_penalty = min(25, tokens / 4000)
    score -= token_penalty

    return max(0, int(score))


def get_health_level(score):
    """Return health level string based on score."""
    if score >= 80:
        return "HEALTHY", "green"
    elif score >= 60:
        return "MODERATE", "yellow"
    elif score >= 40:
        return "ELEVATED", "orange"
    else:
        return "CRITICAL", "red"


def estimate_file_tokens(file_path):
    """Estimate tokens for a file (rough: chars / 4)."""
    try:
        size = Path(file_path).stat().st_size
        return size // 4  # Rough token estimate
    except (OSError, IOError):
        return 500  # Default estimate


# === Commands ===

def cmd_init():
    """Initialize a new session with fresh metrics."""
    metrics = get_default_metrics()
    save_metrics(metrics)

    # Also update .session_start
    SESSION_START_FILE.write_text(metrics["started_at"])

    print(f"Session initialized: {metrics['session_id']}")


def cmd_record(tool_name, stdin_data=None):
    """Record a tool invocation."""
    metrics = load_metrics()
    m = metrics["metrics"]

    # Increment tool count
    m["tool_invocations"][tool_name] = m["tool_invocations"].get(tool_name, 0) + 1
    m["total_tool_calls"] += 1

    # Parse stdin for additional details
    details = {}
    if stdin_data:
        try:
            details = json.loads(stdin_data)
        except json.JSONDecodeError:
            pass

    # Track file operations
    if tool_name == "Read":
        file_path = details.get("file_path", details.get("tool_input", {}).get("file_path", ""))
        if file_path and file_path not in m["files_read"]:
            m["files_read"].append(file_path)
            m["estimated_tokens_in"] += estimate_file_tokens(file_path)

    elif tool_name in ("Write", "Edit"):
        file_path = details.get("file_path", details.get("tool_input", {}).get("file_path", ""))
        if file_path and file_path not in m["files_written"]:
            m["files_written"].append(file_path)
            m["estimated_tokens_out"] += 500  # Estimate for write

    elif tool_name == "Bash":
        m["estimated_tokens_out"] += 200  # Bash output estimate

    save_metrics(metrics)


def cmd_status():
    """Display session health dashboard."""
    metrics = load_metrics()
    m = metrics.get("metrics", {})

    duration = get_duration_minutes(metrics)
    hours = int(duration // 60)
    mins = int(duration % 60)
    duration_str = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"

    score = metrics.get("health_score", calculate_health_score(metrics))
    level, _ = get_health_level(score)

    # Build progress bar
    bar_filled = int(score / 10)
    bar_empty = 10 - bar_filled
    bar = "=" * bar_filled + " " * bar_empty

    # Tool breakdown
    tool_counts = m.get("tool_invocations", {})
    top_tools = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:4]
    tool_str = ", ".join(f"{t}: {c}" for t, c in top_tools) if top_tools else "None"

    # Recommendations
    recs = []
    if score < 60 and m.get("checkpoints_created", 0) == 0:
        recs.append("[!] Create a checkpoint: /session-checkpoint milestone")
    if score < 50:
        recs.append("[!] Run /session-optimize before context grows further")
    if score < 30:
        recs.append("[!] CRITICAL: Consider restarting session after checkpoint")
    if not recs:
        recs.append("[ ] Session is healthy - continue working")

    # Calculate penalties for breakdown
    duration_penalty = min(30, int(duration / 12))
    tool_penalty = min(25, int(m.get("total_tool_calls", 0) / 10))
    files_penalty = min(20, int(len(m.get("files_read", [])) / 2))

    print(f"""SESSION HEALTH DASHBOARD
========================
Session ID:      {metrics.get('session_id', 'unknown')}
Duration:        {duration_str}
Health Score:    {score}/100 [{bar}] {level}

ACTIVITY METRICS
----------------
Files Read:      {len(m.get('files_read', []))}
Files Written:   {len(m.get('files_written', []))}
Tool Calls:      {m.get('total_tool_calls', 0)} ({tool_str})
Checkpoints:     {m.get('checkpoints_created', 0)}

HEALTH BREAKDOWN
----------------
Duration:        -{duration_penalty} pts ({duration_str})
Tool Activity:   -{tool_penalty} pts ({m.get('total_tool_calls', 0)} calls)
File Load:       -{files_penalty} pts ({len(m.get('files_read', []))} files)

RECOMMENDATIONS
---------------""")
    for rec in recs:
        print(rec)


def cmd_export():
    """Export current metrics as JSON."""
    metrics = load_metrics()
    print(json.dumps(metrics, indent=2))


def cmd_analyze():
    """Analyze session and provide optimization recommendations."""
    metrics = load_metrics()
    m = metrics.get("metrics", {})

    duration = get_duration_minutes(metrics)
    score = metrics.get("health_score", calculate_health_score(metrics))

    # Categorize files by recency (we can't actually know recency, so use order)
    files_read = m.get("files_read", [])
    files_written = m.get("files_written", [])

    # Recent files (last 5 read or any written)
    recent_files = set(files_read[-5:] + files_written)
    old_files = [f for f in files_read[:-5] if f not in recent_files]

    print(f"""SESSION OPTIMIZATION ANALYSIS
==============================
Health Score: {score}/100
Duration: {int(duration)}m
Total Tool Calls: {m.get('total_tool_calls', 0)}

CONTEXT CATEGORIZATION
----------------------
MUST PRESERVE (Recent/Active):""")

    for f in list(recent_files)[:5]:
        print(f"  - {Path(f).name}")

    print(f"""
SAFE TO PRUNE (Older Reads):""")
    for f in old_files[:5]:
        print(f"  - {Path(f).name}")
    if len(old_files) > 5:
        print(f"  ... and {len(old_files) - 5} more")

    print(f"""
RECOMMENDED ACTIONS
-------------------""")

    if score < 70 and m.get("checkpoints_created", 0) == 0:
        print("1. Create checkpoint first:")
        print("   /session-checkpoint before-optimize")
        print()

    if score < 60:
        # Build compact suggestion
        preserve_patterns = []
        for f in list(recent_files)[:3]:
            preserve_patterns.append(Path(f).name)

        print("2. Run focused compaction:")
        print(f"   /compact Preserve: {', '.join(preserve_patterns)}")

    if score < 40:
        print()
        print("3. CRITICAL: Consider session restart after saving checkpoint")


def cmd_increment_checkpoint():
    """Increment checkpoint counter."""
    metrics = load_metrics()
    metrics["metrics"]["checkpoints_created"] = metrics["metrics"].get("checkpoints_created", 0) + 1
    save_metrics(metrics)


def cmd_increment_compaction():
    """Increment compaction counter."""
    metrics = load_metrics()
    metrics["metrics"]["compactions_triggered"] = metrics["metrics"].get("compactions_triggered", 0) + 1
    save_metrics(metrics)


# === Main ===

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "init":
        cmd_init()
    elif command == "record":
        tool_name = sys.argv[2] if len(sys.argv) > 2 else "Unknown"
        stdin_data = sys.stdin.read() if not sys.stdin.isatty() else None
        cmd_record(tool_name, stdin_data)
    elif command == "status":
        cmd_status()
    elif command == "export":
        cmd_export()
    elif command == "analyze":
        cmd_analyze()
    elif command == "checkpoint":
        cmd_increment_checkpoint()
    elif command == "compaction":
        cmd_increment_compaction()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
