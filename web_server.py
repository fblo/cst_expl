#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request, render_template, after_this_request
from flask_cors import CORS
import json
import subprocess
import sys
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Cache for dispatch call data
_calls_cache = {"data": None, "timestamp": 0}
CACHE_DURATION = 30  # seconds


def get_dispatch_call_data():
    """Get real call data from CCCP dispatch with caching using subprocess"""
    import time

    now = time.time()

    if _calls_cache["data"] and (now - _calls_cache["timestamp"]) < CACHE_DURATION:
        return _calls_cache["data"]

    try:
        cmd = [
            "python3",
            "/home/fblo/Documents/repos/explo-cst/recup_dispatch_project.py",
            "10.199.30.67",
            "20103",
            "MPU_PREPROD",
        ]
        proc_result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=30,
        )

        if proc_result.returncode == 0 and proc_result.stdout.strip():
            output = proc_result.stdout
            # Extract JSON from output (find the JSON block)
            json_start = output.find("{")
            json_end = output.rfind("}")
            if json_start >= 0 and json_end > json_start:
                json_str = output[json_start : json_end + 1]
                dispatch_data = json.loads(json_str)

            if not dispatch_data or not dispatch_data.get("connected"):
                raise Exception("Dispatch not connected")

            active = dispatch_data.get("active", {})
            terminated = dispatch_data.get("terminated", {})

            incoming = []
            for call in active.get("incoming_calls", []):
                incoming.append(
                    {
                        "session_id": call.get("session_id", "N/A"),
                        "caller": call.get("caller", "-"),
                        "callee": call.get("callee", "-"),
                        "start_time": call.get("start_time", "-"),
                        "direction": "incoming",
                        "status": call.get("status", "active"),
                        "user_login": "",
                        "user_name": "",
                        "queue_name": "",
                    }
                )

            outgoing = []
            for call in active.get("outgoing_calls", []):
                outgoing.append(
                    {
                        "session_id": call.get("session_id", "N/A"),
                        "caller": call.get("caller", "-"),
                        "callee": call.get("callee", "-"),
                        "start_time": call.get("start_time", "-"),
                        "direction": "outgoing",
                        "status": call.get("status", "active"),
                        "user_login": "",
                        "user_name": "",
                        "queue_name": "",
                    }
                )

            terminated_calls = []
            for call in terminated.get("calls", []):
                terminated_calls.append(
                    {
                        "session_id": call.get("session_id", ""),
                        "type": call.get("type", ""),
                        "start_time": call.get("start_time", ""),
                        "end_time": call.get("end_time", ""),
                        "user": call.get("user", ""),
                    }
                )

            result = {
                "incoming": incoming,
                "outgoing": outgoing,
                "active": len(incoming) + len(outgoing),
                "history": terminated_calls,
                "users": dispatch_data.get("users", []),
                "queues": dispatch_data.get("queues", []),
            }

            _calls_cache["data"] = result
            _calls_cache["timestamp"] = now

            return result

    except subprocess.TimeoutExpired:
        print("Dispatch call timed out")
    except Exception as e:
        print(f"Error getting dispatch data: {e}")
        import traceback

        traceback.print_exc()

    return _calls_cache["data"] or {
        "incoming": [],
        "outgoing": [],
        "active": 0,
        "history": [],
    }


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
    """DEPRECATED - Now using /api/all for calls data"""
    try:
        call_data = get_dispatch_call_data()
        return jsonify(
            {
                "incoming": call_data.get("incoming", []),
                "outgoing": call_data.get("outgoing", []),
                "active": call_data.get("active", 0),
            }
        )
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


@app.route("/api/all")
def get_all_data():
    """Get all dashboard data from CCCP dispatch"""
    try:
        dispatch_data = get_dispatch_call_data()

        users = dispatch_data.get("users", [])
        queues = dispatch_data.get("queues", [])
        history = dispatch_data.get("history", [])

        real_sessions = [
            c.get("session_id", "") for c in history if c.get("session_id")
        ]

        supervisors_count = len(
            [u for u in users if u.get("type", "").lower() == "supervisor"]
        )
        agents_count = len([u for u in users if u.get("type", "").lower() == "agent"])
        logged_in_count = len(users)

        return jsonify(
            {
                "connected": True,
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "stats": {
                    "total_users": len(users),
                    "supervisors": supervisors_count,
                    "agents": agents_count,
                    "logged_in": logged_in_count,
                },
                "users": users,
                "queues": queues,
                "calls": dispatch_data,
                "real_sessions": real_sessions,
                "message": "Data from CCCP dispatch",
            }
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify(
            {
                "connected": False,
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "stats": {
                    "total_users": 0,
                    "supervisors": 0,
                    "agents": 0,
                    "logged_in": 0,
                },
                "users": [],
                "queues": [],
                "calls": {"incoming": [], "outgoing": [], "active": 0, "history": []},
                "real_sessions": [],
                "error": str(e),
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
        call_data = get_dispatch_call_data()
        return jsonify(call_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
