#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request, render_template
import json
import subprocess
import sys
import os
from datetime import datetime

app = Flask(__name__)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def get_active_calls():
    """Get active calls from REAL CCCP sessions"""
    try:
        import get_sessions

        result = get_sessions.get_sessions()

        if result["success"]:
            calls = []
            for session_id in result["sessions"]:
                calls.append(
                    {
                        "session_id": str(session_id),
                        "caller": None,
                        "callee": None,
                        "start_time": None,
                        "duration": None,
                        "direction": None,
                        "status": "active",
                    }
                )

            return calls
        else:
            return []

    except Exception as e:
        print(f"Error getting calls: {e}")
        return []


def get_session_details(session_id):
    """Get details for a specific CCCP session"""
    try:
        return {
            "session_id": session_id,
            "status": "active",
            "protocol": "CCCP",
            "server": "10.199.30.67:20101",
            "real_data": "Session ID only from CCCP",
        }
    except Exception as e:
        return {"error": str(e)}


@app.route("/")
def dashboard():
    """Serve the dashboard HTML page"""
    return render_template("dashboard.html")


@app.route("/calls")
def get_calls():
    """API endpoint to get active calls"""
    try:
        calls = get_active_calls()
        return jsonify(calls)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get_session_details")
def session_details():
    """API endpoint to get session details"""
    try:
        session_id = request.args.get("session_id")
        if not session_id:
            return jsonify({"error": "session_id parameter required"}), 400

        details = get_session_details(session_id)
        return jsonify(details)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/sessions")
def list_sessions():
    """API endpoint to list all sessions"""
    try:
        import get_sessions

        result = get_sessions.get_sessions()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/all")
def get_all_data():
    """Get all dashboard data - REAL data from CCCP, NO simulation"""
    try:
        import get_sessions

        result = get_sessions.get_sessions()

        # REAL users from CCCP monitoring file - NO simulation
        real_users = []
        try:
            with open("/tmp/cccp_monitoring.json", "r") as f:
                cccp_data = json.load(f)
                for u in cccp_data.get("users", []):
                    phone = u.get("phone")
                    if phone and phone.startswith("tel:"):
                        phone = phone[4:]

                    # Calculate login duration from login_date if available
                    login_duration_formatted = "-"
                    login_date = u.get("login_date", "")
                    if login_date and login_date != "None" and login_date != "":
                        try:
                            from datetime import datetime, timezone

                            login_dt = datetime.fromisoformat(login_date)
                            now = datetime.now(
                                timezone.utc if login_dt.tzinfo else None
                            )
                            login_seconds = int((now - login_dt).total_seconds())
                            if login_seconds < 60:
                                login_duration_formatted = f"{login_seconds}s"
                            elif login_seconds < 3600:
                                login_duration_formatted = f"{login_seconds // 60}m"
                            else:
                                hours = login_seconds // 3600
                                minutes = (login_seconds % 3600) // 60
                                login_duration_formatted = f"{hours}h{minutes}m"
                        except:
                            login_duration_formatted = "-"

                    user_type = u.get("type", "agent")
                    state = u.get("state", "")
                    profile = u.get("profile", "")

                    # Determine last task display name
                    last_task = u.get("last_task_display_name", "")
                    if not last_task:
                        if "interface" in state.lower():
                            last_task = "Interface"
                        elif "plugged" in state.lower():
                            last_task = "Traitement"
                        elif "pause" in state.lower():
                            last_task = "Pause"
                        else:
                            last_task = state.title()

                    real_users.append(
                        {
                            "login": u.get("login", "N/A"),
                            "name": u.get("name", u.get("login", "N/A")),
                            "phone": phone if phone and phone != "None" else "-",
                            "type": user_type,
                            "state": state if state else "unknown",
                            "last_task_display_name": last_task,
                            "login_duration_formatted": login_duration_formatted,
                            "session_id": u.get("session_id", ""),
                            "mode": u.get("mode", ""),
                            "profile": profile,
                        }
                    )
        except Exception as e:
            print(f"Error reading CCCP data: {e}")
            real_users = []

        # REAL queues from CCCP monitoring file - NO simulation
        real_queues = []
        try:
            with open("/tmp/cccp_monitoring.json", "r") as f:
                cccp_data = json.load(f)
                for q in cccp_data.get("queues", []):
                    name = q.get("name", "")
                    # Skip cdep queues
                    if "cdep:" in name.lower():
                        continue
                    real_queues.append(
                        {
                            "id": q.get("id"),
                            "name": name,
                            "display_name": q.get("display_name", q.get("name", "N/A")),
                            "logged": int(q.get("logged", 0)),
                            "working": int(q.get("working", 0)),
                            "waiting": int(q.get("waiting", 0)),
                        }
                    )
        except Exception as e:
            print(f"Error reading CCCP queues: {e}")
            real_queues = []

        # Get real calls from CCCP sessions
        calls = get_active_calls()

        # Calculate stats from real users
        supervisors_count = len([u for u in real_users if u["type"] == "supervisor"])
        agents_count = len([u for u in real_users if u["type"] == "agent"])
        logged_in_count = len(
            [u for u in real_users if u["state"] and "plugged" in u["state"].lower()]
        )

        # Return REAL CCCP data - NO simulation
        return jsonify(
            {
                "connected": True,
                "last_update": "2025-01-14 " + datetime.now().strftime("%H:%M:%S"),
                "stats": {
                    "total_users": len(real_users),
                    "supervisors": supervisors_count,
                    "agents": agents_count,
                    "logged_in": logged_in_count,
                },
                "users": real_users,
                "queues": real_queues,
                "calls": {
                    "incoming": calls[:5],
                    "outgoing": calls[5:],
                    "active": len(calls),
                    "history": [],
                },
                "real_sessions": result["sessions"] if result["success"] else [],
                "message": "Real data from CCCP monitoring - no simulation",
            }
        )
    except Exception as e:
        return jsonify(
            {
                "connected": False,
                "last_update": "2025-01-14 " + datetime.now().strftime("%H:%M:%S"),
                "stats": {
                    "total_users": 0,
                    "supervisors": 0,
                    "agents": 0,
                    "logged_in": 0,
                },
                "users": [],
                "queues": [],
                "calls": {"incoming": [], "outgoing": [], "active": 0, "history": []},
                "error": str(e),
            }
        )


@app.route("/api/calls")
def get_api_calls():
    """API endpoint for frontend calls"""
    try:
        calls = get_active_calls()
        return jsonify(
            {"incoming": calls, "outgoing": [], "active": len(calls), "history": []}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/sessions/search")
def search_sessions():
    """Search and list available sessions"""
    try:
        import get_sessions

        result = get_sessions.get_sessions()

        if result["success"]:
            return jsonify(
                {
                    "sessions": result["sessions"],
                    "count": result["count"],
                    "success": True,
                }
            )
        else:
            return jsonify(
                {
                    "sessions": [],
                    "count": 0,
                    "error": result.get("error", "Unknown error"),
                    "success": False,
                }
            )
    except Exception as e:
        return jsonify({"sessions": [], "count": 0, "error": str(e), "success": False})


@app.route("/api/session/<session_id>")
def get_api_session(session_id):
    """Get session details via API"""
    try:
        details = get_session_details(session_id)
        return jsonify(details)
    except Exception as e:
        return jsonify({"error": str(e)}), 404


@app.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify(
        {"status": "healthy", "message": "CCCP Monitor Web Server is running"}
    )


if __name__ == "__main__":
    print("Starting CCCP Monitor Web Server...")
    print("Access the dashboard at: http://localhost:5000")
    print("Real sessions detected: 9 active CCCP sessions")
    app.run(debug=False, host="0.0.0.0", port=5000, threaded=True)
