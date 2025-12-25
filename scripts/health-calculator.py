#!/usr/bin/env python3
"""Session health calculator for session-memory-optimizer plugin."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

def get_plugin_root():
    """Get the plugin root directory."""
    return Path(os.environ.get('CLAUDE_PLUGIN_ROOT', Path(__file__).parent.parent))

def calculate_session_health():
    """Calculate current session health metrics."""
    plugin_root = get_plugin_root()
    session_start_file = plugin_root / 'data' / '.session_start'

    # Calculate duration
    duration_minutes = 0
    if session_start_file.exists():
        try:
            start_time = session_start_file.read_text().strip()
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            duration = datetime.now(start_dt.tzinfo) - start_dt
            duration_minutes = int(duration.total_seconds() / 60)
        except Exception:
            pass

    # Determine health level based on duration
    if duration_minutes < 120:
        health_level = "healthy"
        health_emoji = "🟢"
        recommendation = "Session is healthy. Continue working normally."
    elif duration_minutes < 240:
        health_level = "moderate"
        health_emoji = "🟡"
        recommendation = "Consider creating a checkpoint with /session-checkpoint"
    elif duration_minutes < 360:
        health_level = "elevated"
        health_emoji = "🟠"
        recommendation = "Run /session-optimize to analyze context. Consider compacting."
    else:
        health_level = "critical"
        health_emoji = "🔴"
        recommendation = "Strongly recommend: checkpoint, compact, or restart session."

    # Check for recent checkpoints
    checkpoint_dir = plugin_root / 'data' / 'checkpoints'
    last_checkpoint = None
    if checkpoint_dir.exists():
        checkpoints = list(checkpoint_dir.glob('*.json'))
        if checkpoints:
            latest = max(checkpoints, key=lambda x: x.stat().st_mtime)
            last_checkpoint = datetime.fromtimestamp(latest.stat().st_mtime).isoformat()

    return {
        "duration_minutes": duration_minutes,
        "duration_formatted": f"{duration_minutes // 60}h {duration_minutes % 60}m",
        "health_level": health_level,
        "health_emoji": health_emoji,
        "recommendation": recommendation,
        "last_checkpoint": last_checkpoint
    }

def format_health_dashboard(health: dict) -> str:
    """Format health metrics as a dashboard."""
    return f"""
SESSION HEALTH DASHBOARD
========================
Duration:        {health['duration_formatted']}
Health Status:   {health['health_emoji']} {health['health_level'].upper()}
Last Checkpoint: {health['last_checkpoint'] or 'None'}

Recommendation:  {health['recommendation']}

Commands:
  /session-checkpoint <name>  - Save current state
  /session-optimize           - Get pruning recommendations
  /session-restore            - List/restore checkpoints
"""

def main():
    """CLI interface for health calculator."""
    health = calculate_session_health()

    if len(sys.argv) > 1 and sys.argv[1] == '--json':
        print(json.dumps(health, indent=2))
    else:
        print(format_health_dashboard(health))

if __name__ == '__main__':
    main()
