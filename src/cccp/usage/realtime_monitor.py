#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's mcanal libraries.
# Interact-IV.com (c) 2013-2016
#
# Contact: softeam@interact-iv.com
# Authors:
#    - JTAG <jtag@interact-iv.com>

"""CCCP Real-time Monitoring Module."""

import json
import os
import time
import threading
from datetime import datetime
from flask import Flask, Response
from cccp.usage.sessions_manager import CccpSessionsManager


class CccpRealtimeMonitor(object):
    """Real-time monitoring for CCCP with Server-Sent Events."""

    def __init__(self, data_file="/tmp/cccp_monitoring.json", update_interval=10):
        self.data_file = data_file
        self.update_interval = update_interval
        self.sessions_manager = CccpSessionsManager()
        self.monitoring_active = False
        self.monitoring_thread = None
        self.last_connected = False
        self.call_history = []

        # Initialize default data structure
        self.data = {
            "ip": self.sessions_manager.host,
            "connected": False,
            "last_update": None,
            "users": [],
            "queues": [],
            "calls": {"incoming": [], "outgoing": [], "active": 0, "history": []},
            "statistics": {
                "users": {
                    "total_users": 0,
                    "supervisors": 0,
                    "agents": 0,
                    "logged_in": 0,
                },
                "queues": {
                    "total_queues": 0,
                    "total_logged": 0,
                    "total_working": 0,
                    "total_waiting": 0,
                },
                "calls": {
                    "active_calls": 0,
                    "incoming_active": 0,
                    "outgoing_active": 0,
                    "completed_today": 0,
                },
            },
            "errors": [],
        }

    def read_shared_data(self):
        """Read data from shared file."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            self._log_error(f"Error reading shared data: {e}")
        return self.data

    def write_shared_data(self):
        """Write data to shared file."""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            self._log_error(f"Error writing shared data: {e}")

    def _log_error(self, message):
        """Log error message."""
        error = {"timestamp": datetime.now().isoformat(), "message": str(message)}
        self.data["errors"].insert(0, error)
        if len(self.data["errors"]) > 50:
            self.data["errors"] = self.data["errors"][:50]

    def monitoring_loop(self):
        """Main monitoring loop."""
        cycle = 0

        while self.monitoring_active:
            cycle += 1
            start_time = time.time()

            try:
                # Fetch data from CCCP
                cccp_data = self.sessions_manager.fetch_cccp_data()

                # Process data
                summary = self.sessions_manager.get_monitoring_summary(cccp_data)

                # Update internal data
                self.data.update(summary)

                # Preserve call history across updates
                new_history = summary.get("calls", {}).get("history", [])
                if new_history:
                    self.call_history = new_history
                    self.data["calls"]["history"] = self.call_history

                # Update last update time
                self.data["last_update"] = datetime.now().isoformat()

                # Log connection status changes
                connected = self.data.get("connected", False)
                if connected != self.last_connected:
                    self.last_connected = connected
                    print(
                        f"[{datetime.now().strftime('%H:%M:%S')}] "
                        f"{'Connected' if connected else 'Disconnected'} to dispatch"
                    )
                    print(
                        f"  Users: {len(self.data['users'])}, "
                        f"Queues: {len(self.data['queues'])}, "
                        f"Active calls: {self.data['calls']['active']}"
                    )

                # Write to shared file
                self.write_shared_data()

            except Exception as e:
                self._log_error(f"Monitoring cycle error: {e}")
                self.data["connected"] = False
                self.data["last_update"] = datetime.now().isoformat()
                self.write_shared_data()

            # Calculate sleep time to maintain interval
            elapsed = time.time() - start_time
            sleep_time = max(0, self.update_interval - elapsed)
            time.sleep(sleep_time)

    def start_monitoring(self):
        """Start monitoring in background thread."""
        if self.monitoring_active:
            return False, "Monitoring already active"

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self.monitoring_loop, daemon=True
        )
        self.monitoring_thread.start()

        return True, "Monitoring started"

    def stop_monitoring(self):
        """Stop monitoring."""
        if not self.monitoring_active:
            return False, "Monitoring not active"

        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)

        return True, "Monitoring stopped"

    def get_current_data(self):
        """Get current monitoring data."""
        return self.data

    def generate_sse_data(self):
        """Generate data for Server-Sent Events."""
        data = self.read_shared_data()
        yield f"data: {json.dumps(data)}\n\n"

    def create_sse_response(self):
        """Create Flask SSE response."""

        def generate():
            while True:
                try:
                    data = self.read_shared_data()
                    yield f"data: {json.dumps(data)}\n\n"
                    time.sleep(1)
                except Exception as e:
                    error_data = {
                        "timestamp": datetime.now().isoformat(),
                        "error": str(e),
                        "type": "sse_error",
                    }
                    yield f"data: {json.dumps(error_data)}\n\n"
                    time.sleep(5)

        return Response(generate(), mimetype="text/event-stream")

    def get_user_summary(self):
        """Get user summary statistics."""
        users = self.data.get("users", [])
        return {
            "total": len(users),
            "logged_in": len([u for u in users if u.get("logged_in")]),
            "supervisors": len([u for u in users if u.get("type") == "supervisor"]),
            "agents": len([u for u in users if u.get("type") == "agent"]),
            "states": self._count_user_states(users),
        }

    def _count_user_states(self, users):
        """Count users by state."""
        states = {}
        for user in users:
            state = user.get("state", "unknown")
            states[state] = states.get(state, 0) + 1
        return states

    def get_queue_summary(self):
        """Get queue summary statistics."""
        queues = self.data.get("queues", [])
        return {
            "total": len(queues),
            "total_logged": sum(q.get("logged", 0) for q in queues),
            "total_working": sum(q.get("working", 0) for q in queues),
            "total_waiting": sum(q.get("waiting", 0) for q in queues),
            "queues": [
                {
                    "name": q.get("name"),
                    "display_name": q.get("display_name"),
                    "logged": q.get("logged", 0),
                    "working": q.get("working", 0),
                    "waiting": q.get("waiting", 0),
                }
                for q in queues
            ],
        }

    def get_call_summary(self):
        """Get call summary statistics."""
        calls = self.data.get("calls", {})
        return {
            "active": calls.get("active", 0),
            "incoming_active": len(calls.get("incoming", [])),
            "outgoing_active": len(calls.get("outgoing", [])),
            "recent_calls": calls.get("history", [])[:20],
        }

    def get_status_overview(self):
        """Get overall status overview."""
        return {
            "connected": self.data.get("connected", False),
            "ip": self.data.get("ip"),
            "last_update": self.data.get("last_update"),
            "uptime": self._get_uptime(),
            "errors_count": len(self.data.get("errors", [])),
            "monitoring_active": self.monitoring_active,
        }

    def _get_uptime(self):
        """Get monitoring uptime."""
        if not hasattr(self, "start_time"):
            self.start_time = datetime.now()
        uptime = datetime.now() - self.start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"

    def search_users(self, query):
        """Search users by login, name, or state."""
        users = self.data.get("users", [])
        query = query.lower()
        results = []

        for user in users:
            if (
                query in user.get("login", "").lower()
                or query in user.get("name", "").lower()
                or query in user.get("state", "").lower()
                or query in user.get("profile", "").lower()
            ):
                results.append(user)

        return results

    def get_user_details(self, user_id):
        """Get detailed information for a specific user."""
        users = self.data.get("users", [])
        for user in users:
            if user.get("id") == user_id or user.get("login") == user_id:
                return user
        return None

    def get_queue_details(self, queue_name):
        """Get detailed information for a specific queue."""
        queues = self.data.get("queues", [])
        for queue in queues:
            if (
                queue.get("name") == queue_name
                or queue.get("display_name") == queue_name
            ):
                return queue
        return None

    def export_current_state(self):
        """Export current monitoring state to JSON."""
        return {
            "export_timestamp": datetime.now().isoformat(),
            "monitoring_data": self.data,
            "summary": {
                "users": self.get_user_summary(),
                "queues": self.get_queue_summary(),
                "calls": self.get_call_summary(),
                "status": self.get_status_overview(),
            },
        }

    def force_refresh(self):
        """Force immediate data refresh."""
        try:
            cccp_data = self.sessions_manager.fetch_cccp_data()
            summary = self.sessions_manager.get_monitoring_summary(cccp_data)
            self.data.update(summary)
            self.data["last_update"] = datetime.now().isoformat()
            self.write_shared_data()
            return True, "Data refreshed successfully"
        except Exception as e:
            self._log_error(f"Force refresh error: {e}")
            return False, str(e)

    def clear_errors(self):
        """Clear error logs."""
        self.data["errors"] = []
        self.write_shared_data()
        return True, "Errors cleared"
