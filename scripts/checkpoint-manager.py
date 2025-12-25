#!/usr/bin/env python3
"""Checkpoint manager for session-memory-optimizer plugin."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

def get_checkpoint_dir():
    """Get the checkpoints directory path."""
    plugin_root = os.environ.get('CLAUDE_PLUGIN_ROOT', Path(__file__).parent.parent)
    return Path(plugin_root) / 'data' / 'checkpoints'

def list_checkpoints():
    """List all available checkpoints."""
    checkpoint_dir = get_checkpoint_dir()
    if not checkpoint_dir.exists():
        print("No checkpoints found.")
        return []

    checkpoints = []
    for f in sorted(checkpoint_dir.glob('*.json'), key=lambda x: x.stat().st_mtime, reverse=True):
        try:
            with open(f) as fp:
                data = json.load(fp)
                checkpoints.append({
                    'name': f.stem,
                    'timestamp': data.get('timestamp', 'unknown'),
                    'summary': data.get('summary', data.get('note', ''))[:100],
                    'path': str(f)
                })
        except Exception as e:
            checkpoints.append({
                'name': f.stem,
                'timestamp': 'error',
                'summary': f'Error reading: {e}',
                'path': str(f)
            })

    return checkpoints

def save_checkpoint(name: str, data: dict):
    """Save a checkpoint."""
    checkpoint_dir = get_checkpoint_dir()
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    data['name'] = name
    data['timestamp'] = datetime.now().isoformat()

    checkpoint_path = checkpoint_dir / f"{name}.json"
    with open(checkpoint_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Checkpoint saved: {checkpoint_path}")
    return str(checkpoint_path)

def load_checkpoint(name: str):
    """Load a checkpoint by name."""
    checkpoint_dir = get_checkpoint_dir()
    checkpoint_path = checkpoint_dir / f"{name}.json"

    if not checkpoint_path.exists():
        print(f"Checkpoint not found: {name}")
        return None

    with open(checkpoint_path) as f:
        return json.load(f)

def delete_checkpoint(name: str):
    """Delete a checkpoint by name."""
    checkpoint_dir = get_checkpoint_dir()
    checkpoint_path = checkpoint_dir / f"{name}.json"

    if checkpoint_path.exists():
        checkpoint_path.unlink()
        print(f"Checkpoint deleted: {name}")
        return True
    else:
        print(f"Checkpoint not found: {name}")
        return False

def main():
    """CLI interface for checkpoint manager."""
    if len(sys.argv) < 2:
        print("Usage: checkpoint-manager.py <action> [args]")
        print("Actions: list, save, load, delete")
        sys.exit(1)

    action = sys.argv[1].lower()

    if action == 'list':
        checkpoints = list_checkpoints()
        for cp in checkpoints:
            print(f"  {cp['name']}: {cp['timestamp']}")
            if cp['summary']:
                print(f"    {cp['summary'][:80]}...")

    elif action == 'save':
        if len(sys.argv) < 3:
            print("Usage: checkpoint-manager.py save <name>")
            sys.exit(1)
        name = sys.argv[2]
        # Read checkpoint data from stdin
        data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
        save_checkpoint(name, data)

    elif action == 'load':
        if len(sys.argv) < 3:
            print("Usage: checkpoint-manager.py load <name>")
            sys.exit(1)
        name = sys.argv[2]
        checkpoint = load_checkpoint(name)
        if checkpoint:
            print(json.dumps(checkpoint, indent=2))

    elif action == 'delete':
        if len(sys.argv) < 3:
            print("Usage: checkpoint-manager.py delete <name>")
            sys.exit(1)
        name = sys.argv[2]
        delete_checkpoint(name)

    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == '__main__':
    main()
