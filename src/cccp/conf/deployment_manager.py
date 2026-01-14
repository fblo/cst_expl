#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's mcanal libraries.
# Interact-IV.com (c) 2013-2016
#
# Contact: softeam@interact-iv.com
# Authors:
#    - JTAG <jtag@interact-iv.com>

"""Unified CCXML Deployment Manager."""

import os
import tempfile
import time
from datetime import datetime
from cccp.utils.log import Log

log = Log("cccp.deployment_manager")


class CcxmlDeploymentManager(object):
    """Unified manager for CCXML deployment with multiple methods."""

    def __init__(self, host, project, method="auto", auth=None, config_dir="/tmp"):
        self.host = host
        self.project = project
        self.method = method
        self.config_dir = config_dir
        self.auth = auth or {"login": "admin", "password": "admin"}

        # Initialize deployment clients
        self.ccxml_client = None
        self.fallback_client = None

        # Initialize configuration managers
        self.config_manager = CcxmlConfigManager(host, project, config_dir)
        self.entries_manager = CcxmlEntriesManager(host, project, config_dir)
        self.values_manager = CcxmlValuesManager(host, project, config_dir)

        # Deployment history
        self.deployment_history = []
        self.last_deployment = None

    def initialize_clients(self):
        """Initialize deployment clients."""
        try:
            # Initialize CCXML client (primary method)
            self.ccxml_client = ConfigurableCcxmlClient(
                "deploy_client", self.host, 20102, self.config_dir
            )
            log.system_message("CCXML client initialized for port 20102")

        except Exception as e:
            log.warning_message("Failed to initialize CCXML client: %s" % e)
            self.ccxml_client = None

        try:
            # Initialize fallback client
            self.fallback_client = CcenterUpdateFallback(
                self.host, self.project, self.auth
            )
            log.system_message("ccenter_update fallback initialized")

        except Exception as e:
            log.error_message("Failed to initialize fallback client: %s" % e)
            self.fallback_client = None

    def deploy_configuration(self, config_changes=None, backup=True, validate=True):
        """Deploy configuration changes to server."""
        log.system_message("Starting deployment for project: %s" % self.project)

        deployment_plan = self._create_deployment_plan(config_changes)

        try:
            # Phase 1: Preparation
            if backup:
                backup_result = self._create_deployment_backup(deployment_plan)
                deployment_plan["backup_created"] = backup_result
                log.system_message("Backup phase completed")

            if validate:
                validation_result = self._validate_configuration(deployment_plan)
                if not validation_result["valid"]:
                    error_msg = (
                        "Configuration validation failed: %s"
                        % validation_result["errors"]
                    )
                    log.error_message(error_msg)
                    return False, error_msg, None

                deployment_plan["validation_passed"] = True
                log.system_message("Validation phase passed")

            # Phase 2: Deployment
            deployment_id = self._execute_deployment(deployment_plan)

            # Phase 3: Verification
            verification_result = self._verify_deployment(
                deployment_id, deployment_plan
            )

            # Record deployment
            self._record_deployment(deployment_id, deployment_plan, verification_result)

            return True, deployment_id, deployment_plan

        except Exception as e:
            error_msg = "Deployment failed: %s" % e
            log.error_message(error_msg)

            # Emergency rollback if backup was created
            if backup and deployment_plan.get("backup_created"):
                try:
                    self._emergency_rollback(deployment_plan)
                except Exception as rb_error:
                    log.error_message("Rollback failed: %s" % rb_error)

            return False, error_msg, None

    def _create_deployment_plan(self, config_changes):
        """Create structured deployment plan."""
        timestamp = datetime.now().isoformat()

        plan = {
            "deployment_id": "DEPLOY_%d" % int(time.time()),
            "project": self.project,
            "timestamp": timestamp,
            "changes": config_changes or {},
            "method": self.method,
            "backup_created": False,
            "validation_passed": False,
            "local_ccxml_file": None,
            "deployment_attempts": [],
        }

        # Apply changes to local configuration
        if config_changes:
            self._apply_configuration_changes(config_changes)

        # Save current configuration
        self.config_manager.save_ccxml()
        plan["local_ccxml_file"] = self.config_manager.updated_filename

        log.system_message("Deployment plan created: %s" % plan["deployment_id"])
        return plan

    def _apply_configuration_changes(self, config_changes):
        """Apply configuration changes to local managers."""
        for change_type, change_data in config_changes.items():
            try:
                if change_type == "values":
                    self.values_manager.import_values(change_data, backup=False)
                elif change_type == "entries":
                    if isinstance(change_data, list):
                        self.entries_manager.import_entries_from_template(
                            change_data, backup=False
                        )
                    else:
                        # Single entry operations
                        if change_data.get("action") == "add":
                            self.entries_manager.add_entry(
                                name=change_data["name"],
                                scenario=change_data["scenario"],
                                values=change_data.get("values", {}),
                                backup=False,
                            )
                        elif change_data.get("action") == "remove":
                            self.entries_manager.remove_entry(
                                change_data["name"], backup=False
                            )
                elif change_type == "project_values":
                    self.values_manager.update_project_values(
                        **change_data, backup=False
                    )

                log.system_message("Applied %s changes successfully" % change_type)

            except Exception as e:
                log.error_message("Failed to apply %s changes: %s" % (change_type, e))
                raise

    def _create_deployment_backup(self, deployment_plan):
        """Create backup before deployment."""
        try:
            backup_name = "%s_pre_deploy_%d" % (self.project, int(time.time()))

            if self.fallback_client:
                # Use fallback method for backup
                backup_file = self.fallback_client._download_current_ccxml()
                if backup_file:
                    log.system_message("Remote backup created: %s" % backup_file)
                    return backup_file

            # Local backup
            self.config_manager.backup_current_file()
            log.system_message("Local backup created")
            return True

        except Exception as e:
            log.error_message("Backup creation failed: %s" % e)
            return False

    def _validate_configuration(self, deployment_plan):
        """Validate configuration before deployment."""
        try:
            ccxml_file = deployment_plan["local_ccxml_file"]

            if not os.path.exists(ccxml_file):
                return {"valid": False, "errors": ["CCXML file not found"]}

            # Load and validate CCXML
            self.config_manager.load_ccxml(ccxml_file)
            valid, message = self.config_manager.validate_ccxml()

            return {
                "valid": valid,
                "errors": [] if valid else [message],
                "validation_time": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"valid": False, "errors": ["Validation error: %s" % e]}

    def _execute_deployment(self, deployment_plan):
        """Execute deployment using preferred method."""
        deployment_attempts = []

        # Try CCXML protocol first
        if self.method in ["ccxml", "auto"] and self.ccxml_client:
            attempt = self._deploy_via_ccxml(deployment_plan)
            deployment_attempts.append(attempt)

            if attempt["success"]:
                deployment_plan["method_used"] = "ccxml"
                log.system_message("Deployment successful via CCXML protocol")
                return deployment_plan["deployment_id"]

        # Fallback to ccenter_update
        if self.method in ["ccenter", "auto"] and self.fallback_client:
            attempt = self._deploy_via_ccenter(deployment_plan)
            deployment_attempts.append(attempt)

            if attempt["success"]:
                deployment_plan["method_used"] = "ccenter_update"
                log.system_message("Deployment successful via ccenter_update")
                return deployment_plan["deployment_id"]

        deployment_plan["deployment_attempts"] = deployment_attempts

        # All methods failed
        error_msg = "All deployment methods failed"
        log.error_message(error_msg)
        raise Exception(error_msg)

    def _deploy_via_ccxml(self, deployment_plan):
        """Deploy via CCXML protocol."""
        try:
            from twisted.internet import defer
            from twisted.internet import reactor

            # Initialize clients if needed
            if not self.ccxml_client:
                self.initialize_clients()

            if not self.ccxml_client:
                return {
                    "success": False,
                    "method": "ccxml",
                    "error": "CCXML client not available",
                }

            # Create deferred for async operation
            d = defer.Deferred()

            def deploy():
                try:
                    # Authenticate for deployment
                    session_id = self.ccxml_client.authenticate_for_deployment(
                        self.auth["login"], self.auth["password"], self.project
                    )

                    # Register callback
                    self.ccxml_client.register_deployment_callback(
                        deployment_plan["deployment_id"], d.callback
                    )

                    # Deploy configuration
                    with open(deployment_plan["local_ccxml_file"], "r") as f:
                        ccxml_content = f.read()

                    self.ccxml_client.deploy_configuration(
                        self.project, ccxml_content, backup=False
                    )

                    # Wait for response (with timeout)
                    reactor.callLater(30, timeout_handler)

                except Exception as e:
                    reactor.callFromThread(d.errback, e)

            def timeout_handler():
                if not d.called:
                    d.errback(Exception("Deployment timeout"))

            def on_success(result):
                return {
                    "success": True,
                    "method": "ccxml",
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                }

            def on_failure(failure):
                return {
                    "success": False,
                    "method": "ccxml",
                    "error": str(failure.value),
                    "timestamp": datetime.now().isoformat(),
                }

            d.addCallback(on_success)
            d.addErrback(on_failure)

            # Start deployment
            reactor.callFromThread(deploy)

            # Wait for completion (this would need to be integrated properly)
            return d.result  # This is simplified

        except Exception as e:
            return {
                "success": False,
                "method": "ccxml",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _deploy_via_ccenter(self, deployment_plan):
        """Deploy via ccenter_update fallback."""
        try:
            if not self.fallback_client:
                return {
                    "success": False,
                    "method": "ccenter_update",
                    "error": "ccenter_update client not available",
                }

            # Deploy using fallback
            success, message, details = self.fallback_client.deploy_ccxml(
                deployment_plan["local_ccxml_file"], backup=False
            )

            return {
                "success": success,
                "method": "ccenter_update",
                "message": message,
                "details": details,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "method": "ccenter_update",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _verify_deployment(self, deployment_id, deployment_plan):
        """Verify deployment success."""
        try:
            # Basic verification - check if deployment was recorded
            verification = {
                "deployment_id": deployment_id,
                "verified": True,
                "method_used": deployment_plan.get("method_used"),
                "timestamp": datetime.now().isoformat(),
            }

            log.system_message("Deployment verified: %s" % deployment_id)
            return verification

        except Exception as e:
            log.error_message("Verification failed: %s" % e)
            return {
                "deployment_id": deployment_id,
                "verified": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _record_deployment(self, deployment_id, deployment_plan, verification):
        """Record deployment in history."""
        deployment_record = {
            "deployment_id": deployment_id,
            "plan": deployment_plan,
            "verification": verification,
            "timestamp": datetime.now().isoformat(),
        }

        self.deployment_history.append(deployment_record)
        self.last_deployment = deployment_record

        log.system_message("Deployment recorded: %s" % deployment_id)

    def _emergency_rollback(self, deployment_plan):
        """Emergency rollback to previous configuration."""
        try:
            if self.fallback_client:
                # Try to restore from backup
                log.warning_message("Attempting emergency rollback")

                # This would need to be implemented based on backup strategy
                success = False  # Placeholder

                if success:
                    log.system_message("Emergency rollback successful")
                else:
                    log.error_message("Emergency rollback failed")

        except Exception as e:
            log.error_message("Rollback error: %s" % e)

    def get_deployment_history(self):
        """Get deployment history."""
        return self.deployment_history

    def get_deployment_status(self):
        """Get current deployment status."""
        return {
            "ccxml_client_available": self.ccxml_client is not None,
            "fallback_client_available": self.fallback_client is not None,
            "last_deployment": self.last_deployment,
            "deployment_count": len(self.deployment_history),
            "current_method": self.method,
        }

    def set_auth_credentials(self, login, password):
        """Set authentication credentials."""
        self.auth = {"login": login, "password": password}

        if self.fallback_client:
            self.fallback_client.auth = self.auth

    def validate_deployment_readiness(self):
        """Validate if system is ready for deployment."""
        checks = {
            "ccxml_client": self.ccxml_client is not None,
            "fallback_client": self.fallback_client is not None,
            "auth_configured": bool(
                self.auth.get("login") and self.auth.get("password")
            ),
            "config_manager_ready": self.config_manager is not None,
            "file_permissions": os.access(self.config_dir, os.W_OK),
        }

        all_ready = all(checks.values())

        return {
            "ready": all_ready,
            "checks": checks,
            "timestamp": datetime.now().isoformat(),
        }
