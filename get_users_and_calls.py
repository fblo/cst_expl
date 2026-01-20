#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Script pour récupérer les utilisateurs actifs et les appels
# - Utilisateurs : avec noms réels, durée de connexion
# - Appels : triés par date descendante, avec numéro appelé

import subprocess
import json
import sys
from datetime import datetime, timedelta

DEFAULT_IP = "10.199.30.67"
DISPATCH_PORT = 20103


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


def get_user_real_names():
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
                DEFAULT_IP,
                str(DISPATCH_PORT),
                "-list",
                "-path",
                "/dispatch",
                "-field",
                "sessions",
                "-filter",
                ".[session_type eq 3 and terminate_date eq '']",
                "-fields",
                "row.object_id;row.user.name;row.user.login;row.current_mode;row.create_date;row.terminate_date",
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
            if len(parts) >= 6:
                object_id = parts[0]
                user_name = parts[1] if parts[1] != "undefined" else "-"
                login = parts[2] if parts[2] != "undefined" else "-"
                mode = parts[3] if parts[3] != "undefined" else "-"
                create_date = parts[4]
                terminate_date = parts[5]

                if object_id and object_id != "undefined":
                    start_dt = parse_french_datetime(create_date)
                    if start_dt:
                        duration_secs = int((datetime.now() - start_dt).total_seconds())
                        duration = format_duration_seconds(duration_secs)
                    else:
                        duration = "-"

                    users_map[object_id] = {
                        "object_id": object_id,
                        "user_name": user_name,
                        "login": login,
                        "mode": mode,
                        "position": "-",
                        "queue": "-",
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

        # Filtrer pour ne garder que les utilisateurs avec un vrai nom
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


def get_ccxml_sessions():
    """Récupère les sessions CCXML et les sépare en utilisateurs/appels"""
    cmd = [
        "/opt/consistent/bin/ccenter_report",
        "-login",
        "supervisor_stho",
        "-password",
        "toto",
        "-server",
        DEFAULT_IP,
        str(DISPATCH_PORT),
        "-list",
        "-path",
        "/ccxml",
        "-field",
        "sessions",
        "-fields",
        "row.object_id;row.session_id;row.create_date;row.terminate_date",
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


def get_dispatch_calls():
    """Récupère les détails des appels depuis dispatch"""
    cmd = [
        "/opt/consistent/bin/ccenter_report",
        "-login",
        "supervisor_stho",
        "-password",
        "toto",
        "-server",
        DEFAULT_IP,
        str(DISPATCH_PORT),
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


def get_all_data():
    """Récupère et combine toutes les données"""

    print("Récupération des utilisateurs...", file=sys.stderr)
    dispatch_users = get_user_real_names()

    print("Récupération des sessions CCXML...", file=sys.stderr)
    ccxml_users, ccxml_calls = get_ccxml_sessions()

    print("Récupération des détails dispatch...", file=sys.stderr)
    dispatch_calls = get_dispatch_calls()

    print(
        f"CCXML - Utilisateurs: {len(ccxml_users)}, Appels: {len(ccxml_calls)}",
        file=sys.stderr,
    )

    enriched_users = []
    for user in ccxml_users:
        obj_id = user.get("object_id", "")
        if obj_id in dispatch_users:
            disp_user = dispatch_users[obj_id]
            user["user_name"] = disp_user.get("user_name", "-")
            user["login"] = disp_user.get("login", "-")
            user["mode"] = disp_user.get("mode", "-")
            user["position"] = disp_user.get("position", "-")
            user["queue"] = disp_user.get("queue", "-")
            user["create_date"] = disp_user.get(
                "create_date", user.get("create_date", "-")
            )
            user["create_date_iso"] = disp_user.get(
                "create_date_iso", user.get("create_date_iso", "")
            )

            start_dt = parse_french_datetime(user.get("create_date", ""))
            if start_dt:
                terminate_date = user.get("terminate_date", "")
                if terminate_date and terminate_date != "undefined":
                    end_dt = parse_french_datetime(terminate_date)
                    duration_secs = int((end_dt - start_dt).total_seconds())
                else:
                    duration_secs = int((datetime.now() - start_dt).total_seconds())
                user["duration"] = format_duration_seconds(duration_secs)
                user["duration_seconds"] = duration_secs
                user["is_active"] = not terminate_date or terminate_date == "undefined"
            else:
                user["duration"] = "-"
                user["duration_seconds"] = 0
                user["is_active"] = True

        enriched_users.append(user)

    active_users = [
        u
        for u in enriched_users
        if u.get("is_active", True)
        and u.get("user_name")
        and u.get("user_name") != "-"
        and u.get("user_name") != "None"
    ]
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

    result = {
        "connected": True,
        "timestamp": datetime.now().isoformat(),
        "users": {
            "count": len(active_users),
            "active": active_users,
            "all": active_users,
        },
        "calls": {"count": len(ccxml_calls), "all": ccxml_calls},
    }

    print(
        f"Total - Utilisateurs actifs: {len(active_users)}, Appels: {len(ccxml_calls)}",
        file=sys.stderr,
    )

    return result


if __name__ == "__main__":
    result = get_all_data()
    print(json.dumps(result, indent=2, ensure_ascii=False))
