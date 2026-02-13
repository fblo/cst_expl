# -*- coding: utf-8 -*-
"""
Snapshots management module
Handles log snapshots persistence and lifecycle
"""

import os
import json
import logging
from typing import Optional, Dict

logger = logging.getLogger("cccp")

# Import config
from config import SNAPSHOTS_FILE

# Global state
_log_snapshots: Dict[str, dict] = {}  # key: "PROJECT_YYYY-MM-DD" -> {...}


def load_snapshots_from_disk():
    """Load snapshots from JSON file at startup"""
    global _log_snapshots
    if os.path.exists(SNAPSHOTS_FILE):
        try:
            with open(SNAPSHOTS_FILE, 'r') as f:
                loaded = json.load(f)
            _log_snapshots.clear()
            _log_snapshots.update(loaded)
            logger.info(f"Loaded {len(_log_snapshots)} snapshots from disk")
        except Exception as e:
            logger.warning(f"Failed to load snapshots: {e}")


def save_snapshots_to_disk():
    """Save all snapshots to JSON file"""
    try:
        with open(SNAPSHOTS_FILE, 'w') as f:
            json.dump(_log_snapshots, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save snapshots: {e}")


def get_log_snapshot(project: str, date: str) -> Optional[dict]:
    """Get a log snapshot for a specific project and date"""
    key = f"{project}_{date}"
    return _log_snapshots.get(key)


def save_log_snapshot(project: str, date: str, port: int, directory: str, files_count: int):
    """Save a log snapshot"""
    key = f"{project}_{date}"
    import time as time_mod
    _log_snapshots[key] = {
        "project": project,
        "date": date,
        "port": port,
        "directory": directory,
        "created_at": time_mod.time(),
        "files_count": files_count
    }
    logger.info(f"Saved log snapshot: {key} (port={port}, files={files_count})")
    save_snapshots_to_disk()


def delete_log_snapshot(key: str) -> bool:
    """Delete a snapshot by key, returns True if deleted"""
    if key in _log_snapshots:
        del _log_snapshots[key]
        logger.info(f"Deleted log snapshot: {key}")
        return True
    return False


def cleanup_old_snapshots(max_age_days: float = 0.083):
    """Clean up snapshots older than max_age_days (default: 2 hours = 0.083 days)"""
    import time as time_mod
    cutoff_time = time_mod.time() - (max_age_days * 24 * 60 * 60)
    cleaned = 0

    for key, snapshot in list(_log_snapshots.items()):
        if snapshot.get("created_at", 0) < cutoff_time:
            del _log_snapshots[key]
            cleaned += 1

    if cleaned > 0:
        logger.info(f"Cleaned up {cleaned} old log snapshots")
        save_snapshots_to_disk()

    return cleaned


def get_all_snapshots():
    """Get all snapshots with age information"""
    import time as time_mod
    snapshots = []
    for key, snapshot in _log_snapshots.items():
        age = int(time_mod.time() - snapshot.get("created_at", 0))
        snapshots.append({
            "key": key,
            "project": snapshot.get("project"),
            "date": snapshot.get("date"),
            "port": snapshot.get("port"),
            "directory": snapshot.get("directory"),
            "files_count": snapshot.get("files_count"),
            "age_seconds": age,
            "created_at": snapshot.get("created_at")
        })
    snapshots.sort(key=lambda x: x.get("date", ""), reverse=True)
    return snapshots
