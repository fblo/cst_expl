#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Script pour récupérer les utilisateurs actifs et les appels
# - Utilisateurs : avec noms réels, durée de connexion
# - Appels : triés par date descendante, avec numéro appelé

import subprocess
import json
import sys
import argparse
from datetime import datetime

DEFAULT_IP = "10.199.30.67"
DISPATCH_PORT = 20103


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Fetch users and calls from CCCP server"
    )
    parser.add_argument(
        "--host", type=str, default=DEFAULT_IP, help="Server IP address"
    )
    parser.add_argument("--port", type=int, default=DISPATCH_PORT, help="Dispatch port")
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


def get_user_real_names(host=DEFAULT_IP, port=DISPATCH_PORT):
    """Récupère les vrais noms d'utilisateurs depuis dispatch avec tous les champs"""
    try:
        result = subprocess.run(
            [
                "/opt/consistent/bin/ccenter_report",
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


def get_ccxml_sessions(host=DEFAULT_IP, port=DISPATCH_PORT):
    """Récupère les sessions CCXML et les sépare en utilisateurs/appels"""
    cmd = [
        "/opt/consistent/bin/ccenter_report",
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


def get_dispatch_calls(host=DEFAULT_IP, port=DISPATCH_PORT):
    """Récupère les détails des appels depuis dispatch"""
    cmd = [
        "/opt/consistent/bin/ccenter_report",
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
        "-filter",
        ".[session_type eq 1]",
        "-fields",
        "row.session_id;row.object_id;row.create_date;row.terminate_date;row.queue_name;row.tasks.last.manager_user_id;row.connections.first.remote_address;row.connections.last.local_address",
        "-separator",
        "|",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        calls_map = {}
        for line in result.stdout.strip().split("\n"):
            if not line or "|" not in line:
                continue

            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 8:
                session_id = parts[0]
                object_id = parts[1]
                create_date = parts[2]
                terminate_date = parts[3]
                queue_name = parts[4]
                agent = parts[5]
                remote = parts[6]  # Caller (qui appelle)
                local = parts[7]  # Called (numéro appelé)

                if object_id == "undefined":
                    continue

                # Extract call_id from session_id
                call_id = (
                    session_id.split("@")[0].replace("session_", "")
                    if "@" in session_id
                    else ""
                )

                # Caller - who is calling
                caller = ""
                if remote and remote != "undefined":
                    caller = remote.replace("sip:", "").split("@")[0]

                # Called - the target number
                called = ""
                if local and local != "undefined":
                    called = local.replace("sip:", "").split("@")[0]

                # Calculate duration
                duration = "-"
                start_dt = parse_french_datetime(create_date)
                if start_dt and terminate_date and terminate_date != "undefined":
                    end_dt = parse_french_datetime(terminate_date)
                    if end_dt:
                        duration_secs = int((end_dt - start_dt).total_seconds())
                        duration = format_duration_seconds(duration_secs)

                calls_map[object_id] = {
                    "call_id": call_id,
                    "session_id": session_id,
                    "queue_name": queue_name
                    if queue_name and queue_name != "undefined"
                    else "-",
                    "agent": agent if agent and agent != "undefined" else "-",
                    "caller": caller,  # Qui appelle
                    "called": called,  # Numéro appelé
                    "duration": duration,
                    "create_date": create_date,
                    "create_date_iso": format_datetime_iso(start_dt),
                }
                print(
                    f"Appel {call_id}: caller={caller}, called={called}",
                    file=sys.stderr,
                )

        print(f"Total appels dispatch: {len(calls_map)}", file=sys.stderr)
        return calls_map

    except Exception as e:
        print(f"Erreur Dispatch: {e}", file=sys.stderr)

    return {}


def get_all_data(host=DEFAULT_IP, port=DISPATCH_PORT):
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
        obj_id = call.get("object_id", "")
        if obj_id in dispatch_calls:
            disp_data = dispatch_calls[obj_id]
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


def get_queue_statistics(active_users=None, host=DEFAULT_IP, port=DISPATCH_PORT):
    """Récupère les queues et leurs statistiques depuis dispatch"""

    queues_cmd = [
        "/opt/consistent/bin/ccenter_report",
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


if __name__ == "__main__":
    args = parse_arguments()
    host = args.host
    port = args.port

    result = get_all_data(host=host, port=port)
    print(json.dumps(result, indent=2, ensure_ascii=False))
