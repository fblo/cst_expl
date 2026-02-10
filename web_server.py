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
from datetime import datetime
from typing import Dict, List
import logging
import mysql.connector
import os

# Import configuration
from config import MYSQL_CONFIG, FLASK_CONFIG
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
        _rlog_dispatcher = RlogDispatcher.get_instance(logs_dir)
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


@app.route("/rlog_console")
def rlog_console():
    """RLOG console page for sessions from log files"""
    return render_template("rlog_console.html")


@app.route("/rlog_console_light")
def rlog_console_light():
    """RLOG console page for sessions from log files (light theme)"""
    return render_template("rlog_console_light.html")


@app.route("/api/rlog/status")
def api_rlog_status():
    """Get RlogDispatcher status"""
    try:
        dispatcher = get_rlog_dispatcher()
        return jsonify({
            "success": True,
            "port": dispatcher.port,
            "running": dispatcher.process is not None,
            "loaded_days": list(dispatcher._loaded_days) if hasattr(dispatcher, '_loaded_days') else []
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
    try:
        global _rlog_dispatcher
        if _rlog_dispatcher:
            _rlog_dispatcher.stop()
            _rlog_dispatcher = None
        return jsonify({"success": True, "message": "Dispatch stopped"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/rlog/sessions")
def api_rlog_sessions():
    """Get call sessions from log files using direct parsing (dispatch for call events)"""
    try:
        import subprocess
        from get_users_and_calls import get_rlog_sessions_direct
        
        date = request.args.get("date", "2026-02-08")
        use_dispatch = request.args.get("use_dispatch", "false").lower() == "true"
        logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "import_logs")
        
        if use_dispatch:
            port = 35000
            
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
            
            sessions = {}
            for line in result.stdout.strip().split("\n"):
                if line.strip() and "|" in line:
                    parts = line.strip().split("|")
                    if len(parts) >= 3:
                        object_id = parts[0].strip()
                        session_id = parts[1].strip()
                        create_date = parts[2].strip()
                        
                        # Only keep call sessions (session_*, not user_*)
                        if session_id and session_id.startswith("session_"):
                            sessions[session_id] = {
                                "id": session_id,
                                "object_id": object_id,
                                "type": "call_session",
                                "caller": "",
                                "called": "",
                                "create_date": create_date
                            }
            
            if sessions:
                return jsonify({
                    "success": True,
                    "date": date,
                    "sessions": sessions,
                    "using_dispatch": True
                })
            else:
                logger.warning("Dispatch returned empty sessions, falling back to direct parsing")
        
        # Use direct parsing which extracts caller/called from SIP URIs
        result = get_rlog_sessions_direct(logs_dir, date)
        sessions = result.get("sessions", {})
        
        # Filter to only call sessions (session_*, not user_*)
        call_sessions = {}
        for sid, info in sessions.items():
            if sid.startswith("session_"):
                call_sessions[sid] = info
        
        return jsonify({
            "success": True,
            "date": date,
            "sessions": call_sessions,
            "using_direct_parsing": True
        })
            
    except subprocess.TimeoutExpired:
        logger.warning("Dispatch query timed out, falling back to direct parsing")
        result = get_rlog_sessions_direct(logs_dir, date)
        sessions = result.get("sessions", {})
        call_sessions = {k: v for k, v in sessions.items() if k.startswith("session_")}
        return jsonify({
            "success": True,
            "date": date,
            "sessions": call_sessions,
            "using_direct_parsing": True,
            "dispatch_note": "DispatchTimeout"
        })
    except Exception as dispatch_error:
        logger.warning(f"Dispatch failed ({dispatch_error}), falling back to direct parsing")
        result = get_rlog_sessions_direct(logs_dir, date)
        sessions = result.get("sessions", {})
        call_sessions = {k: v for k, v in sessions.items() if k.startswith("session_")}
        return jsonify({
            "success": True,
            "date": date,
            "sessions": call_sessions,
            "using_direct_parsing": True
        })
            
    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/rlog/session/detail", methods=["GET"])
def api_rlog_session_detail():
    """Get detailed events for a specific session using dispatch (with fallback to direct)"""
    import subprocess
    
    session_id = request.args.get("session", "")
    date = request.args.get("date", "2026-02-08")
    use_direct = request.args.get("use_direct", "false").lower() == "true"
    
    if not session_id:
        return jsonify({"success": False, "error": "Session ID required"}), 400
    
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
        from get_users_and_calls import get_rlog_session_detail_direct
        
        logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "import_logs")
        
        if use_direct:
            result = get_rlog_session_detail_direct(logs_dir, session_id, date)
            
            if not result.get("success"):
                return jsonify(result), 404 if "not found" in result.get("error", "") else 500
            
            output_columns = []
            output_lines = []
            
            for event in result.get("events", []):
                output_columns.append({
                    "date": event.get("date", ""),
                    "source": event.get("source", ""),
                    "target": event.get("target", ""),
                    "state": event.get("state", ""),
                    "name": event.get("name", ""),
                    "data": event.get("data", "")
                })
                output_lines.append(f"{event.get('date', '')}   {event.get('source', '')}   {event.get('target', '')}   {event.get('state', '')}   {event.get('name', '')}   {event.get('data', '')}")
            
            return jsonify({
                "success": True,
                "session": session_id,
                "object_id": result.get("object_id", ""),
                "date": date,
                "running": True,
                "count": len(output_lines),
                "output": output_lines,
                "columns": output_columns,
                "using_direct_parsing": True,
                "note": "Mode direct parsing"
            })
        
        try:
            port = 35000
            
            # First, find the object_id for the session
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
                raise Exception(f"Session '{session_id}' not found")
            
            # Now get the events for this session
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
            
            if output_lines:
                return jsonify({
                    "success": True,
                    "session": session_id,
                    "object_id": object_id,
                    "date": date,
                    "running": True,
                    "count": len(output_lines),
                    "output": output_lines,
                    "columns": output_columns,
                    "using_dispatch": True
                })
            else:
                raise Exception("No events returned from dispatch")
            
        except subprocess.TimeoutExpired:
            logger.warning("Dispatch query timed out, falling back to direct parsing")
            result = get_rlog_session_detail_direct(logs_dir, session_id, date)
            
            if not result.get("success"):
                return jsonify(result), 404 if "not found" in result.get("error", "") else 500
            
            output_columns = []
            output_lines = []
            
            for event in result.get("events", []):
                output_columns.append({
                    "date": event.get("date", ""),
                    "source": event.get("source", ""),
                    "target": event.get("target", ""),
                    "state": event.get("state", ""),
                    "name": event.get("name", ""),
                    "data": event.get("data", "")
                })
                output_lines.append(f"{event.get('date', '')}   {event.get('source', '')}   {event.get('target', '')}   {event.get('state', '')}   {event.get('name', '')}   {event.get('data', '')}")
            
            return jsonify({
                "success": True,
                "session": session_id,
                "object_id": result.get("object_id", ""),
                "date": date,
                "running": True,
                "count": len(output_lines),
                "output": output_lines,
                "columns": output_columns,
                "using_direct_parsing": True,
                "dispatch_note": "DispatchTimeout"
            })
            
        except Exception as dispatch_error:
            logger.warning(f"Dispatch failed ({dispatch_error}), falling back to direct parsing")
            result = get_rlog_session_detail_direct(logs_dir, session_id, date)
            
            if not result.get("success"):
                return jsonify(result), 404 if "not found" in result.get("error", "") else 500
            
            output_columns = []
            output_lines = []
            
            for event in result.get("events", []):
                output_columns.append({
                    "date": event.get("date", ""),
                    "source": event.get("source", ""),
                    "target": event.get("target", ""),
                    "state": event.get("state", ""),
                    "name": event.get("name", ""),
                    "data": event.get("data", "")
                })
                output_lines.append(f"{event.get('date', '')}   {event.get('source', '')}   {event.get('target', '')}   {event.get('state', '')}   {event.get('name', '')}   {event.get('data', '')}")
            
            return jsonify({
                "success": True,
                "session": session_id,
                "object_id": result.get("object_id", ""),
                "date": date,
                "running": True,
                "count": len(output_lines),
                "output": output_lines,
                "columns": output_columns,
                "using_direct_parsing": True,
                "dispatch_error": str(dispatch_error)
            })
            
    except Exception as e:
        logger.error(f"RlogDispatcher error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)})


import uuid
import time
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
            "using_dispatch": True
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


@app.route("/api/protocol")
def api_protocol():
    """Get protocol specification"""
    return jsonify({
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
    })



if __name__ == "__main__":
    print("=" * 70)
    print("CCCP Explorer - Live Dashboard")
    print("=" * 70)

    print("Loading servers list from MySQL...")
    servers = get_servers_from_mysql()
    state.available_servers = {s["project"]: s for s in servers}
    print(f"Loaded {len(servers)} projects")

    print()
    print(f"Server running: http://{FLASK_CONFIG['host']}:{FLASK_CONFIG['port']}")
    print("  - Go to / for project selection")
    print("  - Go to /cst_explorer/PROJECT_NAME to access a project directly")
    print("=" * 70)

    app.run(host=FLASK_CONFIG["host"], port=FLASK_CONFIG["port"], debug=FLASK_CONFIG["debug"])
