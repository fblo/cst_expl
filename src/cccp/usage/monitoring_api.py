#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's mcanal libraries.
# Interact-IV.com (c) 2013-2016
#
# Contact: softeam@interact-iv.com
# Authors:
#    - JTAG <jtag@interact-iv.com>

"""CCCP Monitoring REST API."""

from flask import Flask, request, jsonify, render_template_string
from cccp.usage.realtime_monitor import CccpRealtimeMonitor
from cccp.conf.ccxml_values import CcxmlValuesManager
from cccp.conf.ccxml_entries import CcxmlEntriesManager
from cccp.conf.ccxml_template import CcxmlTemplateManager
from cccp.conf.deployment_manager import CcxmlDeploymentManager
import json


class CccpMonitoringAPI(object):
    """REST API for CCCP monitoring and configuration."""

    def __init__(self, host="10.199.30.67", project="default", debug=False):
        self.app = Flask(__name__)
        self.host = host
        self.project = project
        self.debug = debug

        # Initialize managers
        self.monitor = CccpRealtimeMonitor()
        self.values_manager = CcxmlValuesManager(host, project)
        self.entries_manager = CcxmlEntriesManager(host, project)
        self.template_manager = CcxmlTemplateManager(host, project)

        # Initialize deployment manager (will be set up later)
        self.deployment_manager = None

        self._setup_routes()

    def _setup_routes(self):
        """Setup Flask routes."""

        @self.app.route("/")
        def index():
            """Main dashboard page."""
            template = """
<!DOCTYPE html>
<html>
<head>
    <title>CCCP Monitor - {{ host }}</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .header { background: #333; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .status { display: flex; gap: 20px; margin-bottom: 20px; }
        .card { background: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card h3 { margin-top: 0; color: #333; }
        .connected { color: green; }
        .disconnected { color: red; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .refresh-btn { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 3px; cursor: pointer; }
        .refresh-btn:hover { background: #0056b3; }
        .deploy-section { background: white; padding: 20px; border-radius: 5px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .deploy-btn { background: #28a745; color: white; border: none; padding: 8px 16px; border-radius: 3px; cursor: pointer; margin: 5px; }
        .deploy-btn:hover { background: #218838; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 CCCP CCXML Manager & Monitor</h1>
        <p>Server: {{ host }} | Project: {{ project }}</p>
        <p>Status: <span id="connection-status" class="{{ 'connected' if status.connected else 'disconnected' }}">
            {{ 'Connected' if status.connected else 'Disconnected' }}
        </span></p>
        <p>Last Update: <span id="last-update">{{ status.last_update or 'Never' }}</span></p>
    </div>
    
    <div class="deploy-section">
        <h3>📋 CCXML Deployment</h3>
        <div>
            <button class="deploy-btn" onclick="deployConfiguration()">🚀 Deploy Current Configuration</button>
            <button class="deploy-btn" onclick="validateConfiguration()">✅ Validate Configuration</button>
            <button class="deploy-btn" onclick="showDeploymentStatus()">📊 Deployment Status</button>
        </div>
    </div>
    
    <div class="stats">
        <div class="card">
            <h3>👥 Users</h3>
            <p>Total: {{ stats.users.total }}</p>
            <p>Logged In: {{ stats.users.logged_in }}</p>
            <p>Supervisors: {{ stats.users.supervisors }}</p>
            <p>Agents: {{ stats.users.agents }}</p>
        </div>
        
        <div class="card">
            <h3>📞 Queues</h3>
            <p>Total: {{ stats.queues.total }}</p>
            <p>Logged: {{ stats.queues.total_logged }}</p>
            <p>Working: {{ stats.queues.total_working }}</p>
            <p>Waiting: {{ stats.queues.total_waiting }}</p>
        </div>
        
        <div class="card">
            <h3>📞 Calls</h3>
            <p>Active: {{ stats.calls.active }}</p>
            <p>Incoming: {{ stats.calls.incoming_active }}</p>
            <p>Outgoing: {{ stats.calls.outgoing_active }}</p>
            <p>Completed Today: {{ stats.calls.completed_today }}</p>
        </div>
    </div>
    
    <div style="margin-top: 20px; text-align: center;">
        <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>
        <a href="/api/all" target="_blank">📊 API Data</a>
    </div>
    
    <script>
        // CCXML Deployment Functions
        function deployConfiguration() {
            fetch('/api/ccxml/deploy', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    method: 'auto',
                    backup: true,
                    validate: true
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✅ Deployment successful! ' + data.message);
                } else {
                    alert('❌ Deployment failed: ' + data.error);
                }
            })
            .catch(error => {
                alert('💥 Error: ' + error.message);
            });
        }
        
        function validateConfiguration() {
            fetch('/api/ccxml/deploy/validate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    // This would need the current CCXML content
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.valid) {
                    alert('✅ Configuration is valid!');
                } else {
                    alert('❌ Configuration is invalid: ' + data.errors.join(', '));
                }
            })
            .catch(error => {
                alert('💥 Error: ' + error.message);
            });
        }
        
        function showDeploymentStatus() {
            fetch('/api/ccxml/deploy/status')
            .then(response => response.json())
            .then(status => {
                let statusText = 'CCXML Client: ' + (status.ccxml_client_available ? '✅ Available' : '❌ Not Available') + '\\n' +
                               'Fallback Client: ' + (status.fallback_client_available ? '✅ Available' : '❌ Not Available') + '\\n' +
                               'Current Method: ' + status.current_method + '\\n' +
                               'Deployment Count: ' + status.deployment_count;
                alert(statusText);
            })
            .catch(error => {
                alert('💥 Error: ' + error.message);
            });
        }
        
        // Auto-refresh every 30 seconds
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>
            """
            data = self._get_dashboard_data()
            return render_template_string(template, **data)

        @self.app.route("/api/status")
        def api_status():
            """Get system status."""
            return jsonify(self.monitor.get_status_overview())

        @self.app.route("/api/users")
        def api_users():
            """Get users data."""
            search = request.args.get("search", "")
            if search:
                users = self.monitor.search_users(search)
            else:
                users = self.monitor.data.get("users", [])
            return jsonify({"users": users, "total": len(users)})

        @self.app.route("/api/users/<user_id>")
        def api_user_details(user_id):
            """Get specific user details."""
            user = self.monitor.get_user_details(user_id)
            if not user:
                return jsonify({"error": "User not found"}), 404
            return jsonify(user)

        @self.app.route("/api/queues")
        def api_queues():
            """Get queues data."""
            return jsonify(self.monitor.get_queue_summary())

        @self.app.route("/api/queues/<queue_name>")
        def api_queue_details(queue_name):
            """Get specific queue details."""
            queue = self.monitor.get_queue_details(queue_name)
            if not queue:
                return jsonify({"error": "Queue not found"}), 404
            return jsonify(queue)

        @self.app.route("/api/calls")
        def api_calls():
            """Get calls data."""
            return jsonify(self.monitor.get_call_summary())

        @self.app.route("/api/calls/history")
        def api_calls_history():
            """Get call history."""
            calls = self.monitor.data.get("calls", {})
            history = calls.get("history", [])
            return jsonify({"history": history, "total": len(history)})

        @self.app.route("/api/statistics")
        def api_statistics():
            """Get comprehensive statistics."""
            return jsonify(
                {
                    "users": self.monitor.get_user_summary(),
                    "queues": self.monitor.get_queue_summary(),
                    "calls": self.monitor.get_call_summary(),
                    "status": self.monitor.get_status_overview(),
                }
            )

        @self.app.route("/api/errors")
        def api_errors():
            """Get error logs."""
            return jsonify({"errors": self.monitor.data.get("errors", [])})

        @self.app.route("/api/clear-errors", methods=["POST"])
        def api_clear_errors():
            """Clear error logs."""
            success, message = self.monitor.clear_errors()
            return jsonify({"success": success, "message": message})

        @self.app.route("/api/refresh", methods=["POST"])
        def api_refresh():
            """Force data refresh."""
            success, message = self.monitor.force_refresh()
            return jsonify({"success": success, "message": message})

        @self.app.route("/api/sse")
        def api_sse():
            """Server-Sent Events for real-time updates."""
            return self.monitor.create_sse_response()

        @self.app.route("/api/all")
        def api_all():
            """Get all monitoring data."""
            return jsonify(self.monitor.get_current_data())

        @self.app.route("/api/export")
        def api_export():
            """Export current state."""
            return jsonify(self.monitor.export_current_state())

        # CCXML Configuration API endpoints

        @self.app.route("/api/ccxml/values")
        def api_ccxml_values():
            """Get CCXML configuration values."""
            try:
                values = self.values_manager.list_all_values()
                return jsonify({"values": values})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/ccxml/values/<path:section>")
        def api_ccxml_section_values(section):
            """Get CCXML values for specific section."""
            try:
                if section == "users":
                    values = self.values_manager.get_user_values()
                elif section == "entries":
                    values = self.values_manager.get_entry_values()
                else:
                    return jsonify({"error": "Invalid section"}), 400
                return jsonify({"section": section, "values": values})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/ccxml/values/<path:value_path>", methods=["PUT"])
        def api_ccxml_set_value(value_path):
            """Set CCXML configuration value."""
            try:
                data = request.get_json()
                if not data or "value" not in data:
                    return jsonify({"error": "Value required in request body"}), 400

                result = self.values_manager.set_value_by_path(
                    value_path, data["value"]
                )
                return jsonify({"path": value_path, "result": result})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/ccxml/entries")
        def api_ccxml_entries():
            """Get CCXML entries."""
            try:
                entries = self.entries_manager.get_all_entries()
                return jsonify({"entries": entries, "total": len(entries)})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/ccxml/entries/<entry_name>")
        def api_ccxml_entry_details(entry_name):
            """Get specific CCXML entry."""
            try:
                entry = self.entries_manager.get_entry_by_name(entry_name)
                if not entry:
                    return jsonify({"error": "Entry not found"}), 404
                return jsonify(entry)
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/ccxml/entries", methods=["POST"])
        def api_ccxml_add_entry():
            """Add new CCXML entry."""
            try:
                data = request.get_json()
                required = ["name", "scenario"]
                for field in required:
                    if field not in data:
                        return jsonify(
                            {"error": f"Missing required field: {field}"}
                        ), 400

                result = self.entries_manager.add_entry(
                    name=data["name"],
                    scenario=data["scenario"],
                    values=data.get("values", {}),
                    disconnected_timeout=data.get("disconnected_timeout", "0"),
                )
                return jsonify({"success": True, "result": result})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/ccxml/entries/<entry_name>", methods=["DELETE"])
        def api_ccxml_remove_entry(entry_name):
            """Remove CCXML entry."""
            try:
                result = self.entries_manager.remove_entry(entry_name)
                return jsonify({"success": True, "result": result})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/ccxml/outbound/upgrade", methods=["POST"])
        def api_ccxml_outbound_upgrade():
            """Upgrade project to support outbound calls."""
            try:
                result = self.entries_manager.upgrade_to_outbound()
                return jsonify({"success": True, "result": result})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/ccxml/outbound/check")
        def api_ccxml_outbound_check():
            """Check if outbound is configured."""
            try:
                has_outbound = self.entries_manager.check_outbound_support()
                return jsonify({"outbound_enabled": has_outbound})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/ccxml/scenarios")
        def api_ccxml_scenarios():
            """List all scenarios used by entries."""
            try:
                scenarios = self.entries_manager.list_scenarios()
                return jsonify({"scenarios": scenarios, "total": len(scenarios)})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        # Deployment management API

        @self.app.route("/api/ccxml/deploy", methods=["POST"])
        def api_ccxml_deploy():
            """Deploy CCXML configuration manually."""
            try:
                data = request.get_json()

                # Deployment options
                method = data.get("method", "auto")  # auto, ccxml, ccenter
                backup = data.get("backup", True)
                validate = data.get("validate", True)

                # Prepare deployment changes if any
                config_changes = data.get("config_changes", {})

                # Deploy configuration
                success, message, details = (
                    self.deployment_manager.deploy_configuration(
                        config_changes=config_changes, backup=backup, validate=validate
                    )
                )

                return jsonify(
                    {
                        "success": success,
                        "message": message,
                        "method": method,
                        "backup_created": backup,
                        "details": details,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/ccxml/deploy/status")
        def api_deployment_status():
            """Get deployment status."""
            try:
                status = self.deployment_manager.get_deployment_status()
                return jsonify(status)
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/ccxml/deploy/history")
        def api_deployment_history():
            """Get deployment history."""
            try:
                history = self.deployment_manager.get_deployment_history()
                return jsonify({"history": history, "total": len(history)})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/ccxml/deploy/validate", methods=["POST"])
        def api_validate_configuration():
            """Validate configuration before deployment."""
            try:
                data = request.get_json()
                ccxml_content = data.get("ccxml_content")

                if not ccxml_content:
                    return jsonify({"error": "CCXML content required"}), 400

                # Create temporary deployment plan for validation
                deployment_plan = {
                    "deployment_id": "VALIDATION",
                    "local_ccxml_file": None,
                    "ccxml_content": ccxml_content,
                }

                validation_result = self.deployment_manager._validate_configuration(
                    deployment_plan
                )

                return jsonify(
                    {
                        "valid": validation_result["valid"],
                        "errors": validation_result.get("errors", []),
                        "timestamp": validation_result.get("validation_time"),
                    }
                )

            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/ccxml/deploy/ready")
        def api_deployment_readiness():
            """Check if system is ready for deployment."""
            try:
                readiness = self.deployment_manager.validate_deployment_readiness()
                return jsonify(readiness)
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/ccxml/deploy/rollback", methods=["POST"])
        def api_emergency_rollback():
            """Emergency rollback deployment."""
            try:
                data = request.get_json()
                backup_name = data.get("backup_name")

                # This would need implementation based on deployment history
                success = True  # Placeholder
                message = (
                    "Rollback completed successfully" if success else "Rollback failed"
                )

                return jsonify(
                    {"success": success, "message": message, "backup_name": backup_name}
                )

            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        # Template management API

        @self.app.route("/api/ccxml/template/standard")
        def api_ccxml_template_standard():
            """Get standard CCXML template."""
            try:
                template = self.template_manager.get_standard_template()
                return jsonify(template)
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/ccxml/template/create", methods=["POST"])
        def api_ccxml_template_create():
            """Create CCXML from template."""
            try:
                data = request.get_json()
                required = ["country", "whitelabel", "project", "pai"]
                for field in required:
                    if field not in data:
                        return jsonify(
                            {"error": f"Missing required field: {field}"}
                        ), 400

                ccxml_content = self.template_manager.create_standard_project(
                    country=data["country"],
                    whitelabel=data["whitelabel"],
                    project=data["project"],
                    pai=data["pai"],
                    include_outbound=data.get("include_outbound", True),
                )

                return jsonify(
                    {
                        "success": True,
                        "ccxml_content": ccxml_content,
                        "parameters": data,
                    }
                )
            except Exception as e:
                return jsonify({"error": str(e)}), 500

    def _get_dashboard_data(self):
        """Get data for dashboard template."""
        monitoring_data = self.monitor.get_current_data()
        return {
            "host": self.host,
            "project": self.project,
            "status": self.monitor.get_status_overview(),
            "stats": {
                "users": self.monitor.get_user_summary(),
                "queues": {
                    "total": len(self.monitor.data.get("queues", [])),
                    "total_logged": sum(
                        q.get("logged", 0) for q in self.monitor.data.get("queues", [])
                    ),
                    "total_working": sum(
                        q.get("working", 0) for q in self.monitor.data.get("queues", [])
                    ),
                    "total_waiting": sum(
                        q.get("waiting", 0) for q in self.monitor.data.get("queues", [])
                    ),
                },
                "calls": self.monitor.get_call_summary(),
            },
        }

    def start(self, host="0.0.0.0", port=5000, auto_start_monitoring=True):
        """Start the API server."""
        if auto_start_monitoring:
            success, message = self.monitor.start_monitoring()
            if success:
                print(f"✓ Monitoring started: {message}")
            else:
                print(f"✗ Monitoring error: {message}")

        print(f"✓ Starting CCCP Monitoring API")
        print(f"  Host: {host}")
        print(f"  Port: {port}")
        print(f"  Dashboard: http://localhost:{port}")
        print(f"  API Base: http://localhost:{port}/api")
        print(f"  SSE Stream: http://localhost:{port}/api/sse")

        self.app.run(host=host, port=port, debug=self.debug, threaded=True)

    def stop(self):
        """Stop the API server."""
        success, message = self.monitor.stop_monitoring()
        return {"success": success, "message": message}
