#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Script pour récupérer les utilisateurs actifs et les appels
# - Utilisateurs : avec noms réels, durée de connexion
# - Appels : triés par date descendante, avec numéro appelé

import subprocess
import json
import sys
import argparse
import os
import time
import glob
import re
import socket
import signal
from datetime import datetime
from typing import Optional, List, Dict, Any

from config import CCC_BIN

DEFAULT_IP = ""  # Default IP is now empty to allow initialization without server
DEFAULT_DISPATCH_PORT = 20103


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Fetch users and calls from CCCP server"
    )
    parser.add_argument(
        "--host", type=str, required=False, help="Server IP address"
    )
    parser.add_argument("--port", type=int, default=DEFAULT_DISPATCH_PORT, help="Dispatch port")
    return parser.parse_args()


def parse_french_datetime(date_str):
    """Parse datetime format and return datetime object"""
    if not date_str or date_str == "undefined" or date_str == "None":
        return None

    try:
        parts = date_str.split(" le ")
        if len(parts) == 2:
            time_part = parts[0]
            date_part = parts[1]
            dt = datetime.strptime(f"{date_part} {time_part}", "%d/%m/%Y %H:%M:%S")
            return dt
    except Exception:
        pass

    return None


def format_datetime_iso(dt):
    """Format datetime to 2026-01-19 10:00:00 format"""
    if dt:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return None


def format_duration_seconds(seconds):
    """Format duration in seconds to human readable"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins}m {secs}s"
    else:
        hours = seconds // 3600
        mins = (seconds % 3600) // 60
        return f"{hours}h {mins}m"


def parse_active_queues(active_queues):
    """Extract queue name from active_queues field"""
    if not active_queues or active_queues == "undefined" or active_queues == "":
        return "-"
    try:
        import re

        queue_match = re.search(r"queue:'([^']+)'", active_queues)
        if queue_match:
            queue_name = queue_match.group(1)
            if "__" in queue_name:
                return queue_name.split("__", 1)[1]
            return queue_name
    except Exception:
        pass
    return "-"


def parse_active_queues_state(active_queues):
    """Extract state (task) from active_queues field"""
    if not active_queues or active_queues == "undefined" or active_queues == "":
        return "-"
    try:
        import re

        task_match = re.search(r"task:'([^']+)'", active_queues)
        if task_match:
            task = task_match.group(1)
            return task.capitalize()
    except Exception:
        pass
    return "-"


def get_user_real_names(host=DEFAULT_IP, port=DEFAULT_DISPATCH_PORT):
    """Récupère les vrais noms d'utilisateurs depuis dispatch avec tous les champs"""
    # Ne pas exécuter si aucun hôte n'est spécifié
    if not host:
        print("Aucun hôte spécifié, skipping get_user_real_names", file=sys.stderr)
        return {}
        
    try:
        result = subprocess.run(
            [
                CCC_BIN["report"],
                "-login",
                "admin",
                "-password",
                "admin",
                "-server",
                host,
                str(port),
                "-list",
                "-path",
                "/dispatch",
                "-filter",
                ".[session_type eq 3 and terminate_date eq '']",
                "-field",
                "sessions",
                "-fields",
                "row.object_id;row.project_name;row.user.login;row.user.name;row.phone_contact_uri;row.login_date;row.profile_name;row.current_mode;row.states.last.display_name;row.session_id;row.session_type;row.create_date;row.terminate_date",
                "-separator",
                "|",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        users_map = {}
        for line in result.stdout.strip().split("\n"):
            if not line or "|" not in line:
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 14:
                object_id = parts[0] if parts[0] != "undefined" else "-"
                project_name = parts[1] if parts[1] != "undefined" else "-"
                login = parts[2] if parts[2] != "undefined" else "-"
                user_name = parts[3] if parts[3] != "undefined" else "-"
                phone_contact_uri = parts[4] if parts[4] != "undefined" else "-"
                login_date = parts[5]
                profile_name = (
                    parts[6] if len(parts) > 6 and parts[6] != "undefined" else "-"
                )
                current_mode = (
                    parts[7] if len(parts) > 7 and parts[7] != "undefined" else "-"
                )
                state_display_name = (
                    parts[8] if len(parts) > 8 and parts[8] != "undefined" else "-"
                )
                session_id = (
                    parts[9] if len(parts) > 9 and parts[9] != "undefined" else "-"
                )
                session_type = (
                    parts[10] if len(parts) > 10 and parts[10] != "undefined" else "-"
                )
                create_date = parts[11]
                terminate_date = parts[12]

                if login and login != "undefined":
                    start_dt = parse_french_datetime(login_date)
                    if start_dt:
                        duration_secs = int((datetime.now() - start_dt).total_seconds())
                        duration = format_duration_seconds(duration_secs)
                    else:
                        duration = "-"

                    users_map[login] = {
                        "login": login,
                        "object_id": object_id,
                        "user_name": user_name,
                        "project_name": project_name,
                        "phone_contact_uri": phone_contact_uri,
                        "profile_name": profile_name,
                        "mode": current_mode,
                        "state": state_display_name,
                        "session_id": session_id,
                        "session_type": session_type,
                        "login_date": login_date,
                        "create_date": create_date,
                        "create_date_iso": format_datetime_iso(start_dt)
                        if start_dt
                        else None,
                        "terminate_date": terminate_date,
                        "duration": duration,
                        "duration_seconds": int(
                            (datetime.now() - start_dt).total_seconds()
                        )
                        if start_dt
                        else 0,
                        "is_active": True,
                    }

        real_users_map = {
            k: v
            for k, v in users_map.items()
            if v.get("user_name")
            and v.get("user_name") != "-"
            and v.get("user_name") != "None"
        }

        print(
            f"Utilisateurs dispatch (réels): {len(real_users_map)}/{len(users_map)}",
            file=sys.stderr,
        )
        return real_users_map
    except Exception as e:
        print(f"Erreur noms utilisateurs: {e}", file=sys.stderr)
    return {}


def get_ccxml_sessions(host=DEFAULT_IP, port=DEFAULT_DISPATCH_PORT):
    """Récupère les sessions CCXML et les sépare en utilisateurs/appels"""
    # Ne pas exécuter si aucun hôte n'est spécifié
    if not host:
        print("Aucun hôte spécifié, skipping get_ccxml_sessions", file=sys.stderr)
        return [], []
        
    cmd = [
        CCC_BIN["report"],
        "-login",
        "supervisor_stho",
        "-password",
        "toto",
        "-server",
        host,
        str(port),
        "-list",
        "-path",
        "/ccxml",
        "-field",
        "sessions",
        "-fields",
        "row.object_id;row.session_id;row.create_date;row.terminate_date;row.active_queues",
        "-separator",
        "|",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        users = []
        calls = []

        for line in result.stdout.strip().split("\n"):
            if not line or "|" not in line:
                continue

            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 4:
                object_id = parts[0]
                session_id = parts[1]
                create_date = parts[2]
                terminate_date = parts[3]
                active_queues = parts[4]

                if not object_id or object_id == "undefined":
                    continue

                base_name = (
                    session_id.split("@")[0] if "@" in session_id else session_id
                )

                if base_name.startswith("user_"):
                    users.append(
                        {
                            "object_id": object_id,
                            "session_id": session_id,
                            "user_id": base_name,
                            "create_date": create_date,
                            "terminate_date": terminate_date,
                            "active_queues": active_queues,
                        }
                    )

                elif base_name.startswith("session_"):
                    calls.append(
                        {
                            "object_id": object_id,
                            "session_id": session_id,
                            "call_id": base_name.replace("session_", ""),
                            "create_date": create_date,
                            "terminate_date": terminate_date,
                            "duration": "-",
                            "duration_seconds": 0,
                            "is_active": not terminate_date
                            or terminate_date == "undefined",
                        }
                    )

        return users, calls

    except Exception as e:
        print(f"Erreur CCXML: {e}", file=sys.stderr)

    return [], []


def get_dispatch_calls(host=DEFAULT_IP, port=DEFAULT_DISPATCH_PORT):
    """Récupère les détails des appels depuis dispatch (TOUTES les sessions)"""
    # Ne pas exécuter si aucun hôte n'est spécifié
    if not host:
        print("Aucun hôte spécifié, skipping get_dispatch_calls", file=sys.stderr)
        return {}
        
    cmd = [
        CCC_BIN["report"],
        "-login",
        "supervisor_stho",
        "-password",
        "toto",
        "-server",
        host,
        str(port),
        "-list",
        "-path",
        "/dispatch",
        "-field",
        "sessions",
        "-fields",
        "row.session_id;row.object_id;row.create_date;row.terminate_date;row.session_type;row.queue_name;row.tasks.last.queue_name;row.tasks.last.manager_user_id;row.connections.first.remote_address;row.connections.last.local_address",
        "-separator",
        "|",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        session_to_info = {}
        for line in result.stdout.strip().split("\n"):
            if not line or "|" not in line:
                continue

            parts = [p.strip() for p in line.split("|")]

            if len(parts) >= 10:
                session_id = parts[0]
                object_id = parts[1]
                create_date = parts[2]
                terminate_date = parts[3]
                session_type = parts[4]
                queue_name = parts[5] if parts[5] != "undefined" else ""
                queue_name_alt = (
                    parts[6] if len(parts) > 6 and parts[6] != "undefined" else ""
                )
                agent = parts[7] if len(parts) > 7 and parts[7] != "undefined" else ""
                remote = parts[8] if len(parts) > 8 else ""
                local = parts[9] if len(parts) > 9 else ""

                if not queue_name:
                    queue_name = queue_name_alt

                if object_id == "undefined" or not object_id:
                    continue

                caller = ""
                if remote and remote != "undefined":
                    caller = remote.replace("sip:", "").split("@")[0]

                called = ""
                if local and local != "undefined":
                    called = local.replace("sip:", "").split("@")[0]

                duration = "-"
                start_dt = parse_french_datetime(create_date)
                if start_dt and terminate_date and terminate_date != "undefined":
                    end_dt = parse_french_datetime(terminate_date)
                    if end_dt:
                        duration_secs = int((end_dt - start_dt).total_seconds())
                        duration = format_duration_seconds(duration_secs)

                session_to_info[session_id] = {
                    "object_id": object_id,
                    "session_type": session_type,
                    "queue_name": queue_name if queue_name else "-",
                    "agent": agent if agent else "-",
                    "caller": caller,
                    "called": called,
                    "duration": duration,
                    "create_date": create_date,
                    "create_date_iso": format_datetime_iso(start_dt),
                }

        return session_to_info

    except Exception as e:
        print(f"Erreur Dispatch: {e}", file=sys.stderr)

    return {}


def get_all_data(host=DEFAULT_IP, port=DEFAULT_DISPATCH_PORT):
    """Récupère et combine toutes les données"""

    print("Récupération des utilisateurs...", file=sys.stderr)
    dispatch_users = get_user_real_names(host=host, port=port)

    print("Récupération des sessions CCXML...", file=sys.stderr)
    ccxml_users, ccxml_calls = get_ccxml_sessions(host=host, port=port)

    print("Récupération des détails dispatch...", file=sys.stderr)
    dispatch_calls = get_dispatch_calls(host=host, port=port)

    print(
        f"CCXML - Utilisateurs: {len(ccxml_users)}, Appels: {len(ccxml_calls)}",
        file=sys.stderr,
    )

    ccxml_object_to_queues = {}
    for ccxml_user in ccxml_users:
        obj_id = ccxml_user.get("object_id", "")
        if obj_id and ccxml_user.get("active_queues"):
            ccxml_object_to_queues[obj_id] = ccxml_user.get("active_queues", "")

    active_users = []

    for login, disp_user in dispatch_users.items():
        user = {
            "login": login,
            "object_id": disp_user.get("object_id", "-"),
            "user_name": disp_user.get("user_name", "-"),
            "project_name": disp_user.get("project_name", "-"),
            "phone_contact_uri": disp_user.get("phone_contact_uri", "-"),
            "profile_name": disp_user.get("profile_name", "-"),
            "mode": disp_user.get("mode", "-"),
            "state": disp_user.get("state", "-"),
            "session_id": disp_user.get("session_id", "-"),
            "session_type": disp_user.get("session_type", "-"),
            "queue": "-",
            "create_date": disp_user.get("create_date", "-"),
            "create_date_iso": disp_user.get("create_date_iso", "-"),
            "duration": disp_user.get("duration", "-"),
            "duration_seconds": disp_user.get("duration_seconds", 0),
            "is_active": disp_user.get("is_active", True),
        }

        active_queues = ccxml_object_to_queues.get(disp_user.get("object_id", ""), "")
        if active_queues and active_queues != "undefined":
            user["active_queues"] = active_queues
            user["queue"] = parse_active_queues(active_queues)
            # Set queue to "-" if user is in unplug mode
            if "unplug" in (disp_user.get("mode", "").lower()):
                user["queue"] = "-"

        active_users.append(user)

    active_users.sort(key=lambda x: x.get("duration_seconds", 0), reverse=True)

    for call in ccxml_calls:
        session_id = call.get("session_id", "")
        if session_id in dispatch_calls:
            disp_data = dispatch_calls[session_id]
            call["object_id"] = disp_data.get("object_id", call.get("object_id", ""))
            call["queue_name"] = disp_data.get("queue_name", "-")
            call["agent"] = disp_data.get("agent", "-")
            call["caller"] = disp_data.get("caller", "-")
            call["called"] = disp_data.get("called", "-")
            call["duration"] = disp_data.get("duration", "-")
            call["create_date"] = disp_data.get(
                "create_date", call.get("create_date", "")
            )
            call["create_date_iso"] = disp_data.get(
                "create_date_iso", call.get("create_date_iso", "")
            )

    ccxml_calls.sort(key=lambda x: x.get("create_date_iso", ""), reverse=True)

    queues = get_queue_statistics(active_users, host=host, port=port)

    result = {
        "connected": True,
        "timestamp": datetime.now().isoformat(),
        "users": {
            "count": len(active_users),
            "active": active_users,
            "all": active_users,
        },
        "calls": {"count": len(ccxml_calls), "all": ccxml_calls},
        "queues": {"count": len(queues), "all": queues},
    }

    print(
        f"Total - Utilisateurs actifs: {len(active_users)}, Appels: {len(ccxml_calls)}, Queues: {len(queues)}",
        file=sys.stderr,
    )

    return result


def get_queue_statistics(active_users=None, host=DEFAULT_IP, port=DEFAULT_DISPATCH_PORT):
    """Récupère les queues et leurs statistiques depuis dispatch"""
    
    # Ne pas exécuter si aucun hôte n'est spécifié
    if not host:
        print("Aucun hôte spécifié, skipping get_queue_statistics", file=sys.stderr)
        return []
        
    queues_cmd = [
        CCC_BIN["report"],
        "-login",
        "admin",
        "-password",
        "admin",
        "-server",
        host,
        str(port),
        "-list",
        "-path",
        "/dispatch",
        "-field",
        "queues",
        "-fields",
        "row.object_id;row.name;row.queue_type;row.display_name;row.priority;row.logged;row.working;row.waiting",
        "-separator",
        "|",
    ]

    def clean_queue_name(name):
        """Remove everything before '__' and the double underscore"""
        if "__" in name:
            return name.split("__", 1)[1]
        return name

    try:
        queues_result = subprocess.run(
            queues_cmd, capture_output=True, text=True, timeout=30
        )

        queues = []

        for line in queues_result.stdout.strip().split("\n"):
            if not line or "|" not in line:
                continue

            parts = line.split("|")
            if len(parts) >= 8:
                object_id = parts[0].strip() if parts[0] else ""
                name = parts[1].strip() if len(parts) > 1 and parts[1] else ""
                queue_type = parts[2].strip() if len(parts) > 2 and parts[2] else ""
                display_name = parts[3].strip() if len(parts) > 3 and parts[3] else ""
                priority = parts[4].strip() if len(parts) > 4 and parts[4] else ""
                _logged = parts[5].strip() if len(parts) > 5 and parts[5] else ""
                working = parts[6].strip() if len(parts) > 6 and parts[6] else ""
                waiting = parts[7].strip() if len(parts) > 7 and parts[7] else ""

                if not name or name == "undefined":
                    continue

                # Skip VQ_ prefixed queues and user-type entries
                if name.startswith("VQ_"):
                    continue
                if queue_type == "user":
                    continue

                clean_name = clean_queue_name(name)

                logged_count = 0
                if active_users:
                    logged_count = sum(
                        1
                        for u in active_users
                        if u.get("queue", "") == clean_name
                        and "unplug" not in (u.get("mode", "").lower())
                    )

                queues.append(
                    {
                        "name": clean_name,
                        "object_id": object_id,
                        "type": queue_type
                        if queue_type and queue_type != "undefined"
                        else "queue",
                        "display_name": display_name
                        if display_name and display_name != "undefined"
                        else clean_name,
                        "priority": priority
                        if priority and priority != "undefined"
                        else "-",
                        "logged": logged_count,
                        "working": int(working) if working and working.isdigit() else 0,
                        "waiting": int(waiting) if waiting and waiting.isdigit() else 0,
                    }
                )

        print(
            f"Queues recuperees: {len(queues)}",
            file=sys.stderr,
        )
        return queues

    except Exception as e:
        print(f"Erreur recuperation queues: {e}", file=sys.stderr)
    return []


class RlogDispatcher:
    """Gère un dispatch local pour charger et interroger des logs RLOG"""
    
    DISPATCH_BIN = CCC_BIN["dispatch"]
    UPDATE_BIN = CCC_BIN["update"]
    BASE_PORT = 35000
    PORT_RANGE = 200
    
    _instance = None
    _logs_dir = None
    
    def __new__(cls, logs_dir: str = None):
        if cls._instance is not None and (logs_dir is None or logs_dir == cls._logs_dir):
            return cls._instance
        
        instance = super().__new__(cls)
        instance._initialized = False
        return instance
    
    def __init__(self, logs_dir: str = None):
        if self._initialized and logs_dir == self._logs_dir:
            return
        
        self.logs_dir = logs_dir or self._logs_dir or "/opt/debug"
        self._logs_dir = self.logs_dir
        self.port: Optional[int] = None
        self.process: Optional[subprocess.Popen] = None
        self._loaded_days: set = set()
        self._last_activity: float = time.time()
        self._initialized = True
        
    @classmethod
    def reset(cls):
        """Reset singleton for testing"""
        if cls._instance and cls._instance.process:
            cls._instance.stop()
        cls._instance = None
        cls._logs_dir = None
    
    @classmethod
    def get_instance(cls, logs_dir: str = None) -> 'RlogDispatcher':
        """Get or create singleton instance"""
        if cls._instance is None:
            cls._instance = cls(logs_dir)
            cls._logs_dir = logs_dir
        return cls._instance
    
    def find_available_port(self) -> int:
        """Trouve un port disponible dans la plage spécifiée"""
        import socket
        netstat_output = subprocess.run(["netstat", "-nlt"], capture_output=True, text=True).stdout
        
        for i in range(self.BASE_PORT, self.BASE_PORT + self.PORT_RANGE):
            if f":{i}" not in netstat_output:
                return i
        raise RuntimeError(f"Aucun port disponible dans la plage {self.BASE_PORT}-{self.BASE_PORT + self.PORT_RANGE}")
    
    def find_log_directories(self) -> List[str]:
        """Trouve les répertoires contenant des fichiers de logs"""
        # First try Logger structure
        logger_pattern = os.path.join(self.logs_dir, "**/log_*.log")
        log_files = glob.glob(logger_pattern, recursive=True)
        if log_files:
            return [self.logs_dir]
        
        # Fall back to import_logs root
        import_logs = os.path.join(self.logs_dir, "import_logs")
        if os.path.exists(import_logs):
            log_files = glob.glob(os.path.join(import_logs, "*.log"))
            if log_files:
                return [import_logs]
        
        log_files = glob.glob(os.path.join(self.logs_dir, "*.log"))
        if log_files:
            return [self.logs_dir]
        return []
    
    def create_logger_structure(self, project: str = "ARTELIA", hostname: str = "ps-ics-prd-cst-fr-529") -> str:
        """Crée la structure Logger/PROJECT/_/ccenter_ccxml/Ccxml/HOSTNAME à partir de import_logs"""
        import_logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "import_logs")

        # Return the specific project path for dispatch (only this project's logs)
        project_logger_dir = os.path.join(self.logs_dir, "Logger", project, "_", "ccenter_ccxml", "Ccxml", hostname)

        # Check if this specific project path exists and has log files
        if os.path.exists(project_logger_dir):
            log_files = glob.glob(os.path.join(project_logger_dir, "log_*.log"))
            if log_files:
                print(f"✅ Trouvé {len(log_files)} fichiers logs pour {project} dans {project_logger_dir}", file=sys.stderr)
                return project_logger_dir

        # Create structure and copy logs
        os.makedirs(project_logger_dir, exist_ok=True)

        # Copy log files from import_logs (flat directory)
        log_files = glob.glob(os.path.join(import_logs_dir, "log_*.log"))
        for log_file in log_files:
            try:
                import shutil
                shutil.copy(log_file, project_logger_dir)
            except Exception as e:
                print(f"Warning: Could not copy {log_file}: {e}", file=sys.stderr)

        print(f"✅ Copié {len(log_files)} fichiers logs vers {project_logger_dir}", file=sys.stderr)
        return project_logger_dir
    
    def get_logs_path(self) -> str:
        """Retourne le chemin des logs pour le dispatch"""
        # Check if Logger structure exists
        logger_pattern = os.path.join(self.logs_dir, "**/log_*.log")
        log_files = glob.glob(logger_pattern, recursive=True)
        if log_files:
            return self.logs_dir
        
        # Check import_logs directory
        import_logs = os.path.join(self.logs_dir, "import_logs")
        log_files = glob.glob(os.path.join(import_logs, "*.log"))
        if log_files:
            return import_logs
        
        # Create Logger structure if needed
        return self.create_logger_structure()
    
    def launch(self, timeout: int = 30) -> int:
        """Lance le dispatch en mode slave avec gestion du timeout (2h)"""
        
        INACTIVITY_TIMEOUT = 2 * 60 * 60  # 2 hours in seconds
        
        if self.process is not None:
            if self.process.poll() is not None:
                self.process = None
                self.port = None
            else:
                if time.time() - self._last_activity > INACTIVITY_TIMEOUT:
                    print(f"🛑 Dispatch inactif depuis plus de 2h, arrêt...", file=sys.stderr)
                    self.stop()
                else:
                    return self.port
        
        # Try to find an existing dispatch or start a new one
        import socket
        
        for port in range(self.BASE_PORT, self.BASE_PORT + self.PORT_RANGE):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex(('127.0.0.1', port))
                sock.close()
                
                if result == 0:
                    self.port = port
                    self.process = None  # External dispatch, no subprocess to manage
                    self._last_activity = time.time()
                    print(f"✅ Utilise dispatch existant sur port {port}", file=sys.stderr)
                    return port
            except:
                pass
        
        # No existing dispatch found, start a new one
        self.port = self.find_available_port()
        
        logs_path = self.create_logger_structure()
        
        if not logs_path:
            raise RuntimeError(f"Aucun fichier .log trouvé dans {self.logs_dir}")
        
        print(f"🚀 Dispatch sur port {self.port} avec logs: {logs_path}", file=sys.stderr)
        
        env = os.environ.copy()
        env["PATH"] = env.get("PATH", "") + ":/opt/lampp/bin"
        
        interface_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debug_interface.xml")
        if not os.path.exists(interface_path):
            interface_path = os.path.join(self.logs_dir, "debug_interface.xml")
        
        cmd = [
            self.DISPATCH_BIN,
            "-slave", str(self.port),
            "-logs", logs_path,
            "-interface", interface_path,
            "-stderr"
        ]
        
        self.process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        
        time.sleep(timeout)
        
        if self.process.poll() is not None:
            stderr = self.process.stderr.read().decode() if self.process.stderr else ""
            raise RuntimeError(f"Dispatch arrêté: {stderr}")
        
        self._last_activity = time.time()
        RlogDispatcher._instance = self
        print(f"✅ Dispatch prêt sur 127.0.0.1:{self.port}", file=sys.stderr)
        return self.port
        
    def _calculate_days(self) -> List[str]:
        """Calcule les jours disponibles dans les logs"""
        days = set()
        
        log_files = glob.glob(os.path.join(self.logs_dir, "**/log_*.log"), recursive=True)
        
        for f in log_files:
            match = re.search(r'log_(\d{4}_\d{2}_\d{2})', os.path.basename(f))
            if match:
                day = match.group(1).replace("_", "-")
                days.add(day)
        
        return sorted(days)
    
    def query(self, query_type: str, **kwargs) -> Dict[str, Any]:
        """Exécute une requête sur le dispatch"""
        if not self.port or not self.process:
            self.launch()
        
        # Update activity timestamp
        self._last_activity = time.time()
        
        # Lazy load le jour demandé
        day = kwargs.get("date", "").replace("-", "_")
        if day and day not in self._loaded_days:
            self._load_day(day)
            self._loaded_days.add(day)
        
        cmd = [
            CCC_BIN["report"],
            "-login", kwargs.get("login", "admin"),
            "-password", kwargs.get("password", "admin"),
            "-server", "127.0.0.1",
            str(self.port),
            "-list"
        ]
        
        if query_type == "sessions":
            cmd.extend([
                "-path", "/ccxml",
                "-field", "sessions",
                "-fields", "row.object_id;row.session_id;row.create_date;row.terminate_date;row.active_queues"
            ])
        elif query_type == "session_events":
            cmd.extend([
                "-path", "/dispatch",
                "-field", "events",
                "-fields", "row.date;row.source;row.target;row.state;row.name;row.string_data",
                "-filter", f"row.session_id eq '{kwargs.get('session_id', '')}'"
            ])
        elif query_type == "session_detail":
            cmd.extend([
                "-path", "/dispatch",
                "-field", kwargs.get("field", "events"),
                "-fields", "row.date;row.source;row.target;row.state;row.name;row.string_data",
                "-object", kwargs.get("object_id", "")
            ])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                encoding="latin-1",
                errors="replace",
                timeout=kwargs.get("timeout", 5)
            )
            
            return {
                "success": True,
                "port": self.port,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Timeout lors de la requête",
                "timed_out": True
            }
    
    def _load_day(self, day: str):
        """Charge un jour spécifique dans le dispatch"""
        print(f"  → Chargement {day.replace('_', '-')}...", file=sys.stderr)
        try:
            subprocess.run(
                [
                    self.UPDATE_BIN,
                    "-login", "admin",
                    "-password", "admin",
                    "-server", "127.0.0.1",
                    str(self.port),
                    "-event", f"com.consistent.ccenter.dispatch.load_day.{day}"
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=10
            )
        except subprocess.TimeoutExpired:
            print(f"  ⚠️ Timeout lors du chargement de {day}", file=sys.stderr)
    
    def stop(self):
        """Arrête le dispatch"""
        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                self.process.wait(timeout=5)
                print(f"🛑 Dispatch arrêté", file=sys.stderr)
            except Exception as e:
                print(f"⚠️ Erreur lors de l'arrêt du dispatch: {e}", file=sys.stderr)
                try:
                    self.process.kill()
                except:
                    pass
        
        self.port = None
        self.process = None
        RlogDispatcher._instance = None


def parse_rlog_file(log_file: str, target_session: str = None) -> List[Dict[str, Any]]:
    """Parse un fichier log binaire et extraie TOUS les événements de session"""
    events = []
    seen_events = set()  # Pour éliminer les duplicatas
    
    if not os.path.exists(log_file):
        return events
    
    with open(log_file, 'rb') as f:
        content = f.read()
    
    content_str = content.decode('latin-1', errors='replace')
    
    # Event types to look for
    event_types = [
        ('connection.alerting', 'connection', 'alerting'),
        ('connection.connected', 'connection', 'connected'),
        ('connection.disconnected', 'connection', 'disconnected'),
        ('connection.accepted', 'connection', 'accepted'),
        ('dialog.joined', 'dialog', 'joined'),
        ('dialog.unjoined', 'dialog', 'unjoined'),
        ('dialog.created', 'dialog', 'created'),
        ('dialog.terminated', 'dialog', 'terminated'),
        ('conference.joined', 'conference', 'joined'),
        ('conference.unjoined', 'conference', 'unjoined'),
        ('conference.created', 'conference', 'created'),
        ('conference.terminated', 'conference', 'terminated'),
    ]
    
    # Find all positions with timestamp
    timestamp_positions = []
    for m in re.finditer(r'(\d{2}:\d{2}:\d{2}) le (\d{2}/\d{2}/\d{4})', content_str):
        timestamp_positions.append((m.start(), m.group(1), m.group(2)))
    
    if not timestamp_positions:
        return events
    
    # Process ALL event occurrences for each event type
    for event_type, event_name, event_state in event_types:
        # Find ALL occurrences of this event type
        for event_match in re.finditer(event_type, content_str):
            event_pos = event_match.start()
            
            # Find the nearest timestamp before this event
            nearest_ts = None
            for ts_pos, ts_time, ts_date in reversed(timestamp_positions):
                if ts_pos < event_pos:
                    nearest_ts = (ts_time, ts_date, ts_pos)
                    break
            
            if not nearest_ts:
                continue
            
            ts_time, ts_date, ts_pos = nearest_ts
            
            # Get context around this event
            context_start = max(0, ts_pos - 1000)
            context_end = min(len(content_str), event_pos + 500)
            context = content_str[context_start:context_end]
            
            # Check if session is in this context
            if target_session and target_session not in context:
                continue
            
            # Extract phone numbers from context
            phones = []
            sip_matches = re.findall(r'sip:(\d{10,})@', context)
            phones.extend(sip_matches)
            tel_matches = re.findall(r'tel:(\d{10,})', context)
            phones.extend(tel_matches)
            
            # Try to extract remote and local from JSON-like data
            remote_match = re.search(r'"remote":\s*"([^"]+)"', context)
            local_match = re.search(r'"local":\s*"([^"]+)"', context)
            
            remote = remote_match.group(1) if remote_match else ""
            local = local_match.group(1) if local_match else ""
            
            # Extract phone numbers from remote/local
            if remote:
                phone_match = re.search(r'(\d{6,})', remote)
                if phone_match:
                    phones.insert(0, phone_match.group(1))
            if local:
                local_phone_match = re.search(r'(\d{6,})', local)
                if local_phone_match:
                    phones.insert(0, local_phone_match.group(1))
            
            # Extract user info
            user_match = re.search(r'user[_\s]*(\d+)', context)
            
            # Build target - prefer local (called party) from SIP URI
            target = ""
            if local:
                local_phone = re.search(r'(\d{6,})', local)
                if local_phone:
                    target = local_phone.group(1)
            if not target and phones:
                target = phones[0]
            
            # Build source
            source = target_session or ""
            if user_match:
                source = f"{source} [{user_match.group(1)}]"
            
            # Check for duplicates
            event_key = (ts_time, event_state, target)
            if event_key in seen_events:
                continue
            seen_events.add(event_key)
            
            events.append({
                'date': ts_time,
                'timestamp': ts_date,
                'source': source,
                'target': target,
                'state': event_state,
                'name': event_type,
                'data': '',
                '_phones': list(set(phones))[:5],
                '_users': [user_match.group(1)] if user_match else [],
                '_remote': remote,
                '_local': local,
            })
    
    # Also look for session activity with customer data
    json_pattern = r'"CUSTOMER_ACTIVITY"[^}]+\}'
    for json_match in re.finditer(json_pattern, content_str):
        json_data = json_match.group(0)
        if not target_session or target_session in json_data:
            try:
                caller_match = re.search(r'"caller":"(\d+)"', json_data)
                called_match = re.search(r'"called":"(\d+)"', json_data)
                type_match = re.search(r'"type":"(\w+)"', json_data)
                duration_match = re.search(r'"globalDuration":(\d+)', json_data)
                
                events.append({
                    'date': '',
                    'source': caller_match.group(1) if caller_match else '',
                    'target': called_match.group(1) if called_match else '',
                    'state': 'activity',
                    'name': type_match.group(1) if type_match else 'call',
                    'data': json_data[:200],
                    'duration': duration_match.group(1) if duration_match else ''
                })
            except:
                pass
    
    return events


def find_session_in_logs(logs_dir: str, session_id: str, date: str = None) -> Optional[str]:
    """Trouve le fichier log contenant une session"""
    date_pattern = date.replace('-', '_') if date else None
    
    log_files = glob.glob(os.path.join(logs_dir, "**/log_*.log"), recursive=True)
    
    for log_file in sorted(log_files):
        filename = os.path.basename(log_file)
        
        if date_pattern and date_pattern not in filename:
            continue
            
        with open(log_file, 'rb') as f:
            if session_id.encode('latin-1') in f.read(500000):
                return log_file
    
    return None


def get_rlog_session_detail_direct(logs_dir: str, session_id: str, date: str = None) -> Dict[str, Any]:
    """Récupère les détails d'une session directement depuis les fichiers log (sans dispatch)"""
    log_file = find_session_in_logs(logs_dir, session_id, date)
    
    if not log_file:
        return {
            "success": False,
            "error": f"Session '{session_id}' non trouvée pour la date {date}"
        }
    
    events = parse_rlog_file(log_file, session_id)
    
    if not events:
        return {
            "success": False,
            "error": "Aucun événement trouvé pour cette session"
        }
    
    # Enhance events with better formatting
    enhanced_events = []
    for event in events:
        phones = event.get("_phones", [])
        users = event.get("_users", [])
        
        # Format source with user info if available
        source = event.get("source", "")
        if users and source.startswith("session_"):
            source = f"{source} [{', '.join(users)}]"
        
        # Format target with phone info if available
        target = event.get("target", "")
        if phones:
            phones_str = ", ".join(phones)
            if target:
                target = f"{target} ({phones_str})"
            else:
                target = phones_str
        
        enhanced_event = {
            "date": event.get("date", ""),
            "source": source,
            "target": target,
            "state": event.get("state", ""),
            "name": event.get("name", ""),
            "data": event.get("data", ""),
            "phones": phones,
            "users": users,
            "dialogs": event.get("_dialogs", []),
        }
        enhanced_events.append(enhanced_event)
    
    return {
        "success": True,
        "session": session_id,
        "log_file": log_file,
        "count": len(enhanced_events),
        "events": enhanced_events,
        "output": [f"{e['date']} | {e['source']} | {e['target']} | {e['state']} | {e['name']}" for e in enhanced_events],
        "columns": enhanced_events
    }


def get_rlog_sessions_direct(logs_dir: str, date: str = None) -> Dict[str, Any]:
    """Récupère toutes les sessions depuis les fichiers log (sans dispatch)"""
    sessions = {}
    
    # Use all log files recursively
    log_files = sorted(glob.glob(os.path.join(logs_dir, '**', 'log_*.log'), recursive=True))
    
    for log_file in log_files:
        filename = os.path.basename(log_file)
        
        if date and date.replace('-', '_') not in filename:
            continue
        
        try:
            with open(log_file, 'rb') as f:
                content = f.read()
            
            # Find all session_ patterns
            pattern = b"session_"
            for match in re.finditer(pattern, content):
                start = match.start()
                
                # Find the end (null byte or non-printable)
                end = start
                while end < len(content) and content[end] > 32 and content[end] < 127:
                    end += 1
                
                if end > start:
                    session_id = content[start:end].decode('utf-8', errors='replace')
                    
                    # Extract clean session ID - format: session_N@X.Y.Z.Ccxml.HOSTNAME
                    # Must end EXACTLY with ps-ics-prd-cst-fr-529 (no suffix)
                    valid_hostname = 'ps-ics-prd-cst-fr-529'
                    
                    if session_id.endswith(valid_hostname):
                        # This is a clean session ID
                        if session_id not in sessions:
                            sessions[session_id] = {
                                "id": session_id,
                                "object_id": str(hash(session_id) % 1000000),
                                "type": "call_session",
                                "caller": "",
                                "called": ""
                            }
                            
                            # Extract caller and called from the context around this session
                            context_start = max(0, start - 3000)
                            context_end = min(len(content), start + 3000)
                            context = content[context_start:context_end].decode('latin-1', errors='replace')
                            
                            # Look for SIP phone patterns: sip:0612046899@
                            sip_pattern = r'sip:(\d{10,})@'
                            sip_matches = re.findall(sip_pattern, context)
                            
                            # Look for tel: phone patterns: tel:0033157329750
                            tel_pattern = r'tel:(\d{10,})'
                            tel_matches = re.findall(tel_pattern, context)
                            
                            # Filter and assign caller/called
                            all_phones = sip_matches + tel_matches
                            if len(all_phones) >= 2:
                                # First phone is typically caller, second is called
                                sessions[session_id]["caller"] = all_phones[0]
                                sessions[session_id]["called"] = all_phones[1]
                            elif len(all_phones) == 1:
                                # Only one phone found - might be caller
                                sessions[session_id]["caller"] = all_phones[0]
        except Exception as e:
            print(f"Error reading {log_file}: {e}", file=sys.stderr)
    
    return {
        "success": True,
        "date": date,
        "sessions": sessions
    }


def load_rlog_session_detail(session_id: str, logs_dir: str) -> Dict[str, Any]:
    """Charge les logs et récupère les détails d'une session"""
    dispatcher = RlogDispatcher(logs_dir)
    
    try:
        port = dispatcher.launch()
        
        result = dispatcher.query("sessions")
        
        object_id = None
        for line in result.get("stdout", "").split("\n"):
            if session_id in line and "|" in line:
                parts = line.strip().split("|")
                if len(parts) >= 2 and parts[0].isdigit():
                    object_id = parts[0]
                    break
        
        if not object_id:
            return {
                "success": False,
                "error": f"Session '{session_id}' non trouvée"
            }
        
        events_result = dispatcher.query("session_detail", object_id=object_id)
        
        events_result["session_id"] = session_id
        events_result["object_id"] = object_id
        
        return events_result
        
    finally:
        dispatcher.stop()


def show_help_and_exit():
    """Affiche l'aide et quitte le programme"""
    parser = argparse.ArgumentParser(
        description="Fetch users and calls from CCCP server"
    )
    parser.add_argument(
        "--host", type=str, required=False, help="Server IP address"
    )
    parser.add_argument("--port", type=int, default=DEFAULT_DISPATCH_PORT, help="Dispatch port")
    parser.print_help()
    sys.exit(1)

if __name__ == "__main__":
    import sys
    
    # Si aucun argument n'est fourni (ou seulement -h/--help), afficher l'aide
    if len(sys.argv) == 1:
        show_help_and_exit()
    
    args = parse_arguments()
    host = args.host
    port = args.port

    # Si aucun host n'est fourni, afficher l'aide
    if not host:
        show_help_and_exit()

    result = get_all_data(host=host, port=port)
    print(json.dumps(result, indent=2, ensure_ascii=False))
