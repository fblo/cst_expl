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
import re
import glob
from datetime import datetime
from typing import Dict, List
import logging
import mysql.connector
import os

# Import configuration
from config import MYSQL_CONFIG, FLASK_CONFIG, NFS_CONFIG
from get_users_and_calls import RlogDispatcher
import threading

# Global dispatch instance
_rlog_dispatcher = None
_dispatch_start_thread = None

def get_rlog_dispatcher():
    """Get or create the global RlogDispatcher instance"""
    global _rlog_dispatcher
    if _rlog_dispatcher is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logs_dir = os.path.join(base_dir, "import_logs")
        logger.info(f"Creating new RlogDispatcher for {logs_dir}")
        _rlog_dispatcher = RlogDispatcher(logs_dir)
    logger.info(f"get_rlog_dispatcher: port={_rlog_dispatcher.port}, process={_rlog_dispatcher.process}")
    return _rlog_dispatcher

def _start_dispatch_async():
    """Start dispatch in background thread"""
    global _dispatch_start_thread
    try:
        dispatcher = get_rlog_dispatcher()
        if dispatcher.process is None:
            dispatcher.launch()
    except Exception as e:
        logger.error(f"Error starting dispatch in background: {e}")
    _dispatch_start_thread = None

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

        # Ne pas démarrer le thread de rafraîchissement automatique tant qu'un serveur n'est pas sélectionné
        self.refresh_thread = None
        self.is_refresh_enabled = False

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

    def enable_auto_refresh(self):
        """Enable the auto-refresh thread after a server is selected"""
        if not self.is_refresh_enabled and self.current_host:
            self.is_refresh_enabled = True
            self.refresh_thread = threading.Thread(target=self._auto_refresh, daemon=True)
            self.refresh_thread.start()
            logger.info("Auto-refresh enabled")

    def _refresh_users(self):
        """Fetch users, calls, and queues from get_users_and_calls.py"""
        # Ne pas essayer de rafraîchir si aucun hôte n'est défini
        if not self.current_host:
            logger.debug("No host configured, skipping refresh")
            return
            
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

# Global dictionary to store dispatch ports by date (from retrieve jobs)
_dispatch_ports_by_date = {}


def get_dispatch_port_for_date(date: str) -> Optional[int]:
    """Get the dispatch port for a specific date, or None if not found"""
    return _dispatch_ports_by_date.get(date)


def set_dispatch_port_for_date(date: str, port: int):
    """Store the dispatch port for a specific date"""
    _dispatch_ports_by_date[date] = port


# Global dictionary to track dispatch processes with metadata
_dispatch_info = {}  # port -> {"date": date, "project": str, "created_at": timestamp, "process": process}


# Global dictionary to store log retrieval snapshots (project_date -> snapshot)
_log_snapshots = {}  # key: "PROJECT_YYYY-MM-DD" -> {"project": str, "date": str, "port": int, "directory": str, "created_at": timestamp, "files_count": int}


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


def cleanup_old_snapshots(max_age_days: float = 7):
    """Clean up snapshots older than max_age_days"""
    import time as time_mod
    cutoff_time = time_mod.time() - (max_age_days * 24 * 60 * 60)
    cleaned = 0

    for key, snapshot in list(_log_snapshots.items()):
        if snapshot.get("created_at", 0) < cutoff_time:
            del _log_snapshots[key]
            cleaned += 1

    if cleaned > 0:
        logger.info(f"Cleaned up {cleaned} old log snapshots")

    return cleaned


def cleanup_stale_dispatches(max_age_seconds: float = 1800):
    """Clean up dispatch processes older than max_age_seconds (default: 30 minutes)"""
    import time as time_mod

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
                    import signal
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    logger.info(f"Cleaned up stale dispatch on port {port}")
                except Exception as e:
                    logger.warning(f"Failed to kill stale dispatch on port {port}: {e}")

            date = info.get("date")
            if date and _dispatch_ports_by_date.get(date) == port:
                del _dispatch_ports_by_date[date]


def register_dispatch(date: str, port: int, process, project: str = ""):
    """Register a new dispatch process"""
    import time as time_mod

    _dispatch_ports_by_date[date] = port
    _dispatch_info[port] = {
        "date": date,
        "project": project,
        "created_at": time_mod.time(),
        "process": process
    }
    logger.info(f"Registered dispatch on port {port} for date {date} (project: {project})")


_cleanup_thread = None

def _start_cleanup_thread():
    """Start the background thread that cleans up stale dispatch processes"""
    global _cleanup_thread

    def _cleanup_loop():
        while True:
            try:
                cleanup_stale_dispatches(1800)
            except Exception as e:
                logger.warning(f"Error in dispatch cleanup: {e}")
            time.sleep(60)

    if _cleanup_thread is None or not _cleanup_thread.is_alive():
        _cleanup_thread = threading.Thread(target=_cleanup_loop, daemon=True)
        _cleanup_thread.start()
        logger.info("Started dispatch cleanup thread")


def get_servers_from_mysql():
    """Fetch servers from MySQL database"""
    query = """
        SELECT
            p.name AS project, 
            v.cccip, 
            g.ccc_dispatch_port, 
            g.ccc_proxy_port,
            v.vocalnode AS vocal_node
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


@app.route("/rlog_console")
def rlog_console():
    """RLOG console page for sessions from log files"""
    return render_template("rlog_console.html")


@app.route("/rlog_console_light")
def rlog_console_light():
    """RLOG console page for sessions from log files (light theme)"""
    return render_template("rlog_console_light.html")


@app.route("/logs_explorer")
def logs_explorer():
    """Unified logs explorer - combines RLOG and NFS log viewing"""
    return render_template("logs_explorer.html")


@app.route("/logs_explorer_light")
def logs_explorer_light():
    """Unified logs explorer - combines RLOG and NFS log viewing (light theme)"""
    return render_template("logs_explorer_light.html")


@app.route("/api/rlog/status")
def api_rlog_status():
    """Get RlogDispatcher status"""
    try:
        dispatcher = get_rlog_dispatcher()
        last_activity = getattr(dispatcher, '_last_activity', None)
        import time
        return jsonify({
            "success": True,
            "port": dispatcher.port,
            "running": dispatcher.process is not None if dispatcher else False,
            "loaded_days": list(dispatcher._loaded_days) if hasattr(dispatcher, '_loaded_days') else [],
            "last_activity": last_activity,
            "inactive_seconds": int(time.time() - last_activity) if last_activity else None
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/rlog/start", methods=["POST"])
def api_rlog_start():
    """Start the RlogDispatcher asynchronously"""
    try:
        dispatcher = get_rlog_dispatcher()
        
        if dispatcher.process is not None:
            return jsonify({
                "success": True,
                "port": dispatcher.port,
                "message": "Dispatch already running"
            })
        
        # Start dispatch in background thread
        global _dispatch_start_thread
        if _dispatch_start_thread is None or not _dispatch_start_thread.is_alive():
            _dispatch_start_thread = threading.Thread(target=_start_dispatch_async, daemon=True)
            _dispatch_start_thread.start()
        
        return jsonify({
            "success": True,
            "port": dispatcher.port,
            "message": "Dispatch starting in background..."
        })
    except Exception as e:
        logger.error(f"Error starting dispatch: {e}")
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/rlog/stop", methods=["POST"])
def api_rlog_stop():
    """Stop the RlogDispatcher"""
    global _rlog_dispatcher
    if _rlog_dispatcher:
        _rlog_dispatcher.stop()
        _rlog_dispatcher = None
    return jsonify({"success": True, "message": "Dispatch stopped"})



@app.route("/api/dispatches")
def api_dispatches_list():
    """List all active dispatches"""
    import time as time_mod

    dispatches = []
    for port, info in _dispatch_info.items():
        process = info.get("process")
        is_running = process is not None and process.poll() is None
        age = int(time_mod.time() - info.get("created_at", 0))

        dispatches.append({
            "port": port,
            "date": info.get("date"),
            "created_at": info.get("created_at"),
            "age_seconds": age,
            "running": is_running
        })

    return jsonify({
        "success": True,
        "dispatches": dispatches,
        "count": len(dispatches)
    })


@app.route("/api/dispatches/cleanup", methods=["POST"])
def api_dispatches_cleanup():
    """Manually trigger cleanup of stale dispatches (>24h)"""
    count = _cleanup_stale_dispatches(86400)
    return jsonify({"success": True, "message": f"Cleaned up {count} stale dispatches"})


@app.route("/api/rlog/search")
def api_rlog_search():
    """Global search across all available dispatches"""
    import subprocess
    import time as time_mod
    import socket

    search_term = request.args.get("term", "").strip().lower()

    if not search_term:
        return jsonify({"success": False, "error": "Search term required"}), 400

    results = []
    searched_dates = set()

    # First, search in already running dispatches
    searched_dates = set()

    for date, port in list(_dispatch_ports_by_date.items()):
        if date in searched_dates:
            continue

        info = _dispatch_info.get(port, {})
        project = info.get("project", "")

        logger.info(f"Searching dispatch port {port} for date {date}, project={project}")

        try:
            cmd = [
                "/app/ccenter_report",
                "-login", "admin",
                "-password", "admin",
                "-server", "127.0.0.1",
                str(port),
                "-list",
                "-path", "/ccxml",
                "-field", "sessions",
                "-fields", "row.object_id;row.session_id;row.create_date",
                "-separator", "|"
            ]

            result = subprocess.run(cmd, capture_output=True, encoding="latin-1", timeout=10)

            sessions_found = 0
            matches_found = 0

            for line in result.stdout.strip().split("\n"):
                if line.strip() and "|" in line:
                    parts = line.strip().split("|")
                    if len(parts) >= 3:
                        object_id = parts[0].strip()
                        session_id = parts[1].strip()
                        create_date = parts[2].strip()

                        sessions_found += 1

                        if session_id and session_id.startswith("session_"):
                            # Get caller/called from session events
                            caller_num, called_num = _get_session_caller_called(port, object_id)

                            # Check if search term matches
                            term_lower = search_term.lower()
                            caller_lower = caller_num.lower() if caller_num else ""
                            called_lower = called_num.lower() if called_num else ""
                            session_lower = session_id.lower()
                            date_lower = create_date.lower()

                            # Normalize phone numbers for comparison (remove spaces, dashes, etc.)
                            caller_norm = caller_lower.replace(' ', '').replace('-', '').replace('.', '')
                            called_norm = called_lower.replace(' ', '').replace('-', '').replace('.', '')
                            term_norm = term_lower.replace(' ', '').replace('-', '').replace('.', '')

                            match = (
                                term_norm in caller_norm or
                                term_norm in called_norm or
                                term_norm in session_lower or
                                term_norm in date_lower
                            )

                            if match:
                                matches_found += 1
                                results.append({
                                    "id": session_id,
                                    "object_id": object_id,
                                    "project": project,
                                    "date": date,
                                    "caller": caller_num,
                                    "called": called_num,
                                    "create_date": create_date
                                })

            logger.info(f"Search on port {port}: {sessions_found} sessions, {matches_found} matches for '{search_term}'")
            searched_dates.add(date)

        except Exception as e:
            logger.warning(f"Failed to search dispatch on port {port}: {e}")

            searched_dates.add(date)
            logger.info(f"Searched dispatch port {port} for date {date}")

        except Exception as e:
            logger.warning(f"Failed to search dispatch on port {port}: {e}")

    return jsonify({
        "success": True,
        "term": search_term,
        "count": len(results),
        "results": results
    })


def _get_project_from_date(date_dir):
    """Extract project name from directory like 'PROJECT_2026-02-10'"""
    if not date_dir:
        return ""
    # Find the pattern PROJECT_DATE
    parts = date_dir.rsplit("_", 2)
    if len(parts) >= 2:
        return parts[0]
    return date_dir


@app.route("/api/logs/cleanup", methods=["POST"])
def api_logs_cleanup():
    """Manually trigger cleanup of old log directories (>2 days)"""
    result = _cleanup_old_directories(2)
    return jsonify({
        "success": True,
        "message": f"Cleaned up {result['cleaned']} old directories",
        "cleaned": result["cleaned"]
    })


@app.route("/api/logs/migrate", methods=["POST"])
def api_logs_migrate():
    """Remove old Logger/ structure (migration to date-based directories)"""
    removed = _cleanup_old_logger_structure()
    return jsonify({
        "success": True,
        "message": f"Old Logger/ structure removed: {removed}"
    })


@app.route("/api/rlog/cleanup", methods=["POST"])
def api_rlog_cleanup():
    """Cleanup old dispatch and restart if inactive for too long"""
    try:
        from get_users_and_calls import RlogDispatcher
        INACTIVITY_TIMEOUT = 2 * 60 * 60  # 2 hours
        
        dispatcher = RlogDispatcher.get_instance()
        
        if dispatcher and dispatcher.process:
            last_activity = getattr(dispatcher, '_last_activity', None)
            import time
            if last_activity and (time.time() - last_activity) > INACTIVITY_TIMEOUT:
                print(f"🛑 Nettoyage: dispatch inactif depuis {int(time.time() - last_activity)}s", file=sys.stderr)
                dispatcher.stop()
                RlogDispatcher.reset()
                return jsonify({
                    "success": True,
                    "message": "Old dispatch cleaned up",
                    "inactive_seconds": int(time.time() - last_activity)
                })
            else:
                return jsonify({
                    "success": True,
                    "message": "Dispatch is active",
                    "inactive_seconds": int(time.time() - last_activity) if last_activity else None
                })
        else:
            return jsonify({
                "success": True,
                "message": "No dispatch running"
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/rlog/sessions")
def api_rlog_sessions():
    """Get call sessions from dispatch for a specific date"""
    import subprocess
    import time as time_mod
    import socket

    date = request.args.get("date", "")

    if not date:
        return jsonify({"success": False, "error": "date required"}), 400

    dispatch_port = get_dispatch_port_for_date(date)

    if dispatch_port:
        port = dispatch_port
        logger.info(f"Using existing dispatch port {port} for date {date}")
    else:
        from get_users_and_calls import RlogDispatcher
        RlogDispatcher.reset()

        logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "import_logs")
        dispatcher = RlogDispatcher(logs_dir)

        new_port = None
        for port_candidate in range(35000, 35200):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', port_candidate))
                sock.close()
                if result != 0:
                    new_port = port_candidate
                    break
            except:
                pass

        if new_port:
            dispatcher.port = new_port

        logs_path = dispatcher.create_logger_structure()

        if not logs_path:
            raise RuntimeError(f"Aucun fichier .log trouvé dans {logs_dir}")

        env = os.environ.copy()
        env["PATH"] = env.get("PATH", "") + ":/opt/lampp/bin"

        interface_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debug_interface.xml")
        if not os.path.exists(interface_path):
            interface_path = os.path.join(logs_dir, "debug_interface.xml")

        cmd = [
            dispatcher.DISPATCH_BIN,
            "-slave", str(dispatcher.port),
            "-logs", logs_path,
            "-interface", interface_path,
            "-stderr"
        ]

        dispatcher.process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )

        time_mod.sleep(10)

        if dispatcher.process.poll() is not None:
            stderr = dispatcher.process.stderr.read().decode() if dispatcher.process.stderr else ""
            raise RuntimeError(f"Dispatch arrêté: {stderr}")

        dispatcher._last_activity = time_mod.time()
        port = dispatcher.port

        day = date.replace("-", "_")
        logger.info(f"Loading day {date} into dispatch on port {port}")
        dispatcher._load_day(day)
        time_mod.sleep(2)

    cmd = [
        "/app/ccenter_report",
        "-login", "admin",
        "-password", "admin",
        "-server", "127.0.0.1",
        str(port),
        "-list",
        "-path", "/ccxml",
        "-field", "sessions",
        "-fields", "row.object_id;row.session_id;row.create_date;row.caller_num;row.called_num;row.caller;row.called",
        "-separator", "|"
    ]

    result = subprocess.run(cmd, capture_output=True, encoding="latin-1", timeout=10)

    logger.info(f"Dispatch query result: stdout={result.stdout[:500] if result.stdout else 'empty'}")

    sessions = {}
    for line in result.stdout.strip().split("\n"):
        if line.strip() and "|" in line:
            parts = line.strip().split("|")

            if len(parts) >= 3:
                object_id = parts[0].strip()
                session_id = parts[1].strip()
                create_date = parts[2].strip()

                if session_id and session_id.startswith("session_"):
                    # Get caller/called from session events
                    caller_num, called_num = _get_session_caller_called(port, object_id)

                    # Also check raw fields as fallback
                    if not caller_num and len(parts) >= 4 and parts[3].strip() and parts[3].strip().lower() != "undefined":
                        caller_num = parts[3].strip()
                    if not called_num and len(parts) >= 5 and parts[4].strip() and parts[4].strip().lower() != "undefined":
                        called_num = parts[4].strip()

                    sessions[session_id] = {
                        "id": session_id,
                        "object_id": object_id,
                        "type": "call_session",
                        "caller": caller_num,
                        "called": called_num,
                        "create_date": create_date
                    }

    return jsonify({
        "success": True,
        "date": date,
        "sessions": sessions,
        "port": port
    })


def _get_session_caller_called(port: int, object_id: str) -> tuple:
    """Extract caller and called numbers from session events"""
    try:
        cmd = [
            "/app/ccenter_report",
            "-login", "admin",
            "-password", "admin",
            "-server", "127.0.0.1",
            str(port),
            "-list",
            "-path", "/dispatch",
            "-field", "events",
            "-fields", "row.name;row.string_data",
            "-object", object_id,
            "-separator", "|"
        ]

        result = subprocess.run(cmd, capture_output=True, encoding="latin-1", timeout=5)

        caller = ""
        called = ""
        phones_found = []  # List of (event_name, phone_number)

        for line in result.stdout.strip().split("\n"):
            if line.strip() and "|" in line:
                parts = line.strip().split("|")
                if len(parts) >= 2:
                    event_name = parts[0].strip() if parts[0].strip() else ""
                    string_data = parts[1].strip() if len(parts) > 1 and parts[1].strip() else ""

                    # Extract phone numbers from string_data
                    import re
                    phone_pattern = r'(?:00\d{2}|\+?\d{1,3}[-.\s]?)?\d{2}[-.\s]?\d{2}[-.\s]?\d{2}[-.\s]?\d{2}'
                    phones = re.findall(phone_pattern, string_data)

                    for p in phones:
                        normalized = p.lstrip('00').replace('-', '').replace('.', '').replace(' ', '')
                        # Filter out too short numbers or obvious non-phone numbers
                        if len(normalized) >= 8 and normalized.isdigit():
                            phones_found.append((event_name, p))

        # Analyze events to determine caller/called
        outcall_phones = []  # Outgoing calls - these are typically the caller
        incall_phones = []   # Incoming calls - these are typically the called
        ccxml_loaded_phones = []  # ccxml.loaded - contains caller (ANI/CLI)
        connection_alerting_phones = []  # connection.alerting - contains called (DNIS)
        other_phones = []

        for event_name, phone in phones_found:
            event_lower = event_name.lower()
            if 'outcall' in event_lower:
                outcall_phones.append(phone)
            elif 'incall' in event_lower:
                incall_phones.append(phone)
            elif 'ccxml.loaded' in event_lower:
                ccxml_loaded_phones.append(phone)
            elif 'connection.alerting' in event_lower:
                connection_alerting_phones.append(phone)
            else:
                other_phones.append((event_name, phone))

        # Priority order for caller:
        # 1. ccxml.loaded - contains the calling number (ANI/CLI)
        # 2. OutCall events
        # 3. Other events with valid phone numbers
        if ccxml_loaded_phones:
            caller = ccxml_loaded_phones[0]
        elif outcall_phones:
            caller = outcall_phones[0]
        elif other_phones:
            for event_name, phone in other_phones:
                if len(phone) >= 8:
                    caller = phone
                    break

        # Priority order for called:
        # 1. connection.alerting - contains the called number (DNIS)
        # 2. INCall events
        # 3. Other events with valid phone numbers (different from caller)
        if connection_alerting_phones:
            called = connection_alerting_phones[0]
        elif incall_phones:
            called = incall_phones[0]
        elif other_phones:
            for event_name, phone in other_phones:
                if len(phone) >= 8 and phone != caller:
                    called = phone
                    break

        logger.info(f"_get_session_caller_called: object_id={object_id}, phones={phones_found[:5]}, caller={caller}, called={called}")
        return caller, called

    except Exception as e:
        logger.warning(f"Failed to get caller/called for session {object_id}: {e}")
        return "", ""


@app.route("/api/rlog/session/detail", methods=["GET"])
def api_rlog_session_detail():
    """Get detailed events for a specific session from dispatch"""
    import subprocess
    
    session_id = request.args.get("session", "")
    date = request.args.get("date", "")
    
    if not session_id:
        return jsonify({"success": False, "error": "Session ID required"}), 400
    
    if not date:
        return jsonify({"success": False, "error": "Date required"}), 400
    
    def reformat_date(line):
        """Reformat date from French format to ISO format"""
        match = re.search(r"(\d{2}:\d{2}:\d{2}) le (\d{2}/\d{2}/\d{4})", line)
        if match:
            time_part = match.group(1)
            date_part = match.group(2)
            day, month, year = date_part.split("/")
            return f"[{year}-{month}-{day} {time_part}]" + line[match.end():]
        return line
    
    try:
        # Check if there's a dispatch port for this date
        dispatch_port = get_dispatch_port_for_date(date)
        
        if dispatch_port:
            # Use the dispatch port from the retrieve job
            port = dispatch_port
            logger.info(f"Using dispatch port {port} for date {date}")
        else:
            # Create a new dispatch for this date
            from get_users_and_calls import RlogDispatcher
            RlogDispatcher.reset()
            
            logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "import_logs")
            dispatcher = RlogDispatcher(logs_dir)
            
            # Find a new port
            import socket
            new_port = None
            for port_candidate in range(35000, 35200):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex(('127.0.0.1', port_candidate))
                    sock.close()
                    if result != 0:
                        new_port = port_candidate
                        break
                except:
                    pass
            
            if new_port:
                dispatcher.port = new_port
            
            # Manually launch the dispatch
            logs_path = dispatcher.create_logger_structure()
            
            if not logs_path:
                raise RuntimeError(f"Aucun fichier .log trouvé dans {logs_dir}")
            
            import os as os_mod
            env = os_mod.environ.copy()
            env["PATH"] = env.get("PATH", "") + ":/opt/lampp/bin"
            
            interface_path = os_mod.path.join(os_mod.path.dirname(os_mod.path.abspath(__file__)), "debug_interface.xml")
            if not os_mod.path.exists(interface_path):
                interface_path = os_mod.path.join(logs_dir, "debug_interface.xml")
            
            cmd = [
                dispatcher.DISPATCH_BIN,
                "-slave", str(dispatcher.port),
                "-logs", logs_path,
                "-interface", interface_path,
                "-stderr"
            ]
            
            import subprocess as sp
            dispatcher.process = sp.Popen(
                cmd,
                env=env,
                stdout=sp.DEVNULL,
                stderr=sp.PIPE,
                preexec_fn=os_mod.setsid
            )
            
            import time as time_mod
            time_mod.sleep(10)
            
            if dispatcher.process.poll() is not None:
                stderr = dispatcher.process.stderr.read().decode() if dispatcher.process.stderr else ""
                raise RuntimeError(f"Dispatch arrêté: {stderr}")
            
            dispatcher._last_activity = time_mod.time()
            port = dispatcher.port
            
            day_underscore = date.replace("-", "_")
            logger.info(f"Loading day {date} into dispatch on port {port}")
            dispatcher._load_day(day_underscore)
            time_mod.sleep(2)
        
        cmd = [
            "/app/ccenter_report",
            "-login", "admin",
            "-password", "admin",
            "-server", "127.0.0.1",
            str(port),
            "-list",
            "-path", "/ccxml",
            "-field", "sessions",
            "-fields", "row.object_id;row.session_id",
            "-separator", "|"
        ]
        
        result = subprocess.run(cmd, capture_output=True, encoding="latin-1", timeout=10)
        
        object_id = None
        for line in result.stdout.strip().split("\n"):
            if session_id in line and "|" in line:
                parts = line.strip().split("|")
                if len(parts) >= 2 and parts[0].isdigit():
                    object_id = parts[0]
                    break
        
        if not object_id:
            return jsonify({"success": False, "error": f"Session '{session_id}' not found on port {port}"}), 404
        
        cmd = [
            "/app/ccenter_report",
            "-login", "admin",
            "-password", "admin",
            "-server", "127.0.0.1",
            str(port),
            "-list",
            "-path", "/dispatch",
            "-field", "events",
            "-fields", "row.date;row.source;row.target;row.state;row.name;row.string_data",
            "-object", object_id,
            "-separator", "|"
        ]
        
        result = subprocess.run(cmd, capture_output=True, encoding="latin-1", timeout=10)
        
        output_lines = []
        output_columns = []
        
        for line in result.stdout.strip().split("\n"):
            if line.strip() and "|" in line:
                parts = line.strip().split("|")
                if len(parts) >= 6:
                    col_date = reformat_date(parts[0].strip())
                    col_source = parts[1].strip() if len(parts) > 1 else ""
                    col_target = parts[2].strip() if len(parts) > 2 else ""
                    col_state = parts[3].strip() if len(parts) > 3 else ""
                    col_name = parts[4].strip() if len(parts) > 4 else ""
                    col_data = "|".join(parts[5:]).strip() if len(parts) > 5 else ""
                    
                    output_columns.append({
                        "date": col_date,
                        "source": col_source,
                        "target": col_target,
                        "state": col_state,
                        "name": col_name,
                        "data": col_data
                    })
                    output_lines.append(f"{col_date}   {col_source}   {col_target}   {col_state}   {col_name}   {col_data}")
        
        return jsonify({
            "success": True,
            "session": session_id,
            "object_id": object_id,
            "date": date,
            "running": True,
            "count": len(output_lines),
            "output": output_lines,
            "columns": output_columns,
            "using_dispatch": True,
            "port": port
        })
            
    except Exception as e:
        logger.error(f"Error getting session detail: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)})


import uuid
import time
import shutil
import bz2
from concurrent.futures import ThreadPoolExecutor

_job_store = {}
_job_executor = ThreadPoolExecutor(max_workers=5)


def _run_dispatch_job(job_id: str, logs_dir: str, session_id: str, date: str):
    """Exécute le job de dispatch dans un thread séparé"""
    try:
        _job_store[job_id] = {
            "status": "starting",
            "progress": "Initialisation...",
            "session_id": session_id,
            "date": date,
            "created_at": time.time()
        }
        
        # Check if there's a dispatch port for this date
        dispatch_port = get_dispatch_port_for_date(date)
        
        if dispatch_port:
            # Use the existing dispatch port
            _job_store[job_id]["progress"] = f"Utilisation du dispatch sur port {dispatch_port}..."
            _job_store[job_id]["status"] = "loading"
            
            # Query the existing dispatch
            cmd = [
                "/app/ccenter_report",
                "-login", "admin",
                "-password", "admin",
                "-server", "127.0.0.1",
                str(dispatch_port),
                "-list",
                "-path", "/ccxml",
                "-field", "sessions",
                "-fields", "row.object_id;row.session_id",
                "-separator", "|"
            ]
            
            result = subprocess.run(cmd, capture_output=True, encoding="latin-1", timeout=10)
            
            object_id = None
            for line in result.stdout.strip().split("\n"):
                if session_id in line and "|" in line:
                    parts = line.strip().split("|")
                    if len(parts) >= 2 and parts[0].isdigit():
                        object_id = parts[0]
                        break
            
            if not object_id:
                _job_store[job_id]["status"] = "error"
                _job_store[job_id]["error"] = f"Session '{session_id}' non trouvée sur port {dispatch_port}"
                return
            
            # Query events from existing dispatch
            cmd = [
                "/app/ccenter_report",
                "-login", "admin",
                "-password", "admin",
                "-server", "127.0.0.1",
                str(dispatch_port),
                "-list",
                "-path", "/dispatch",
                "-field", "events",
                "-fields", "row.date;row.source;row.target;row.state;row.name;row.string_data",
                "-object", object_id,
                "-separator", "|"
            ]
            
            result = subprocess.run(cmd, capture_output=True, encoding="latin-1", timeout=10)
            
            def reformat_date(line):
                match = re.search(r"(\d{2}:\d{2}:\d{2}) le (\d{2}/\d{2}/\d{4})", line)
                if match:
                    time_part = match.group(1)
                    date_part = match.group(2)
                    day, month, year = date_part.split("/")
                    return f"[{year}-{month}-{day} {time_part}]" + line[match.end():]
                return line
            
            output_lines = []
            output_columns = []
            
            for line in result.stdout.strip().split("\n"):
                if line.strip() and "|" in line:
                    parts = line.strip().split("|")
                    if len(parts) >= 6:
                        col_date = reformat_date(parts[0].strip())
                        col_source = parts[1].strip() if len(parts) > 1 else ""
                        col_target = parts[2].strip() if len(parts) > 2 else ""
                        col_state = parts[3].strip() if len(parts) > 3 else ""
                        col_name = parts[4].strip() if len(parts) > 4 else ""
                        col_data = "|".join(parts[5:]).strip() if len(parts) > 5 else ""
                        
                        output_columns.append({
                            "date": col_date,
                            "source": col_source,
                            "target": col_target,
                            "state": col_state,
                            "name": col_name,
                            "data": col_data
                        })
                        output_lines.append(f"{col_date}   {col_source}   {col_target}   {col_state}   {col_name}   {col_data}")
            
            _job_store[job_id]["status"] = "ready"
            _job_store[job_id]["progress"] = f"Terminé ({len(output_lines)} événements)"
            _job_store[job_id]["result"] = {
                "success": True,
                "session": session_id,
                "object_id": object_id,
                "date": date,
                "running": True,
                "count": len(output_lines),
                "output": output_lines,
                "columns": output_columns,
                "using_dispatch": True,
                "port": dispatch_port
            }
            return
        
        # No existing dispatch found, create a new one
        from get_users_and_calls import RlogDispatcher

        dispatcher = RlogDispatcher(logs_dir)

        _job_store[job_id]["progress"] = "Lancement du dispatch..."
        _job_store[job_id]["status"] = "loading"

        port = dispatcher.launch(timeout=10)

        day = date.replace("-", "_")
        _job_store[job_id]["progress"] = f"Chargement du jour {date}..."

        dispatcher._load_day(day)

        _job_store[job_id]["progress"] = "Recherche de la session..."

        result = dispatcher.query("sessions")

        object_id = None
        for line in result.get("stdout", "").split("\n"):
            if session_id in line and "|" in line:
                parts = line.strip().split("|")
                if len(parts) >= 2 and parts[0].isdigit():
                    object_id = parts[0]
                    break

        if not object_id:
            _job_store[job_id]["status"] = "error"
            _job_store[job_id]["error"] = f"Session '{session_id}' non trouvée"
            dispatcher.stop()
            return

        _job_store[job_id]["progress"] = "Récupération des événements..."
        _job_store[job_id]["object_id"] = object_id

        events_result = dispatcher.query("session_detail", object_id=object_id)

        dispatcher.stop()

        output_lines = []
        output_columns = []

        for event in events_result.get("events", []):
            if isinstance(event, dict):
                output_columns.append({
                    "date": event.get("date", ""),
                    "source": event.get("source", ""),
                    "target": event.get("target", ""),
                    "state": event.get("state", ""),
                    "name": event.get("name", ""),
                    "data": event.get("data", "")
                })
                output_lines.append(f"{event.get('date', '')}   {event.get('source', '')}   {event.get('target', '')}   {event.get('state', '')}   {event.get('name', '')}   {event.get('data', '')}")
            else:
                line = str(event)
                output_lines.append(line)
                parts = line.split("|")
                if len(parts) >= 5:
                    output_columns.append({
                        "date": parts[0],
                        "source": parts[1],
                        "target": parts[2],
                        "state": parts[3],
                        "name": parts[4],
                        "data": "|".join(parts[5:]) if len(parts) > 5 else ""
                    })

        _job_store[job_id]["status"] = "ready"
        _job_store[job_id]["progress"] = f"Terminé ({len(output_lines)} événements)"
        _job_store[job_id]["result"] = {
            "success": True,
            "session": session_id,
            "object_id": object_id,
            "date": date,
            "running": True,
            "count": len(output_lines),
            "output": output_lines,
            "columns": output_columns,
            "using_dispatch": True,
            "port": port
        }
        
    except Exception as e:
        _job_store[job_id]["status"] = "error"
        _job_store[job_id]["error"] = str(e)
        logger.error(f"Dispatch job error: {e}")
        import traceback
        logger.error(traceback.format_exc())


@app.route("/api/rlog/session/detail/dispatch", methods=["POST"])
def api_rlog_session_detail_dispatch():
    """Lance un job de dispatch pour récupérer les détails d'une session"""
    session_id = request.json.get("session_id", "")
    date = request.json.get("date", "2026-02-08")

    if not session_id:
        return jsonify({"success": False, "error": "Session ID required"}), 400

    job_id = str(uuid.uuid4())

    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "import_logs")

    _job_executor.submit(_run_dispatch_job, job_id, logs_dir, session_id, date)

    return jsonify({
        "success": True,
        "job_id": job_id,
        "status": "starting",
        "session_id": session_id,
        "date": date
    })


@app.route("/api/rlog/job/<job_id>")
def api_rlog_job_status(job_id: str):
    """Récupère le statut d'un job"""
    if job_id not in _job_store:
        return jsonify({"success": False, "error": "Job not found"}), 404

    job = _job_store[job_id]

    response = {
        "success": True,
        "job_id": job_id,
        "status": job["status"],
        "progress": job["progress"],
        "session_id": job.get("session_id"),
        "date": job.get("date")
    }

    if job["status"] == "ready":
        response.update(job["result"])
        response.pop("result", None)
    elif job["status"] == "error":
        response["error"] = job.get("error", "Unknown error")
        response.pop("result", None)

    return jsonify(response)


@app.route("/api/rlog/job/<job_id>", methods=["DELETE"])
def api_rlog_job_cancel(job_id: str):
    """Annule un job en cours"""
    if job_id not in _job_store:
        return jsonify({"success": False, "error": "Job not found"}), 404

    job = _job_store[job_id]
    if job["status"] in ("starting", "loading"):
        job["status"] = "cancelled"
        job["progress"] = "Job annulé"

    return jsonify({"success": True, "status": "cancelled"})


# =============================================================================
# NFS LOG RETRIEVAL ENDPOINTS
# =============================================================================

_log_retrieval_jobs = {}


def _get_nfs_hostnames():
    """List available hostnames (vocal nodes) on the NFS mount"""
    nfs_dir = NFS_CONFIG["mount_directory"]
    if not os.path.exists(nfs_dir):
        return []
    try:
        return sorted([
            d for d in os.listdir(nfs_dir)
            if os.path.isdir(os.path.join(nfs_dir, d)) and not d.startswith(".")
        ])
    except Exception:
        return []


def _get_nfs_projects_for_hostname(hostname):
    """List projects available for a hostname on NFS"""
    nfs_dir = NFS_CONFIG["mount_directory"]
    logs_base = os.path.join(nfs_dir, hostname, "opt", "consistent", "logs")
    if not os.path.exists(logs_base):
        return []
    try:
        return sorted([
            d for d in os.listdir(logs_base)
            if os.path.isdir(os.path.join(logs_base, d)) and not d.startswith(".")
        ])
    except Exception:
        return []


def _get_nfs_log_path(hostname, project):
    """Get the full path to logs for a given hostname and project"""
    nfs_dir = NFS_CONFIG["mount_directory"]
    
    # Path structure: {mount}/interact-iv/{hostname}/opt/consistent/logs/{project}/Logger/{project}/_/ccenter_ccxml/Ccxml/{hostname}
    # Note: We construct up to 'Ccxml' and then look for the hostname submenu
    ccxml_base = os.path.join(
        nfs_dir, "interact-iv", hostname, "opt", "consistent", "logs", project,
        "Logger", project, "_", "ccenter_ccxml", "Ccxml"
    )
    
    if not os.path.exists(ccxml_base):
        # Try finding without interact-iv prefix (legacy path support)?
        # For now, stick to user request.
        return None
        
    # Find the actual hostname directory (may have suffix or be exact)
    try:
        # Check for exact match first
        exact_path = os.path.join(ccxml_base, hostname)
        if os.path.exists(exact_path):
            return exact_path
            
        # Fallback: scan for directory starting with hostname
        subdirs = [d for d in os.listdir(ccxml_base) if d.startswith(hostname)]
        if subdirs:
            return os.path.join(ccxml_base, subdirs[0])
    except Exception:
        pass
        
    return None


def _get_project_hostname_from_mysql(project_name):
    """Resolve project name to vocal hostname using MySQL.
    Returns a dict with ps_hostname (for NFS paths) and svc_hostname (from master_vocalnodes).
    """
    query = """
        SELECT
            v.cccip,
            g.cst_node,
            v.hostname AS svc_hostname
        FROM
            interactivportal.Global_referential g
        JOIN
            interactivportal.Projects p ON g.customer_id = p.id
        JOIN
            interactivdbmaster.master_vocalnodes v ON g.cst_node = v.vocalnode
        WHERE p.name = %s
    """
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (project_name,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            cst_node = result.get("cst_node")
            svc_hostname = result.get("svc_hostname")

            # Le cst_node peut être un shortcut (ex: "fr529") ou un hostname complet (ex: "ps-ics-prd-cst-fr-530")
            # Le svc_hostname contient toujours le hostname complet avec svc- (ex: "svc-ics-prd-cst-fr-529")
            # Pour le NFS, on a besoin du hostname avec ps- (ex: "ps-ics-prd-cst-fr-529")

            if svc_hostname:
                # Transformer svc- en ps- pour le chemin NFS
                ps_hostname = svc_hostname.replace("svc-", "ps-", 1)
            elif cst_node:
                # Fallback: utiliser cst_node directement
                ps_hostname = cst_node
                svc_hostname = None
            else:
                return None

            logger.info(f"MySQL for {project_name}: cst_node={cst_node}, svc_hostname={svc_hostname}, ps_hostname={ps_hostname}")

            return {
                "cst_node": cst_node,
                "svc_hostname": svc_hostname,
                "ps_hostname": ps_hostname,
            }

    except Exception as e:
        logger.error(f"MySQL error resolving hostname for {project_name}: {e}")

    return None


@app.route("/api/logs/projects")
def api_logs_projects():
    """List available projects (from MySQL database)"""
    try:
        # Fetch directly from MySQL instead of NFS scanning
        servers = get_servers_from_mysql()
        
        # Extract unique project names
        projects = sorted(list(set(s["project"] for s in servers if s.get("project"))))
        
        nfs_dir = NFS_CONFIG["mount_directory"]
        nfs_exists = os.path.exists(nfs_dir)
        
        return jsonify({
            "success": True,
            "nfs_path": nfs_dir,
            "nfs_available": nfs_exists,
            "projects": projects,
            "total_projects": len(projects)
        })
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        return jsonify({"success": False, "error": str(e)})


def _get_hostnames_for_project(project):
    """Find hostnames for a project - checks both NFS and local logs.
    Returns list of hostnames suitable for NFS path.
    """
    # First check local logs
    local_hostnames = _get_local_hostnames_for_project(project)
    if local_hostnames:
        logger.info(f"Local hostnames found for {project}: {local_hostnames}")
        return local_hostnames

    # Then check NFS via MySQL
    mysql_result = _get_project_hostname_from_mysql(project)

    if mysql_result:
        ps_hostname = mysql_result.get("ps_hostname")
        svc_hostname = mysql_result.get("svc_hostname")

        if ps_hostname:
            # Verify if path exists on NFS
            path = _get_nfs_log_path(ps_hostname, project)
            logger.info(f"MySQL for {project}: ps_hostname={ps_hostname}, svc_hostname={svc_hostname}")
            logger.info(f"NFS path check: {path} (exists: {os.path.exists(path) if path else False})")

            if path and os.path.exists(path):
                return [ps_hostname]
            else:
                # Try with svc_hostname if ps_hostname doesn't work
                if svc_hostname and svc_hostname != ps_hostname:
                    path2 = _get_nfs_log_path(svc_hostname, project)
                    if path2 and os.path.exists(path2):
                        logger.info(f"Using svc_hostname {svc_hostname} instead of ps_hostname {ps_hostname}")
                        return [svc_hostname]

    return []


def _get_local_hostnames_for_project(project):
    """Find hostnames for a project in local import_logs directory"""
    import glob
    
    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "import_logs")
    
    # Look for Logger/PROJECT/*/ccenter_ccxml/Ccxml/HOSTNAME structure
    pattern = os.path.join(logs_dir, "Logger", project, "*", "ccenter_ccxml", "Ccxml", "*")
    hostnames = set()
    
    for path in glob.glob(pattern):
        hostname = os.path.basename(path)
        # Exclude hidden directories and non-hostname paths
        if hostname and not hostname.startswith('.') and '_' not in hostname:
            hostnames.add(hostname)
    
    return list(hostnames) if hostnames else []


def _get_local_log_path(hostname, project):
    """Get the local log path for a given hostname and project"""
    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "import_logs")
    return os.path.join(logs_dir, "Logger", project, "_", "ccenter_ccxml", "Ccxml", hostname)


def _cleanup_old_directories(max_age_days: int = 2):
    """Clean up directories older than max_age_days in import_logs"""
    import time as time_mod
    import shutil

    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "import_logs")

    if not os.path.exists(logs_dir):
        return {"cleaned": 0, "errors": 0}

    cutoff_time = time_mod.time() - (max_age_days * 24 * 60 * 60)
    cleaned_count = 0
    error_count = 0

    for item in os.listdir(logs_dir):
        item_path = os.path.join(logs_dir, item)

        if not os.path.isdir(item_path):
            continue

        # Check if it's a date-based directory (contains _YYYY-MM-DD pattern)
        if "_20" not in item:
            continue

        try:
            mtime = os.path.getmtime(item_path)
            if mtime < cutoff_time:
                shutil.rmtree(item_path)
                logger.info(f"Cleaned up old directory: {item_path}")
                cleaned_count += 1
        except Exception as e:
            logger.warning(f"Failed to clean up {item_path}: {e}")
            error_count += 1

    if cleaned_count > 0:
        logger.info(f"Cleanup: removed {cleaned_count} old directories")

    return {"cleaned": cleaned_count, "errors": error_count}


def _cleanup_old_logger_structure():
    """Remove old import_logs/Logger/ structure (migration to date-based directories)"""
    import shutil

    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "import_logs")
    old_logger_path = os.path.join(logs_dir, "Logger")

    if os.path.exists(old_logger_path):
        try:
            shutil.rmtree(old_logger_path)
            logger.info(f"Migration: removed old Logger/ structure: {old_logger_path}")
            return True
        except Exception as e:
            logger.warning(f"Failed to remove old Logger/ structure: {e}")
            return False
    return False


def _cleanup_stale_dispatches(max_age_seconds: float = 86400):  # 24h
    """Clean up dispatch processes older than max_age_seconds"""
    import time as time_mod
    import signal

    current_time = time_mod.time()
    cleaned_count = 0

    for port, info in list(_dispatch_info.items()):
        created_at = info.get("created_at", 0)
        age = current_time - created_at

        if age > max_age_seconds:
            process = info.get("process")
            date = info.get("date")

            if process and process.poll() is None:
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    logger.info(f"Killed stale dispatch on port {port} (age: {age:.0f}s, date: {date})")
                except Exception as e:
                    logger.warning(f"Failed to kill dispatch on port {port}: {e}")

            # Remove from tracking
            if port in _dispatch_info:
                del _dispatch_info[port]

            if date and _dispatch_ports_by_date.get(date) == port:
                del _dispatch_ports_by_date[date]

            cleaned_count += 1

    return cleaned_count


def _run_log_retrieval_job(job_id, project, date, target_dir):
    """Background job: copy log files from NFS to local date-based directory, then launch dispatch"""
    try:
        _log_retrieval_jobs[job_id]["status"] = "running"

        # Cleanup old directories and snapshots
        _cleanup_old_directories(2)
        cleanup_old_snapshots(7)

        # Check if we have an existing snapshot for this project/date
        existing_snapshot = get_log_snapshot(project, date)

        if existing_snapshot:
            snapshot_port = existing_snapshot.get("port")
            snapshot_dir = existing_snapshot.get("directory")

            # Check if dispatch is still running on that port
            if snapshot_port and snapshot_port in _dispatch_info:
                info = _dispatch_info.get(snapshot_port, {})
                process = info.get("process")
                if process and process.poll() is None:
                    # Use existing dispatch
                    _log_retrieval_jobs[job_id]["progress"] = f"✅ Snapshot trouvé: dispatch sur port {snapshot_port}"
                    _log_retrieval_jobs[job_id]["cached"] = True
                    _log_retrieval_jobs[job_id]["dispatch_port"] = snapshot_port
                    _log_retrieval_jobs[job_id]["directory"] = snapshot_dir
                    _log_retrieval_jobs[job_id]["status"] = "done"
                    _log_retrieval_jobs[job_id]["copied"] = existing_snapshot.get("files_count", 0)
                    _log_retrieval_jobs[job_id]["snapshot_used"] = True

                    # Register dispatch if not already registered for this date
                    if date not in _dispatch_ports_by_date:
                        _dispatch_ports_by_date[date] = snapshot_port

                    logger.info(f"Log retrieval for {project}: using existing snapshot on port {snapshot_port}")
                    return

        # No existing snapshot, proceed with normal retrieval
        # Cleanup stale dispatches
        _cleanup_stale_dispatches(86400)

        # Get hostnames from MySQL database
        _log_retrieval_jobs[job_id]["progress"] = f"🔍 Recherche des hostnames pour {project} dans MySQL..."
        valid_hostnames = _get_hostnames_for_project(project)

        if not valid_hostnames:
            _log_retrieval_jobs[job_id]["status"] = "error"
            _log_retrieval_jobs[job_id]["error"] = f"Aucun hostname trouvé pour {project} dans la base MySQL (NFS: {NFS_CONFIG['mount_directory']})"
            return

        hostname = valid_hostnames[0]
        logger.info(f"Log retrieval for {project}: using hostname {hostname}")

        # Get NFS path from configuration
        nfs_path = _get_nfs_log_path(hostname, project)

        if not nfs_path:
            _log_retrieval_jobs[job_id]["status"] = "error"
            _log_retrieval_jobs[job_id]["error"] = f"Chemin NFS non configuré pour {hostname}"
            return

        # Check if NFS path exists
        if not os.path.exists(nfs_path):
            _log_retrieval_jobs[job_id]["status"] = "error"
            _log_retrieval_jobs[job_id]["error"] = f"Répertoire NFS introuvable: {nfs_path}"
            return

        logger.info(f"Log retrieval for {project}: NFS path = {nfs_path}")

        # Create date-based directory structure: import_logs/{PROJECT}_{DATE}/Logger/{PROJECT}/_/ccenter_ccxml/Ccxml/{hostname}
        date_based_dir = os.path.join(target_dir, "import_logs", f"{project}_{date}")
        logger_dir = os.path.join(date_based_dir, "Logger", project, "_", "ccenter_ccxml", "Ccxml", hostname)

        os.makedirs(logger_dir, exist_ok=True)

        # Check if logs have already been retrieved (cache check)
        existing_logs = glob.glob(os.path.join(logger_dir, "log_*.log"))
        existing_logs_compressed = glob.glob(os.path.join(logger_dir, "log_*.bz2"))
        logs_already_exist = len(existing_logs) > 0 or len(existing_logs_compressed) > 0

        copied = 0
        decompressed = 0
        errors = []
        is_cached = False
        total_files = 0

        if logs_already_exist:
            # Use cached logs
            total_files = len(existing_logs) + len(existing_logs_compressed)
            _log_retrieval_jobs[job_id]["progress"] = f"✅ Logs déjà récupérés ({total_files} fichiers existants)"
            _log_retrieval_jobs[job_id]["copied"] = total_files
            _log_retrieval_jobs[job_id]["decompressed"] = len(existing_logs)
            _log_retrieval_jobs[job_id]["cached"] = True
            is_cached = True
            logger.info(f"Log retrieval for {project}: using cached logs ({total_files} files)")
        else:
            # Find files for the date on NFS
            date_pattern = date.replace('-', '_')
            pattern = os.path.join(nfs_path, f"log_{date_pattern}*")
            _log_retrieval_jobs[job_id]["progress"] = f"🔍 Recherche des logs pour la date {date}..."
            files_to_copy = glob.glob(pattern)

            if not files_to_copy:
                _log_retrieval_jobs[job_id]["status"] = "error"
                _log_retrieval_jobs[job_id]["error"] = f"Aucun fichier log_{date_pattern}* trouvé dans {nfs_path}"
                return

            total_files = len(files_to_copy)
            _log_retrieval_jobs[job_id]["total_files"] = total_files
            _log_retrieval_jobs[job_id]["progress"] = f"📥 {total_files} fichiers log_{date_pattern}* trouvés sur NFS"

            for f in files_to_copy:
                try:
                    basename = os.path.basename(f)
                    dest = os.path.join(logger_dir, basename)

                    _log_retrieval_jobs[job_id]["progress"] = f"📥 Copie {basename}... ({copied + 1}/{total_files})"
                    shutil.copy2(f, dest)
                    copied += 1

                    if dest.endswith(".bz2"):
                        _log_retrieval_jobs[job_id]["progress"] = f"🗜️ Décompression {basename}... ({copied}/{total_files})"
                        decompressed_path = dest[:-4]
                        try:
                            with bz2.open(dest, 'rb') as bz_file:
                                with open(decompressed_path, 'wb') as out_file:
                                    shutil.copyfileobj(bz_file, out_file)
                            os.remove(dest)
                            decompressed += 1
                            logger.info(f"Log retrieval for {project}: decompressed {basename}")
                        except Exception as bz_err:
                            errors.append(f"Décompression {basename}: {bz_err}")
                            logger.warning(f"Log retrieval for {project}: failed to decompress {basename}: {bz_err}")

                    _log_retrieval_jobs[job_id]["copied"] = copied
                    _log_retrieval_jobs[job_id]["progress"] = f"📥 {copied}/{total_files} fichiers copiés vers {date_based_dir}/Logger/"

                except Exception as e:
                    errors.append(f"Copie {os.path.basename(f)}: {str(e)}")
                    logger.error(f"Log retrieval for {project}: failed to copy {os.path.basename(f)}: {e}")

            _log_retrieval_jobs[job_id]["cached"] = False
            _log_retrieval_jobs[job_id]["decompressed"] = decompressed
            _log_retrieval_jobs[job_id]["errors"] = errors

        # Launch dispatch
        _log_retrieval_jobs[job_id]["progress"] = "🚀 Lancement du dispatch..."
        _log_retrieval_jobs[job_id]["dispatch_launched"] = True

        try:
            from get_users_and_calls import RlogDispatcher
            RlogDispatcher.reset()

            dispatcher = RlogDispatcher(date_based_dir)

            # Find a new port
            import socket
            new_port = None
            for port in range(35000, 35200):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex(('127.0.0.1', port))
                    sock.close()
                    if result != 0:
                        new_port = port
                        break
                except:
                    pass

            if new_port:
                dispatcher.port = new_port

            _log_retrieval_jobs[job_id]["progress"] = f"🚀 Lancement du dispatch pour {project} sur port {dispatcher.port}..."
            dispatcher.create_logger_structure(project, hostname)

            logs_path = os.path.join(date_based_dir, "Logger")
            logger.info(f"Log retrieval for {project}: dispatch logs_path = {logs_path}")
            logger.info(f"Log retrieval for {project}: date_based_dir = {date_based_dir}")

            if not os.path.exists(logs_path):
                raise RuntimeError(f"Répertoire Logger non trouvé: {logs_path}")

            _log_retrieval_jobs[job_id]["progress"] = f"🚀 Dispatch sur port {dispatcher.port}, logs: {logs_path}/"

            import os as os_mod
            env = os_mod.environ.copy()
            env["PATH"] = env.get("PATH", "") + ":/opt/lampp/bin"

            interface_path = os_mod.path.join(os_mod.path.dirname(os_mod.path.abspath(__file__)), "debug_interface.xml")
            if not os_mod.path.exists(interface_path):
                interface_path = os_mod.path.join(date_based_dir, "debug_interface.xml")

            logger.info(f"Log retrieval for {project}: launching dispatch on port {dispatcher.port}")

            cmd = [
                dispatcher.DISPATCH_BIN,
                "-slave", str(dispatcher.port),
                "-logs", logs_path,
                "-interface", interface_path,
                "-stderr"
            ]

            _log_retrieval_jobs[job_id]["progress"] = f"🚀 Dispatch en cours de démarrage sur le port {dispatcher.port}..."

            import subprocess as sp
            dispatcher.process = sp.Popen(
                cmd,
                env=env,
                stdout=sp.DEVNULL,
                stderr=sp.PIPE,
                preexec_fn=os_mod.setsid
            )

            import time as time_mod
            time_mod.sleep(10)

            if dispatcher.process.poll() is not None:
                stderr = dispatcher.process.stderr.read().decode() if dispatcher.process.stderr else ""
                logger.error(f"Log retrieval for {project}: dispatch failed to start: {stderr}")
                raise RuntimeError(f"Dispatch arrêté: {stderr}")

            _log_retrieval_jobs[job_id]["progress"] = f"🚀 Dispatch démarré, chargement des logs pour {date}..."
            dispatcher._last_activity = time_mod.time()
            port = dispatcher.port

            day = date.replace("-", "_")
            logger.info(f"Log retrieval for {project}: loading day {date} into dispatch on port {port}")
            dispatcher._load_day(day)
            time_mod.sleep(2)

            # Register the dispatch process
            register_dispatch(date, port, dispatcher.process, project)

            # Save snapshot for future use
            files_count = total_files if is_cached else copied
            save_log_snapshot(project, date, port, date_based_dir, files_count)

            if is_cached:
                _log_retrieval_jobs[job_id]["status"] = "done"
                _log_retrieval_jobs[job_id]["progress"] = f"✅ Terminé (cache): {total_files} fichiers. Dispatch sur port {port}"
            else:
                _log_retrieval_jobs[job_id]["status"] = "done"
                _log_retrieval_jobs[job_id]["progress"] = f"✅ Terminé: {copied} fichiers copiés, {decompressed} décompressés. Dispatch sur port {port}"

            _log_retrieval_jobs[job_id]["dispatch_port"] = port
            _log_retrieval_jobs[job_id]["directory"] = date_based_dir

            cache_msg = " (cache)" if is_cached else ""
            logger.info(f"Log retrieval for {project}: completed successfully{cache_msg} - {total_files} files, dispatch on port {port}")

        except Exception as dispatch_err:
            _log_retrieval_jobs[job_id]["status"] = "done_with_errors"
            _log_retrieval_jobs[job_id]["progress"] = f"⚠️ Terminé avec erreurs: {total_files} fichiers. Erreur dispatch: {dispatch_err}"
            _log_retrieval_jobs[job_id]["dispatch_error"] = str(dispatch_err)
            logger.error(f"Log retrieval for {project}: dispatch error: {dispatch_err}")

        _log_retrieval_jobs[job_id]["errors"] = errors

    except Exception as e:
        _log_retrieval_jobs[job_id]["status"] = "error"
        _log_retrieval_jobs[job_id]["error"] = str(e)
        logger.error(f"Log retrieval job error: {e}")


@app.route("/api/logs/retrieve", methods=["POST"])
def api_logs_retrieve():
    """Start a background job to retrieve log files from NFS and launch dispatch"""
    data = request.json
    project = data.get("project", "")
    date = data.get("date", "")
    
    if not project or not date:
        return jsonify({"success": False, "error": "project and date required"}), 400
    
    job_id = str(uuid.uuid4())
    target_dir = os.path.dirname(os.path.abspath(__file__))
    
    _log_retrieval_jobs[job_id] = {
        "status": "starting",
        "progress": "Recherche du hostname pour " + project + "...",
        "project": project,
        "date": date,
        "created_at": time.time(),
        "copied": 0,
        "total_files": 0,
        "dispatch_launched": False,
        "error": None
    }
    
    _job_executor.submit(_run_log_retrieval_job, job_id, project, date, target_dir)
    
    return jsonify({
        "success": True,
        "job_id": job_id,
        "status": "starting",
        "project": project,
        "date": date
    })


@app.route("/api/logs/retrieve/status/<job_id>")
def api_logs_retrieve_status(job_id):
    """Get status of a log retrieval job"""
    if job_id not in _log_retrieval_jobs:
        return jsonify({"success": False, "error": "Job not found"}), 404
    
    job = _log_retrieval_jobs[job_id]
    return jsonify({
        "success": True,
        "job_id": job_id,
        **job
    })


@app.route("/api/logs/local")
def api_logs_local():
    """List log files currently in the local import_logs directory"""
    try:
        import glob
        logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "import_logs")
        
        log_files = glob.glob(os.path.join(logs_dir, "**/log_*.log*"), recursive=True)
        
        files_info = []
        dates = set()
        projects = set()
        
        for f in log_files:
            basename = os.path.basename(f)
            rel_path = os.path.relpath(f, logs_dir)
            
            # Extract date
            match = re.match(r'log_(\d{4}_\d{2}_\d{2})', basename)
            date_str = match.group(1).replace('_', '-') if match else "unknown"
            dates.add(date_str)
            
            # Extract project from path (Logger/PROJECT/...)
            path_parts = rel_path.split(os.sep)
            if len(path_parts) > 1 and path_parts[0] == "Logger":
                projects.add(path_parts[1])
            
            files_info.append({
                "name": basename,
                "path": rel_path,
                "size": os.path.getsize(f),
                "date": date_str,
                "compressed": basename.endswith(".bz2")
            })
        
        files_info.sort(key=lambda x: x["name"], reverse=True)
        
        return jsonify({
            "success": True,
            "logs_dir": logs_dir,
            "total_files": len(files_info),
            "dates": sorted(dates, reverse=True),
            "projects": sorted(projects),
            "files": files_info
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/logs/snapshots")
def api_logs_snapshots():
    """List all available log snapshots"""
    snapshots = []
    for key, snapshot in _log_snapshots.items():
        import time as time_mod
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

    # Sort by date descending
    snapshots.sort(key=lambda x: x.get("date", ""), reverse=True)

    return jsonify({
        "success": True,
        "count": len(snapshots),
        "snapshots": snapshots
    })


@app.route("/api/logs/snapshots/<project>/<date>")
def api_logs_snapshot_detail(project, date):
    """Get details of a specific snapshot"""
    key = f"{project}_{date}"
    snapshot = _log_snapshots.get(key)

    if not snapshot:
        return jsonify({"success": False, "error": f"Snapshot not found for {project} on {date}"}), 404

    return jsonify({
        "success": True,
        "key": key,
        **snapshot
    })


@app.route("/api/logs/snapshots/<project>/<date>", methods=["DELETE"])
def api_logs_snapshot_delete(project, date):
    """Delete a specific snapshot"""
    key = f"{project}_{date}"

    if key not in _log_snapshots:
        return jsonify({"success": False, "error": f"Snapshot not found for {project} on {date}"}), 404

    snapshot = _log_snapshots.pop(key)
    logger.info(f"Deleted log snapshot: {key}")

    return jsonify({
        "success": True,
        "message": f"Snapshot deleted for {project} on {date}"
    })


@app.route("/api/logs/snapshots/cleanup", methods=["POST"])
def api_logs_snapshots_cleanup():
    """Clean up old snapshots (>7 days)"""
    count = cleanup_old_snapshots(7)
    return jsonify({
        "success": True,
        "message": f"Cleaned up {count} old snapshots"
    })


if __name__ == "__main__":
    print("=" * 70)
    print("CCCP Explorer - Live Dashboard")
    print("=" * 70)

    print("Loading servers list from MySQL...")
    try:
        servers = get_servers_from_mysql()
        state.available_servers = {s["project"]: s for s in servers}
        print(f"Loaded {len(servers)} projects")
    except Exception as e:
        print(f"⚠️  MySQL unavailable: {e}")
        print("   Starting with empty project list (use Refresh in UI)")
        state.available_servers = {}

    print()
    print("Running migrations...")
    _cleanup_old_logger_structure()

    print(f"Server running: http://{FLASK_CONFIG['host']}:{FLASK_CONFIG['port']}")
    print("  - Go to / for project selection")
    print("  - Go to /cst_explorer/PROJECT_NAME to access a project directly")
    print("=" * 70)

    _start_cleanup_thread()

    app.run(host=FLASK_CONFIG["host"], port=FLASK_CONFIG["port"], debug=FLASK_CONFIG["debug"])
