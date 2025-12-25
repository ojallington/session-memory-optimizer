#!/usr/bin/env python3
"""
Analytics Manager for Session Memory Optimizer

Tracks historical session data for pattern analysis and recommendations.
Keeps last 30 days of session summaries.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path


def get_plugin_root():
    """Get the plugin root directory."""
    return os.environ.get(
        "CLAUDE_PLUGIN_ROOT",
        str(Path(__file__).parent.parent)
    )


def get_analytics_file():
    """Get path to analytics data file."""
    plugin_root = get_plugin_root()
    data_dir = Path(plugin_root) / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "analytics.json"


def load_analytics():
    """Load analytics data from file."""
    analytics_file = get_analytics_file()
    if analytics_file.exists():
        try:
            with open(analytics_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {
        "sessions": [],
        "aggregates": {
            "total_sessions": 0,
            "avg_duration_minutes": 0,
            "avg_health_score": 0,
            "avg_tool_calls": 0,
            "avg_files_read": 0
        },
        "last_updated": None
    }


def save_analytics(data):
    """Save analytics data to file."""
    analytics_file = get_analytics_file()
    data["last_updated"] = datetime.now().isoformat()
    with open(analytics_file, 'w') as f:
        json.dump(data, f, indent=2)


def prune_old_sessions(data, days=30):
    """Remove sessions older than specified days."""
    cutoff = datetime.now() - timedelta(days=days)
    data["sessions"] = [
        s for s in data["sessions"]
        if datetime.fromisoformat(s.get("ended_at", s.get("started_at", datetime.now().isoformat()))) > cutoff
    ]
    return data


def calculate_aggregates(data):
    """Calculate aggregate statistics from session history."""
    sessions = data["sessions"]
    if not sessions:
        data["aggregates"] = {
            "total_sessions": 0,
            "avg_duration_minutes": 0,
            "avg_health_score": 0,
            "avg_tool_calls": 0,
            "avg_files_read": 0
        }
        return data

    total = len(sessions)
    durations = [s.get("duration_minutes", 0) for s in sessions]
    health_scores = [s.get("final_health_score", 100) for s in sessions]
    tool_calls = [s.get("total_tool_calls", 0) for s in sessions]
    files_read = [s.get("files_read_count", 0) for s in sessions]

    data["aggregates"] = {
        "total_sessions": total,
        "avg_duration_minutes": round(sum(durations) / total, 1) if total else 0,
        "avg_health_score": round(sum(health_scores) / total, 1) if total else 0,
        "avg_tool_calls": round(sum(tool_calls) / total, 1) if total else 0,
        "avg_files_read": round(sum(files_read) / total, 1) if total else 0
    }
    return data


def record_session(session_data):
    """Record a completed session to analytics."""
    data = load_analytics()
    data = prune_old_sessions(data)

    session_summary = {
        "session_id": session_data.get("session_id", "unknown"),
        "started_at": session_data.get("started_at"),
        "ended_at": datetime.now().isoformat(),
        "duration_minutes": session_data.get("duration_minutes", 0),
        "final_health_score": session_data.get("health_score", 100),
        "total_tool_calls": session_data.get("metrics", {}).get("total_tool_calls", 0),
        "files_read_count": len(session_data.get("metrics", {}).get("files_read", [])),
        "checkpoints_created": session_data.get("metrics", {}).get("checkpoints_created", 0),
        "compactions": session_data.get("metrics", {}).get("compactions", 0)
    }

    data["sessions"].append(session_summary)
    data = calculate_aggregates(data)
    save_analytics(data)

    return session_summary


def get_trends():
    """Analyze trends in session data."""
    data = load_analytics()
    sessions = data["sessions"]

    if len(sessions) < 2:
        return None

    # Compare recent sessions (last 5) to older ones
    recent = sessions[-5:] if len(sessions) >= 5 else sessions[-len(sessions)//2:]
    older = sessions[:-5] if len(sessions) >= 5 else sessions[:len(sessions)//2]

    if not older:
        return None

    recent_avg_health = sum(s.get("final_health_score", 100) for s in recent) / len(recent)
    older_avg_health = sum(s.get("final_health_score", 100) for s in older) / len(older)

    recent_avg_duration = sum(s.get("duration_minutes", 0) for s in recent) / len(recent)
    older_avg_duration = sum(s.get("duration_minutes", 0) for s in older) / len(older)

    return {
        "health_trend": "improving" if recent_avg_health > older_avg_health else "declining",
        "health_change": round(recent_avg_health - older_avg_health, 1),
        "duration_trend": "longer" if recent_avg_duration > older_avg_duration else "shorter",
        "duration_change": round(recent_avg_duration - older_avg_duration, 1),
        "recent_avg_health": round(recent_avg_health, 1),
        "recent_avg_duration": round(recent_avg_duration, 1)
    }


def show_dashboard():
    """Display analytics dashboard."""
    data = load_analytics()
    agg = data["aggregates"]
    trends = get_trends()

    print("SESSION ANALYTICS DASHBOARD")
    print("=" * 40)
    print()

    print(f"Total Sessions Tracked: {agg['total_sessions']}")
    print(f"Data Retention: Last 30 days")
    print()

    print("AVERAGES")
    print("-" * 40)
    print(f"  Duration:     {agg['avg_duration_minutes']:.0f} minutes")
    print(f"  Health Score: {agg['avg_health_score']:.0f}/100")
    print(f"  Tool Calls:   {agg['avg_tool_calls']:.0f}")
    print(f"  Files Read:   {agg['avg_files_read']:.0f}")
    print()

    if trends:
        print("TRENDS (Recent vs Older)")
        print("-" * 40)
        health_arrow = "+" if trends["health_change"] > 0 else ""
        duration_arrow = "+" if trends["duration_change"] > 0 else ""
        print(f"  Health:   {trends['health_trend']} ({health_arrow}{trends['health_change']})")
        print(f"  Duration: {trends['duration_trend']} ({duration_arrow}{trends['duration_change']} min)")
        print()

    # Show recent sessions
    sessions = data["sessions"][-5:]
    if sessions:
        print("RECENT SESSIONS")
        print("-" * 40)
        for s in reversed(sessions):
            started = s.get("started_at", "")[:10] if s.get("started_at") else "unknown"
            health = s.get("final_health_score", "?")
            duration = s.get("duration_minutes", 0)
            print(f"  {started}: {duration:.0f}min, health={health}")

    print()
    if agg["avg_health_score"] < 60:
        print("RECOMMENDATION: Consider using /session-checkpoint")
        print("more frequently to preserve context.")


def show_export():
    """Export raw analytics data."""
    data = load_analytics()
    print(json.dumps(data, indent=2))


def main():
    if len(sys.argv) < 2:
        print("Usage: analytics-manager.py <command>")
        print("Commands: dashboard, record, export, trends")
        sys.exit(1)

    command = sys.argv[1]

    if command == "dashboard":
        show_dashboard()
    elif command == "record":
        # Read session data from stdin
        try:
            session_data = json.load(sys.stdin)
            summary = record_session(session_data)
            print(f"Session recorded: {summary['session_id']}")
            print(f"  Duration: {summary['duration_minutes']:.0f} minutes")
            print(f"  Health: {summary['final_health_score']}/100")
        except json.JSONDecodeError:
            print("Error: Invalid JSON input", file=sys.stderr)
            sys.exit(1)
    elif command == "export":
        show_export()
    elif command == "trends":
        trends = get_trends()
        if trends:
            print(json.dumps(trends, indent=2))
        else:
            print("Not enough data for trend analysis")
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
