#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's mcanal libraries.
# Interact-IV.com (c) 2013-2016
#
# Contact: softeam@interact-iv.com
# Authors:
#    - JTAG <jtag@interact-iv.com>

"""CCCP Sessions and Calls Management Module."""

import sys
import json
import time
import subprocess
from datetime import datetime, timezone, timedelta


class CccpSessionsManager(object):
    """Manages CCCP sessions and calls data."""

    def __init__(self, host="10.199.30.67", port=20103):
        self.host = host
        self.port = port
        self.test_script = "/home/fblo/Documents/repos/iv-cccp/test_dispatch_json.py"

    def fetch_cccp_data(self, timeout=15):
        """Fetch data from CCCP dispatch server."""
        try:
            result = subprocess.run(
                [sys.executable, self.test_script, self.host, str(self.port)],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                raise Exception("Test script error: %s" % result.stderr)
        except subprocess.TimeoutExpired:
            raise Exception("Test script timeout")
        except json.JSONDecodeError as e:
            raise Exception("Invalid JSON response: %s" % e)
        except Exception as e:
            raise Exception("Error fetching CCCP data: %s" % e)

    def process_users_data(self, cccp_data):
        """Process users data from CCCP response."""
        users = []
        cccp_users = cccp_data.get("users", [])

        for u in cccp_users:
            login = u.get("login", "")

            # Skip system user
            if login == "consistent":
                continue

            profile = u.get("sessions.last.session.profile_name", "")
            logged_str = u.get("sessions.last.session.logged", "False")
            logged = str(logged_str).lower() == "true"

            # Only keep logged in users
            if not logged:
                continue

            # Extract user information
            phone = u.get("sessions.last.session.phone_uri", "")
            mode = u.get("sessions.last.session.current_mode", "")
            pause_duration = u.get("state_group_pause.duration", "0")
            outbound_duration = u.get("state_group_outbound.duration", "0")
            login_date = u.get("sessions.last.session.login_date", "")
            session_id = u.get("sessions.last.session.session_id", "")
            state_start_date = u.get("states.last.state.start_date", "")

            if phone and phone.startswith("tel:"):
                phone = phone[4:]

            user_type = "agent"
            state = "plugged"

            # Determine user type and state
            last_state_name = u.get("last_state_name", "").lower()
            last_state_display_name = u.get("last_state_display_name", "").lower()

            if (
                (profile and "supervisor" in profile.lower())
                or login.startswith("supervisor")
                or "supervision" in last_state_name
                or "supervision" in last_state_display_name
            ):
                user_type = "supervisor"
                if "interface" in mode.lower():
                    state = "supervisor interface"
                elif "unplug" in mode.lower():
                    state = "supervisor unplug"
                else:
                    state = "supervisor plugged"
            else:
                last_state = u.get("last_state_display_name", "").lower()

                if "sortant" in last_state or "outbound" in last_state:
                    state = "outbound"
                elif "ringing" in last_state:
                    state = "ringing"
                elif "contact" in last_state or "busy" in last_state:
                    state = "busy"
                elif float(pause_duration) > 0:
                    state = "pause"
                else:
                    state = "plugged"

            # Calculate login duration
            login_duration_seconds = 0
            if login_date and login_date not in ("None", ""):
                try:
                    login_dt = datetime.fromisoformat(login_date)
                    now = datetime.now(timezone.utc if login_dt.tzinfo else None)
                    login_duration_seconds = int((now - login_dt).total_seconds())
                except Exception:
                    login_duration_seconds = 0

            users.append(
                {
                    "id": u.get("id"),
                    "login": login,
                    "name": login,
                    "state": state,
                    "profile": profile,
                    "logged_in": logged,
                    "type": user_type,
                    "phone": phone,
                    "mode": mode,
                    "last_state_display_name": u.get("last_state_display_name", ""),
                    "last_state_name": u.get("last_state_name", ""),
                    "last_task_display_name": u.get("last_task_display_name", ""),
                    "last_task_name": u.get("last_task_name", ""),
                    "login_date": login_date,
                    "session_id": session_id,
                    "state_start_date": state_start_date,
                    "login_duration_seconds": login_duration_seconds,
                    "login_duration_formatted": self._format_duration(
                        login_duration_seconds
                    ),
                }
            )

        return users

    def process_queues_data(self, cccp_data):
        """Process queues data from CCCP response."""
        queues = []
        for q in cccp_data.get("queues", []):
            name = q.get("name", "")

            # Skip CDEP queues
            if "cdep:" in name.lower():
                continue

            queues.append(
                {
                    "id": q.get("id"),
                    "name": name,
                    "display_name": q.get("display_name", q.get("name", "")),
                    "logged": int(q.get("logged_sessions_count", 0)),
                    "working": int(q.get("working_sessions_count", 0)),
                    "waiting": int(q.get("waiting_tasks_count", 0)),
                }
            )

        return queues

    def _calculate_duration(self, start_date, end_date=None):
        """Calculate duration between dates."""
        if not start_date or start_date in ("", "None"):
            return ""

        try:
            start_dt = datetime.fromisoformat(
                start_date.replace("/", "-").replace(" ", "T")
            )
            end_dt = (
                datetime.fromisoformat(end_date.replace("/", "-").replace(" ", "T"))
                if end_date and end_date not in ("", "None")
                else datetime.now(timezone.utc)
            )
            delta = end_dt - start_dt
            seconds = int(delta.total_seconds())
            return self._format_duration(seconds)
        except:
            return ""

    def _format_duration(self, seconds):
        """Format duration in human readable format."""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h{minutes}m"

    def _format_call_data(self, call, call_type="inbound"):
        """Format call data."""
        terminate_date = call.get("terminate_date", "")
        local_number = call.get(
            "attributes.local_number.value", call.get("user.name", "")
        )
        remote_number = call.get(
            "attributes.remote_number.value",
            call.get("last_outbound_call_target.value", ""),
        )
        user_login = call.get("user.login", call.get("manager_session.user.login", ""))

        if local_number and local_number.startswith("tel:"):
            local_number = local_number[4:]
        if remote_number and remote_number.startswith("tel:"):
            remote_number = remote_number[4:]

        start_date = call.get(
            "start_date",
            call.get(
                "management_effective_date",
                call.get("last_outbound_call_contact_start.value", ""),
            ),
        )
        duration = self._calculate_duration(start_date, terminate_date)

        return {
            "id": call.get(
                "session_id", call.get("id", call.get("outbound_call_id.value", ""))
            ),
            "type": call_type,
            "local_number": local_number,
            "remote_number": remote_number,
            "user_login": user_login,
            "queue_name": call.get("queue_name", ""),
            "create_date": call.get(
                "create_date", call.get("last_outbound_call_start.value", "")
            ),
            "start_date": start_date,
            "terminate_date": terminate_date,
            "duration": duration,
        }

    def process_calls_data(self, cccp_data, existing_history=None):
        """Process calls data from CCCP response."""
        incoming_calls = []
        outgoing_calls = []
        history_calls = list(existing_history) if existing_history else []
        active_count = 0

        # Process inbound calls
        for call in cccp_data.get("calls_inbound", []):
            terminate_date = call.get("terminate_date", "")

            if terminate_date and terminate_date not in ("", "None"):
                history_calls.append(self._format_call_data(call, "inbound"))
            else:
                active_count += 1
                incoming_calls.append(self._format_call_data(call, "inbound"))

        # Process outbound calls
        for call in cccp_data.get("calls_outbound", []):
            terminate_date = call.get("terminate_date", "")

            if terminate_date and terminate_date not in ("", "None"):
                history_calls.append(self._format_call_data(call, "outbound"))
            else:
                active_count += 1
                outgoing_calls.append(self._format_call_data(call, "outbound"))

        # Process call history
        for call in cccp_data.get("calls_history", []):
            session_type = call.get("session_type", "")
            is_outbound = str(session_type) == "3"
            call_type = "outbound" if is_outbound else "inbound"

            call_id = call.get("session_id", "")
            if not any(h["id"] == call_id for h in history_calls):
                history_calls.append(self._format_call_data(call, call_type))

        # Sort and limit history
        history_calls.sort(
            key=lambda x: x.get("terminate_date", "") or x.get("create_date", ""),
            reverse=True,
        )
        history_calls = history_calls[:100]

        return {
            "incoming": incoming_calls,
            "outgoing": outgoing_calls,
            "active": active_count,
            "history": history_calls,
        }

    def get_user_statistics(self, users):
        """Calculate user statistics."""
        total_users = len(users)
        supervisors = len([u for u in users if u.get("type") == "supervisor"])
        agents = len([u for u in users if u.get("type") == "agent"])
        logged_in = len([u for u in users if u.get("logged_in")])

        # State statistics
        states = {}
        for user in users:
            state = user.get("state", "unknown")
            states[state] = states.get(state, 0) + 1

        return {
            "total_users": total_users,
            "supervisors": supervisors,
            "agents": agents,
            "logged_in": logged_in,
            "states": states,
        }

    def get_queue_statistics(self, queues):
        """Calculate queue statistics."""
        total_queues = len(queues)
        total_logged = sum(q.get("logged", 0) for q in queues)
        total_working = sum(q.get("working", 0) for q in queues)
        total_waiting = sum(q.get("waiting", 0) for q in queues)

        return {
            "total_queues": total_queues,
            "total_logged": total_logged,
            "total_working": total_working,
            "total_waiting": total_waiting,
            "average_waiting": total_waiting / total_queues if total_queues > 0 else 0,
        }

    def get_call_statistics(self, calls):
        """Calculate call statistics."""
        incoming = calls.get("incoming", [])
        outgoing = calls.get("outgoing", [])
        history = calls.get("history", [])
        active = calls.get("active", 0)

        # Today's completed calls
        today = datetime.now().date()
        today_calls = [
            c
            for c in history
            if self._parse_date(c.get("terminate_date", "")).date() == today
        ]

        # Average call duration
        completed_calls = [
            c for c in history if c.get("duration") and c["duration"] != ""
        ]
        durations = []
        for call in completed_calls:
            try:
                duration_str = call["duration"]
                if "h" in duration_str:
                    h, m = duration_str.replace("h", "").replace("m", "").split()
                    total_minutes = int(h) * 60 + int(m)
                elif "m" in duration_str:
                    total_minutes = int(duration_str.replace("m", ""))
                else:
                    total_minutes = int(duration_str.replace("s", "")) / 60
                durations.append(total_minutes)
            except:
                pass

        avg_duration = sum(durations) / len(durations) if durations else 0

        return {
            "active_calls": active,
            "incoming_active": len(incoming),
            "outgoing_active": len(outgoing),
            "completed_today": len(today_calls),
            "total_completed": len(completed_calls),
            "average_duration_minutes": round(avg_duration, 1),
        }

    def _parse_date(self, date_str):
        """Parse date string safely."""
        try:
            if not date_str or date_str in ("", "None"):
                return datetime.now()
            return datetime.fromisoformat(date_str.replace("/", "-").replace(" ", "T"))
        except:
            return datetime.now()

    def get_monitoring_summary(self, cccp_data):
        """Get complete monitoring summary."""
        try:
            users = self.process_users_data(cccp_data)
            queues = self.process_queues_data(cccp_data)
            calls = self.process_calls_data(cccp_data)

            return {
                "timestamp": datetime.now().isoformat(),
                "connected": True,
                "users": users,
                "queues": queues,
                "calls": calls,
                "statistics": {
                    "users": self.get_user_statistics(users),
                    "queues": self.get_queue_statistics(queues),
                    "calls": self.get_call_statistics(calls),
                },
            }
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "connected": False,
                "error": str(e),
                "users": [],
                "queues": [],
                "calls": {
                    "incoming": [],
                    "outgoing": [],
                    "active": 0,
                    "history": [],
                },
            }
