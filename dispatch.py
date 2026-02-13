# -*- coding: utf-8 -*-
"""
Dispatch management module
Handles dispatch processes lifecycle and cleanup
"""

import os
import signal
import time as time_mod
import logging
from typing import Dict, Optional

logger = logging.getLogger("cccp")

# Global state
_dispatch_info: Dict[int, dict] = {}  # port -> {"date": date, "project": str, "created_at": timestamp, "process": process, "snapshot_key": str}
_dispatch_ports_by_date: Dict[str, int] = {}  # date -> port


def get_dispatch_port_for_date(date: str) -> Optional[int]:
    """Get the dispatch port for a specific date"""
    return _dispatch_ports_by_date.get(date)


def set_dispatch_port_for_date(date: str, port: int):
    """Set the dispatch port for a specific date"""
    _dispatch_ports_by_date[date] = port


def register_dispatch(date: str, port: int, process, project: str = ""):
    """Register a new dispatch process"""
    snapshot_key = f"{project}_{date}" if project else None
    _dispatch_info[port] = {
        "date": date,
        "project": project,
        "created_at": time_mod.time(),
        "process": process,
        "snapshot_key": snapshot_key
    }
    _dispatch_ports_by_date[date] = port
    logger.info(f"Registered dispatch on port {port} for date {date} (project: {project})")


def cleanup_stale_dispatches(max_age_seconds: float = 7200):
    """Clean up dispatch processes older than max_age_seconds (default: 2 hours)"""
    current_time = time_mod.time()
    stale_ports = []

    for port, info in _dispatch_info.items():
        age = current_time - info.get("created_at", 0)
        if age > max_age_seconds:
            stale_ports.append(port)

    for port in stale_ports:
        info = _dispatch_info.pop(port, None)
        if info:
            process = info.get("process")
            if process and process.poll() is None:
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    logger.info(f"Cleaned up stale dispatch on port {port}")
                except Exception as e:
                    logger.warning(f"Failed to kill stale dispatch on port {port}: {e}")

            # Delete linked snapshot (snapshots have same lifetime as dispatch)
            snapshot_key = info.get("snapshot_key")
            if snapshot_key:
                from snapshots import delete_log_snapshot, save_snapshots_to_disk
                if delete_log_snapshot(snapshot_key):
                    save_snapshots_to_disk()

            date = info.get("date")
            if date and _dispatch_ports_by_date.get(date) == port:
                del _dispatch_ports_by_date[date]


def get_all_dispatches():
    """Get all active dispatches"""
    dispatches = []
    for port, info in _dispatch_info.items():
        process = info.get("process")
        dispatches.append({
            "port": port,
            "date": info.get("date"),
            "project": info.get("project"),
            "created_at": info.get("created_at"),
            "alive": process.poll() is None if process else False
        })
    return dispatches
