#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's mcanal libraries.
# Interact-IV.com (c) 2013-2016
#
# Contact: softeam@interact-iv.com
# Authors:
#    - JTAG <jtag@interact-iv.com>

"""CCCP Mock Data Generator for Testing."""

import json
import time
import random
from datetime import datetime, timedelta


class CccpDataGenerator(object):
    """Generate mock CCCP data for testing."""

    def __init__(self):
        self.user_counter = 1
        self.queue_counter = 1
        self.call_counter = 1

    def generate_mock_users(self, count=10):
        """Generate mock user data."""
        users = []
        states = ["plugged", "busy", "pause", "ringing", "outbound"]
        types = ["agent", "supervisor"]

        for i in range(count):
            user_id = f"user_{self.user_counter:04d}"
            login = f"user{self.user_counter:03d}"
            self.user_counter += 1

            # Random state
            state = random.choice(states)
            user_type = random.choice(types)

            user = {
                "id": user_id,
                "login": login,
                "name": login,
                "state": state,
                "profile": f"profile_{user_type}",
                "logged_in": True,
                "type": user_type,
                "phone": f"012345678{user_id[-4:]}",
                "mode": "normal" if user_type == "agent" else "supervisor",
                "last_state_display_name": state.title(),
                "last_state_name": state,
                "login_date": (
                    datetime.now() - timedelta(hours=random.randint(1, 8))
                ).isoformat(),
                "session_id": f"sess_{user_id}",
                "login_duration_seconds": random.randint(300, 28800),
                "login_duration_formatted": f"{random.randint(5, 480)}m",
            }
            users.append(user)

        return users

    def generate_mock_queues(self, count=5):
        """Generate mock queue data."""
        queues = []
        for i in range(count):
            queue_id = f"queue_{self.queue_counter:03d}"
            self.queue_counter += 1

            queue = {
                "id": queue_id,
                "name": f"Queue_{i + 1}",
                "display_name": f"Service Queue {i + 1}",
                "logged": random.randint(2, 8),
                "working": random.randint(1, 6),
                "waiting": random.randint(0, 15),
            }
            queues.append(queue)

        return queues

    def generate_mock_calls(self, active_count=3, history_count=20):
        """Generate mock call data."""
        calls = {"incoming": [], "outgoing": [], "active": active_count, "history": []}

        # Active calls
        for i in range(active_count):
            call = {
                "id": f"call_{self.call_counter:04d}",
                "type": "incoming" if i % 2 == 0 else "outgoing",
                "local_number": f"012345678{random.randint(1000, 9999)}",
                "remote_number": f"0612345678{random.randint(1000, 9999)}",
                "user_login": f"user{random.randint(1, 20):03d}",
                "queue_name": f"Queue_{random.randint(1, 5)}",
                "create_date": (
                    datetime.now() - timedelta(minutes=random.randint(1, 30))
                ).isoformat(),
                "start_date": (
                    datetime.now() - timedelta(minutes=random.randint(1, 25))
                ).isoformat(),
                "terminate_date": "",
                "duration": f"{random.randint(5, 120)}s",
            }

            if i % 2 == 0:
                calls["incoming"].append(call)
            else:
                calls["outgoing"].append(call)

            self.call_counter += 1

        # Call history
        for i in range(history_count):
            history_call = {
                "id": f"hist_{i + 1:04d}",
                "type": "incoming" if i % 2 == 0 else "outgoing",
                "local_number": f"012345678{random.randint(1000, 9999)}",
                "remote_number": f"0612345678{random.randint(1000, 9999)}",
                "user_login": f"user{random.randint(1, 20):03d}",
                "queue_name": f"Queue_{random.randint(1, 5)}",
                "create_date": (
                    datetime.now() - timedelta(hours=random.randint(1, 12))
                ).isoformat(),
                "start_date": (
                    datetime.now() - timedelta(hours=random.randint(1, 11))
                ).isoformat(),
                "terminate_date": (
                    datetime.now() - timedelta(hours=random.randint(1, 10))
                ).isoformat(),
                "duration": f"{random.randint(30, 300)}s",
            }

            calls["history"].append(history_call)

        return calls

    def generate_mock_data(self):
        """Generate complete mock CCCP data."""
        users = self.generate_mock_users(15)
        queues = self.generate_mock_queues(6)
        calls = self.generate_mock_calls(2, 25)

        data = {
            "ip": "10.199.30.67",
            "connected": True,
            "last_update": datetime.now().isoformat(),
            "users": users,
            "queues": queues,
            "calls": calls,
            "statistics": {
                "users": {
                    "total_users": len(users),
                    "supervisors": len([u for u in users if u["type"] == "supervisor"]),
                    "agents": len([u for u in users if u["type"] == "agent"]),
                    "logged_in": len([u for u in users if u["logged_in"]]),
                    "states": {
                        "plugged": len([u for u in users if u["state"] == "plugged"]),
                        "busy": len([u for u in users if u["state"] == "busy"]),
                        "pause": len([u for u in users if u["state"] == "pause"]),
                        "ringing": len([u for u in users if u["state"] == "ringing"]),
                        "outbound": len([u for u in users if u["state"] == "outbound"]),
                    },
                },
                "queues": {
                    "total_queues": len(queues),
                    "total_logged": sum(q["logged"] for q in queues),
                    "total_working": sum(q["working"] for q in queues),
                    "total_waiting": sum(q["waiting"] for q in queues),
                    "average_waiting": sum(q["waiting"] for q in queues) / len(queues)
                    if len(queues) > 0
                    else 0,
                },
                "calls": {
                    "active_calls": calls["active"],
                    "incoming_active": len(calls["incoming"]),
                    "outgoing_active": len(calls["outgoing"]),
                    "completed_today": len(
                        [c for c in calls["history"] if "today" in c["start_date"]]
                    ),
                    "total_completed": len(calls["history"]),
                    "average_duration": 120,  # Mock average
                },
            },
            "errors": [],
        }

        return data

    def save_mock_data(self, data, file_path="/tmp/cccp_mock_monitoring.json"):
        """Save mock data to file."""
        try:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
            return True, f"Mock data saved to {file_path}"
        except Exception as e:
            return False, f"Error saving mock data: {e}"


if __name__ == "__main__":
    generator = CccpDataGenerator()

    print("🧪 Generating Mock CCCP Data...")
    data = generator.generate_mock_data()

    success, message = generator.save_mock_data(data)

    if success:
        print(f"✅ {message}")
        print(
            f"📊 Generated {len(data['users'])} users, {len(data['queues'])} queues, {len(data['calls']['history'])} call history"
        )
    else:
        print(f"❌ {message}")
