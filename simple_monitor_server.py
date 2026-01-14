#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's mcanal libraries.
# Interact-IV.com (c) 2013-2016
#
# Contact: softeam@interact-iv.com
# Authors:
#    - JTAG <jtag@interact-iv.com>

"""Simple Web Server for CCCP Monitoring with Mock Data."""

import sys
import os
import json
import time
from flask import Flask, Response
from mock_data_generator import CccpDataGenerator


class SimpleWebServer(object):
    """Simple web server for CCCP monitoring."""

    def __init__(self, data_file="/tmp/cccp_mock_monitoring.json", port=6000):
        self.data_file = data_file
        self.port = port
        self.data_generator = CccpDataGenerator()

        # Initialize with mock data
        self.load_mock_data()

        # Create Flask app
        self.app = Flask(__name__)
        self._setup_routes()

    def load_mock_data(self):
        """Load mock data or generate if not exists."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    self.data = json.load(f)
                print(f"✅ Loaded mock data from {self.data_file}")
                return
            except Exception as e:
                print(f"❌ Error loading mock data: {e}")
        else:
            print("🧪 No mock data found, generating...")
            self.data = self.data_generator.generate_mock_data()
            self.save_mock_data()

    def save_mock_data(self):
        """Save mock data to file."""
        try:
            with open(self.data_file, "w") as f:
                json.dump(self.data, f, indent=2)
            print(f"💾 Saved mock data to {self.data_file}")
        except Exception as e:
            print(f"❌ Error saving mock data: {e}")

    def _setup_routes(self):
        """Setup Flask routes."""

        @self.app.route("/")
        def index():
            """Main dashboard page."""
            template = """
<!DOCTYPE html>
<html>
<head>
    <title>🚀 CCCP Monitor - {{ host }}</title>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="30">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #ffffff; }
        .header { background: #333; color: #fff; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
        .header h1 { margin: 0; font-size: 24px; }
        .header p { margin: 5px 0 0; opacity: 0.8; }
        .status { display: flex; justify-content: space-between; margin-bottom: 20px; }
        .card { background: #2d2d2d; padding: 20px; border-radius: 8px; border: 1px solid #444; }
        .card h3 { margin: 0 0 15px 0; color: #4CAF50; }
        .stat { font-size: 18px; margin: 5px 0; }
        .stat-value { font-weight: bold; color: #fff; }
        .refresh { text-align: center; margin: 20px 0; }
        .highlight { color: #4CAF50; }
        .badge { background: #444; color: #fff; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin-left: 10px; }
        .legend { margin-top: 15px; }
        .legend-item { display: inline-block; margin: 5px; background: #333; padding: 5px 10px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 CCCP Monitor</h1>
        <p>Server: <span class="highlight">{{ host }}</span> | Mock Mode | Auto-refresh every 30s</p>
        <div class="status">
            <span>📊 Status:</span>
            <span class="stat-value">{{ connected_status }}</span>
            <span class="badge">{{ users_count }} Users</span>
            <span class="badge">{{ queues_count }} Queues</span>
            <span class="badge">{{ calls_active }} Calls</span>
        </div>
    </div>
    
    <div class="card">
        <h3>👥 Users</h3>
        <div class="stat">Total: <span class="stat-value">{{ total_users }}</span></div>
        <div class="stat">Logged In: <span class="stat-value">{{ logged_in }}</span></div>
        <div class="stat">Supervisors: <span class="stat-value">{{ supervisors }}</span></div>
        <div class="stat">Agents: <span class="stat-value">{{ agents }}</span></div>
    </div>
    
    <div class="card">
        <h3>📞 Calls</h3>
        <div class="stat">Active: <span class="stat-value">{{ calls_active }}</span></div>
        <div class="stat">Incoming: <span class="stat-value">{{ incoming_calls }}</span></div>
        <div class="stat">Outgoing: <span class="stat-value">{{ outgoing_calls }}</span></div>
    </div>
    
    <div class="card">
        <h3>📋 Queues</h3>
        <div class="stat">Total: <span class="stat-value">{{ total_queues }}</span></div>
        <div class="stat">Total Waiting: <span class="stat-value">{{ total_waiting }}</span></div>
    </div>
    
    <div class="legend">
        <div class="legend-item">📊 <span class="highlight">MOCK DATA</span></div>
        <div class="legend-item">🔄 Auto-refresh enabled</div>
        <div class="legend-item">🔧 No real CCCP connection</div>
    </div>
    
    <div class="refresh">
        <p>⏱ Page will refresh in <span id="countdown">30</span> seconds...</p>
    </div>
    
    <script>
        let countdown = 30;
        
        function updateCountdown() {
            if (countdown > 0) {
                document.getElementById('countdown').innerText = countdown;
                countdown--;
            } else {
                document.getElementById('countdown').innerText = 'Refreshing...';
            }
        }
        
        function refreshData() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    document.querySelectorAll('.stat-value').forEach(el => {
                        el.textContent = '0';
                    });
                    
                    // Update counters
                    document.querySelector('[data-stat="total_users"]').textContent = data.statistics.users.total_users;
                    document.querySelector('[data-stat="logged_in"]').textContent = data.statistics.users.logged_in;
                    document.querySelector('[data-stat="supervisors"]').textContent = data.statistics.users.supervisors;
                    document.querySelector('[data-stat="agents"]').textContent = data.statistics.users.agents;
                    document.querySelector('[data-stat="calls_active"]').textContent = data.statistics.calls.active_calls;
                    document.querySelector('[data-stat="incoming_calls"]').textContent = data.statistics.calls.incoming_active;
                    document.querySelector('[data-stat="outgoing_calls"]').textContent = data.statistics.calls.outgoing_active;
                    document.querySelector('[data-stat="total_queues"]').textContent = data.statistics.queues.total_queues;
                    document.querySelector('[data-stat="total_waiting"]').textContent = data.statistics.queues.total_waiting;
                })
                .catch(error => console.error('Error refreshing data:', error));
            
            countdown = 30;  // Reset countdown
        }
        
        // Initial countdown update
        updateCountdown();
        setInterval(updateCountdown, 1000);
        
        // Refresh data every 5 seconds
        setInterval(refreshData, 5000);
    </script>
</body>
</html>
            """

            data = self.get_dashboard_data()
            return (
                template.replace("{{ host }}", self.data["ip"])
                .replace("{{ connected_status }}", self.data["connected"])
                .replace("{{ total_users }}", str(len(self.data["users"])))
                .replace(
                    "{{ logged_in }}",
                    str(len([u for u in self.data["users"] if u.get("logged_in")])),
                )
                .replace(
                    "{{ supervisors }}",
                    str(
                        len(
                            [
                                u
                                for u in self.data["users"]
                                if u.get("type") == "supervisor"
                            ]
                        )
                    ),
                )
                .replace(
                    "{{ agents }}",
                    str(
                        len([u for u in self.data["users"] if u.get("type") == "agent"])
                    ),
                )
                .replace(
                    "{{ calls_active }}",
                    str(self.data["statistics"]["calls"]["active_calls"]),
                )
                .replace(
                    "{{ incoming_calls }}",
                    str(self.data["statistics"]["calls"]["incoming_active"]),
                )
                .replace(
                    "{{ outgoing_calls }}",
                    str(self.data["statistics"]["calls"]["outgoing_active"]),
                )
                .replace("{{ total_queues }}", str(len(self.data["queues"])))
                .replace(
                    "{{ total_waiting }}",
                    str(self.data["statistics"]["queues"]["total_waiting"]),
                )
            )

        @self.app.route("/api/data")
        def api_data():
            """Get current monitoring data."""
            return self.get_json_response()

        @self.app.route("/api/users")
        def api_users():
            """Get users data."""
            return self.get_json_response(users_only=True)

        @self.app.route("/api/queues")
        def api_queues():
            """Get queues data."""
            return self.get_json_response(queues_only=True)

        @self.app.route("/api/calls")
        def api_calls():
            """Get calls data."""
            return self.get_json_response(calls_only=True)

        @self.app.route("/api/refresh")
        def api_refresh():
            """Refresh mock data."""
            self.data = self.data_generator.generate_mock_data()
            self.save_mock_data()
            return self.get_json_response()

        @self.app.route("/api/generate")
        def api_generate():
            """Generate new mock data."""
            self.data = self.data_generator.generate_mock_data()
            self.save_mock_data()
            return self.get_json_response()

    def get_dashboard_data(self, users_only=False, queues_only=False, calls_only=False):
        """Get formatted dashboard data."""
        stats = self.calculate_statistics()

        return {
            "ip": self.data.get("ip", "10.199.30.67"),
            "connected": self.data.get("connected", False),
            "last_update": self.data.get("last_update"),
            "users": self.data.get("users", []) if not users_only else [],
            "queues": self.data.get("queues", []) if not queues_only else [],
            "calls": self.data.get("calls", {}) if not calls_only else {},
            "statistics": stats,
        }

    def calculate_statistics(self):
        """Calculate statistics from current data."""
        users = self.data.get("users", [])
        calls = self.data.get("calls", {})
        queues = self.data.get("queues", [])

        logged_in = len([u for u in users if u.get("logged_in")])
        supervisors = len([u for u in users if u.get("type") == "supervisor"])
        agents = len([u for u in users if u.get("type") == "agent"])

        total_waiting = sum(q.get("waiting", 0) for q in queues)

        return {
            "users": {
                "total_users": len(users),
                "logged_in": logged_in,
                "supervisors": supervisors,
                "agents": agents,
            },
            "calls": {
                "active_calls": calls.get("active", 0),
                "incoming_active": len(calls.get("incoming", [])),
                "outgoing_active": len(calls.get("outgoing", [])),
                "completed_today": len(calls.get("history", [])),
            },
            "queues": {
                "total_queues": len(queues),
                "total_waiting": total_waiting,
                "average_waiting": total_waiting / len(queues)
                if len(queues) > 0
                else 0,
            },
        }

    def get_json_response(self, users_only=False, queues_only=False, calls_only=False):
        """Get JSON response with current data."""
        data = self.get_dashboard_data(users_only, queues_only, calls_only)
        return json.dumps(data, indent=2)

    def start(self):
        """Start the web server."""
        print("=" * 60)
        print("  🚀 CCCP MONITOR - MOCK MODE")
        print("=" * 60)
        print(f"  Server: http://localhost:{self.port}")
        print(f"  Data: {self.data_file}")
        print("=" * 60)

        try:
            self.app.run(host="0.0.0.0", port=self.port, debug=False)
        except KeyboardInterrupt:
            print("\n⏹️  Server stopped by user")
        except Exception as e:
            print(f"\n❌ Server error: {e}")


def main():
    """Main entry point."""
    port = 6000
    data_file = "/tmp/cccp_mock_monitoring.json"

    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            port = 6000

    if len(sys.argv) > 2:
        data_file = sys.argv[2]

    server = SimpleWebServer(data_file, port)
    server.start()


if __name__ == "__main__":
    main()
