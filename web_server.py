#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CCCP Explorer - Modern Real-Time Dashboard
Connects to CCCP server and displays real data
"""

from flask import Flask, jsonify, render_template, Response, request
from flask_cors import CORS
import threading
import time
import json
import subprocess
from datetime import datetime
from typing import Dict, List
import logging
import mysql.connector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cccp")

app = Flask(__name__, template_folder="templates")
app.jinja_env.auto_reload = True
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["JINJA2_CACHE_DISABLED"] = True
CORS(app)


# Global state


class DashboardState:
    def __init__(self):
        self.all_events: List[dict] = []
        self.users: List[dict] = []
        self.queues: List[dict] = []
        self.history: List[dict] = []
        self.last_update = datetime.now().isoformat()
        self.lock = threading.Lock()
        self.current_host = ""
        self.current_port = 20103
        self.current_project = ""
        self.has_project_selected = False
        self.available_servers: Dict[str, dict] = {}

        self.refresh_thread = threading.Thread(target=self._auto_refresh, daemon=True)
        self.refresh_thread.start()

    def _auto_refresh(self):
        """Auto-refresh data from CCCP"""
        while True:
            try:
                self._refresh_users()
            except Exception as e:
                logger.error(f"Auto-refresh error: {e}")
            time.sleep(30)

    def get_state(self) -> dict:
        """Get current dashboard state"""
        with self.lock:
            return {
                "event_count": len(self.all_events),
                "users_count": len(self.users),
                "queues_count": len(self.queues),
                "history_count": len(self.history),
                "last_update": self.last_update,
                "recent_events": self.all_events[-50:],
                "users": self.users,
                "queues": self.queues,
                "history": self.history[-100:],
                "current_host": self.current_host,
                "current_port": self.current_port,
                "current_project": self.current_project,
            }

    def add_event(self, event: dict):
        """Add event to history"""
        with self.lock:
            self.all_events.append(event)
            if len(self.all_events) > 500:
                self.all_events = self.all_events[-500:]

    def _refresh_users(self):
        """Fetch users, calls, and queues from get_users_and_calls.py"""
        try:
            with self.lock:
                host = self.current_host
                port = self.current_port

            result = subprocess.run(
                [
                    "python3",
                    "get_users_and_calls.py",
                    "--host",
                    host,
                    "--port",
                    str(port),
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                with self.lock:
                    self.users = data.get("users", {}).get("all", [])
                    self.history = data.get("calls", {}).get("all", [])
                    self.queues = data.get("queues", {}).get("all", [])
                    self.last_update = datetime.now().isoformat()
                    logger.info(
                        f"Loaded {len(self.users)} users, {len(self.history)} calls, {len(self.queues)} queues from {host}:{port}"
                    )
        except subprocess.TimeoutExpired:
            logger.error("Timeout fetching users/calls")
        except Exception as e:
            logger.error(f"Error fetching users/calls: {e}")


# Global state instance
state = DashboardState()

MYSQL_CONFIG = {
    "host": "vs-ics-prd-web-fr-505",
    "user": "interactiv",
    "password": "ics427!",
    "database": None,
    "charset": "utf8",
    "collation": "utf8_general_ci",
}


def get_servers_from_mysql():
    """Fetch servers from MySQL database"""
    query = """
        SELECT 
            p.name AS project, 
            v.cccip, 
            g.ccc_dispatch_port, 
            g.ccc_proxy_port
        FROM 
            interactivportal.Global_referential g
        JOIN 
            interactivportal.Projects p ON g.customer_id = p.id
        JOIN 
            interactivdbmaster.master_vocalnodes v ON g.cst_node = v.vocalnode
    """
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        logger.error(f"MySQL error: {e}")
        return []


# =============================================================================
# WEB ROUTES
# =============================================================================


@app.route("/")
def index():
    with open("templates/modern_dashboard.html", "r") as f:
        content = f.read()
    return Response(content, mimetype="text/html")


@app.route("/light")
def index_light():
    """Light theme version of the dashboard"""
    with open("templates/modern_dashboard_light.html", "r") as f:
        content = f.read()
    return Response(content, mimetype="text/html")


@app.route("/cst_explorer/<project_name>")
def cst_explorer(project_name: str):
    """Route for accessing a specific project directly"""
    servers = get_servers_from_mysql()
    state.available_servers = {s["project"]: s for s in servers}

    server = state.available_servers.get(project_name)
    if not server:
        return f"Project '{project_name}' not found", 404

    with state.lock:
        state.current_host = server["cccip"]
        state.current_port = server["ccc_dispatch_port"]
        state.current_project = project_name
        state.has_project_selected = True

    state._refresh_users()

    with open("templates/modern_dashboard.html", "r") as f:
        content = f.read()

    response = Response(content, mimetype="text/html")
    response.headers["X-Project-Name"] = project_name
    response.headers["X-Project-Host"] = state.current_host
    response.headers["X-Project-Port"] = str(state.current_port)
    return response


@app.route("/cst_explorer_light/<project_name>")
def cst_explorer_light(project_name: str):
    """Route for accessing a specific project directly with light theme"""
    servers = get_servers_from_mysql()
    state.available_servers = {s["project"]: s for s in servers}

    server = state.available_servers.get(project_name)
    if not server:
        return f"Project '{project_name}' not found", 404

    with state.lock:
        state.current_host = server["cccip"]
        state.current_port = server["ccc_dispatch_port"]
        state.current_project = project_name
        state.has_project_selected = True

    state._refresh_users()

    with open("templates/modern_dashboard_light.html", "r") as f:
        content = f.read()

    response = Response(content, mimetype="text/html")
    response.headers["X-Project-Name"] = project_name
    response.headers["X-Project-Host"] = state.current_host
    response.headers["X-Project-Port"] = str(state.current_port)
    return response


@app.route("/session_console")
def session_console():
    """Dedicated session console page"""
    return render_template("session_console.html")


@app.route("/console")
def console_minimal():
    """Minimal console page"""
    return render_template("console_minimal.html")


@app.route("/console_light")
def console_minimal_light():
    """Light theme console page"""
    return render_template("console_minimal_light.html")


@app.route("/api/status")
def api_status():
    """Get current dashboard status"""
    return jsonify(state.get_state())


@app.route("/api/events")
def api_events():
    """Get recent events"""
    limit = request.args.get("limit", 100, type=int)
    return jsonify(
        {"count": len(state.all_events), "events": state.all_events[-limit:]}
    )


@app.route("/api/events/stream")
def api_events_stream():
    """Server-Sent Events stream for real-time events"""

    def generate():
        last_idx = 0
        try:
            while True:
                current_len = len(state.all_events)
                if current_len > last_idx:
                    for event in state.all_events[last_idx:]:
                        try:
                            yield f"data: {json.dumps(event)}\n\n"
                        except Exception:
                            pass
                    last_idx = current_len
                time.sleep(0.2)
        except GeneratorExit:
            pass

    return Response(generate(), mimetype="text/event-stream")


@app.route("/api/users")
def api_users():
    """Get users"""
    return jsonify(state.users)


@app.route("/api/queues")
def api_queues():
    """Get queues"""
    return jsonify(state.queues)


@app.route("/api/history")
def api_history():
    """Get call history"""
    return jsonify(state.history)


@app.route("/api/servers")
def api_servers():
    """Get list of servers from MySQL"""
    servers = get_servers_from_mysql()
    return jsonify(servers)


@app.route("/api/select_server", methods=["POST"])
def api_select_server():
    """Select a server and update the dashboard state, returns all data"""
    data = request.json
    host = data.get("host", "")
    port = data.get("port", 20103)
    project = data.get("project", "")

    if not host:
        return jsonify({"success": False, "error": "Host required"}), 400

    with state.lock:
        state.current_host = host
        state.current_port = port
        state.current_project = project

    state._refresh_users()

    with state.lock:
        result = {
            "success": True,
            "host": host,
            "port": port,
            "project": project,
            "users": state.users,
            "queues": state.queues,
            "history": state.history,
            "last_update": state.last_update,
        }

    logger.info(
        f"Selected server: {project} - {host}:{port}, loaded {len(state.users)} users, {len(state.queues)} queues, {len(state.history)} calls"
    )
    return jsonify(result)


@app.route("/api/console/session", methods=["POST"])
def api_console_session():
    """Execute console command for a specific session (like test_cst.sh)"""
    data = request.json
    session_name = data.get("session", "")

    if not session_name:
        return jsonify({"success": False, "error": "Session name required"}), 400

    def reformat_date(line):
        """Convert 'HH:MM:SS le DD/MM/YYYY' to '[YYYY-MM-DD HH:MM:SS]'"""
        import re

        # Match pattern: "HH:MM:SS le DD/MM/YYYY"
        match = re.search(r"(\d{2}:\d{2}:\d{2}) le (\d{2}/\d{2}/\d{4})", line)
        if match:
            time_part = match.group(1)
            date_part = match.group(2)
            # Convert DD/MM/YYYY to YYYY-MM-DD
            day, month, year = date_part.split("/")
            iso_date = f"{year}-{month}-{day}"
            return f"[{iso_date} {time_part}]" + line[match.end() :]
        return line

    try:
        with state.lock:
            host = state.current_host
            port = state.current_port

        username = "admin"
        password = "admin"

        # Build and execute the command
        import subprocess

        # First get object_id for the session
        get_object_cmd = [
            "/app/ccenter_report",
            "-login",
            username,
            "-password",
            password,
            "-server",
            host,
            str(port),
            "-path",
            "/dispatch",
            "-field",
            "sessions",
            "-fields",
            "row.object_id;row.session_id",
            "-list",
        ]

        logger.info(f"Getting object_id for session: {session_name}")
        result = subprocess.run(
            get_object_cmd, capture_output=True, text=True, timeout=30
        )

        if result.returncode != 0:
            return jsonify(
                {"success": False, "error": f"Failed to get object_id: {result.stderr}"}
            )

        # Parse object_id from the result
        object_id = None
        for line in result.stdout.strip().split("\n"):
            if session_name in line and "|" in line:
                parts = line.strip().split("|")
                if len(parts) >= 2 and parts[0].strip().isdigit():
                    object_id = parts[0].strip()
                    break

        if not object_id:
            return jsonify(
                {"success": False, "error": f"Session '{session_name}' not found"}
            )

        logger.info(f"Found object_id: {object_id} for session: {session_name}")

        # Now get events using the object_id
        get_events_cmd = [
            "/app/ccenter_report",
            "-login",
            username,
            "-password",
            password,
            "-server",
            host,
            str(port),
            "-path",
            "/dispatch",
            "-field",
            "events",
            "-fields",
            "row.date;row.source;row.target;row.state;row.name;row.string_data",
            "-object",
            object_id,
            "-list",
        ]

        logger.info(f"Getting events for object_id: {object_id}")
        events_result = subprocess.run(
            get_events_cmd,
            capture_output=True,
            encoding="latin-1",
            errors="replace",
            timeout=60,
        )

        if events_result.returncode != 0:
            return jsonify(
                {
                    "success": False,
                    "error": f"Failed to get events: {events_result.stderr}",
                }
            )

        # Format output: replace pipes with spaces AND reformat dates
        output_lines = []
        output_columns = []
        for line in events_result.stdout.strip().split("\n"):
            # Skip empty lines and header/footer
            if (
                line.strip()
                and "|" in line
                and "Object ID:" not in line
                and "Lignes:" not in line
                and "Fin" not in line
            ):
                # Parse columns
                parts = line.strip().split("|")
                if len(parts) >= 6:
                    col_date = parts[0].strip() if len(parts) > 0 else ""
                    col_source = parts[1].strip() if len(parts) > 1 else ""
                    col_target = parts[2].strip() if len(parts) > 2 else ""
                    col_state = parts[3].strip() if len(parts) > 3 else ""
                    col_name = parts[4].strip() if len(parts) > 4 else ""
                    col_data = parts[5].strip() if len(parts) > 5 else ""

                    # Reformat date
                    col_date = reformat_date(col_date)

                    output_columns.append(
                        {
                            "date": col_date,
                            "source": col_source,
                            "target": col_target,
                            "state": col_state,
                            "name": col_name,
                            "data": col_data,
                        }
                    )

                # Also keep formatted text for backward compatibility
                formatted_line = line.replace("|", "   ")
                formatted_line = formatted_line.rstrip()
                formatted_line = reformat_date(formatted_line)
                output_lines.append(formatted_line)

        return jsonify(
            {
                "success": True,
                "session": session_name,
                "object_id": object_id,
                "output": output_lines,
                "columns": output_columns,
                "count": len(output_lines),
            }
        )

    except subprocess.TimeoutExpired:
        return jsonify({"success": False, "error": "Command timeout (60 seconds)"}), 500
    except Exception as e:
        logger.error(f"Console session error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/protocol")
def api_protocol():
    """Get protocol specification"""
    return jsonify(
        {
            "name": "CCCP Explorer Protocol",
            "version": "1.0",
            "description": "Based on consistent_explorer.exe decompilation",
            "message_types": {
                "103": "INITIALIZE",
                "10000": "LOGIN",
                "10009": "QUERY_LIST",
                "10049": "USE_DEFAULT_NAMESPACES_INDEX",
                "20000": "CONNECTION_OK",
                "20001": "LOGIN_OK",
                "20002": "LOGIN_FAILED",
                "20003": "RESULT",
                "20007": "LIST_RESPONSE",
                "20008": "OBJECT_RESPONSE",
                "20009": "SERVER_EVENT",
                "20012": "START_RESULT",
                "20038": "USE_DEFAULT_NAMESPACES_INDEX_OK",
            },
            "event_fields": [
                "session_id",
                "source",
                "target",
                "delay",
                "event_name",
                "event_object",
            ],
            "binary_format": "[LENGTH(4)][MESSAGE_ID(4)][PAYLOAD...]",
        }
    )


if __name__ == "__main__":
    print("=" * 70)
    print("CCCP Explorer - Live Dashboard")
    print("=" * 70)

    print("Loading servers list from MySQL...")
    servers = get_servers_from_mysql()
    state.available_servers = {s["project"]: s for s in servers}
    print(f"Loaded {len(servers)} projects")

    print()
    print("Server running: http://localhost:5000")
    print("  - Go to / for project selection")
    print("  - Go to /cst_explorer/PROJECT_NAME to access a project directly")
    print("=" * 70)

    app.run(host="0.0.0.0", port=5000, debug=False)
