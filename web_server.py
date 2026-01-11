#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Serveur web temps reel pour le monitoring CCCP
# Lit les donnees depuis un fichier partage et utilise Server-Sent Events

import sys
import json
import os
import time
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify, Response

# Configuration
DEFAULT_IP = "10.199.30.67"
DEFAULT_PORT = 5000
DATA_FILE = "/tmp/cccp_monitoring.json"

app = Flask(__name__)

# Donnees en cache
cached_data = {
    "ip": DEFAULT_IP,
    "connected": False,
    "last_update": None,
    "queues": [],
    "users": [],
    "sessions": [],
    "outbound_sessions": [],
    "ccxml_events": [],
    "errors": [],
}


def read_shared_data():
    """Lire les donnees depuis le fichier partage"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"Erreur lecture: {e}")
    return cached_data


def generate_sse_data():
    """Generer les donnees pour Server-Sent Events"""
    data = read_shared_data()
    yield f"data: {json.dumps(data)}\n\n"


@app.route("/")
def index():
    return render_template(
        "dashboard.html",
        ip=cached_data["ip"],
        title="CCCP Monitor - %s" % cached_data["ip"],
    )


@app.route("/sse")
def sse():
    """Stream Server-Sent Events pour temps reel"""

    def generate():
        while True:
            data = read_shared_data()
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(1)

    return Response(generate(), mimetype="text/event-stream")


@app.route("/api/status")
def api_status():
    data = read_shared_data()
    return jsonify(
        {
            "ip": data["ip"],
            "connected": data["connected"],
            "version": data.get("version"),
            "last_update": data["last_update"],
            "projects_count": len(data.get("projects", [])),
            "queues_count": len(data["queues"]),
            "users_count": len(data["users"]),
            "sessions_count": len(data["outbound_sessions"]),
            "events_count": len(data["ccxml_events"]),
        }
    )


@app.route("/api/queues")
def api_queues():
    data = read_shared_data()
    return jsonify(data["queues"])


@app.route("/api/users")
def api_users():
    data = read_shared_data()
    return jsonify(data["users"])


@app.route("/api/sessions")
def api_sessions():
    data = read_shared_data()
    return jsonify(
        {"sessions": data["sessions"], "outbound": data["outbound_sessions"]}
    )


@app.route("/api/events")
def api_events():
    data = read_shared_data()
    return jsonify(data["ccxml_events"])


@app.route("/api/errors")
def api_errors():
    data = read_shared_data()
    return jsonify(data["errors"])


@app.route("/api/all")
def api_all():
    """Retourne toutes les donnees"""
    data = read_shared_data()

    # Calculate stats
    users = data.get("users", [])
    stats = {
        "total_users": len(users),
        "supervisors": len([u for u in users if u.get("type") == "supervisor"]),
        "agents": len([u for u in users if u.get("type") == "agent"]),
        "logged_in": len(
            [u for u in users if u.get("state") and "plugged" in u["state"].lower()]
        ),
    }

    # Format events for calls tab
    events = data.get("ccxml_events", [])
    formatted_events = []
    for event in events[-20:]:  # Last 20 events
        formatted_events.append(
            {
                "type": event.get("type", "unknown"),
                "user": event.get("user", ""),
                "from": event.get("from", ""),
                "to": event.get("to", ""),
                "time": event.get("time", ""),
            }
        )

    # Add stats and format response
    data["stats"] = stats
    data["events"] = formatted_events

    return jsonify(data)


@app.route("/api/poll")
def api_poll():
    """Polling endpoint pour les clients"""
    return jsonify(read_shared_data())


# Initialiser le fichier de donnees
def init_data_file():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump(cached_data, f, indent=2)


if __name__ == "__main__":
    port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PORT

    init_data_file()

    print("=" * 60)
    print("  CCCP Web Monitor - Temps Reel avec SSE")
    print("  Serveur: http://0.0.0.0:%s" % port)
    print("  Dashboard: http://localhost:%s" % port)
    print("  SSE Stream: http://localhost:%s/sse" % port)
    print("  Polling API: http://localhost:%s/api/poll" % port)
    print("=" * 60)
    print()
    print("  1. Ouvrir http://localhost:%s dans un navigateur" % port)
    print("  2. Les donnees se mettent a jour automatiquement")
    print("  3. Lancer le monitoring: python3 monitor_worker.py")
    print()

    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
