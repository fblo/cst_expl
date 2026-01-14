#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's mcanal libraries.
# Interact-IV.com (c) 2013-2016
#
# Contact: softeam@interact-iv.com
# Authors:
#    - JTAG <jtag@interact-iv.com>

"""Enhanced CCXML Client with Configuration Deployment."""

import uuid
import time
from cccp.async_module.ccxml import CcxmlClient
from cccp.protocols import messages
import cccp.protocols.messages.user_control as message_user
import cccp.protocols.messages.config_deploy as message_config
from cccp.utils.log import Log

log = Log("cccp.async.ccxml_deploy")


class ConfigurableCcxmlClient(CcxmlClient):
    """CCXML client with configuration deployment capabilities."""

    def __init__(self, name, ip, port, config_dir="/tmp"):
        super(ConfigurableCcxmlClient, self).__init__(name, ip, port)
        self.config_dir = config_dir
        self.deployment_callbacks = {}
        self.deployment_queue = []
        self.authenticated_for_deployment = False
        self.deployment_permissions = set()

    def authenticate_for_deployment(self, login, password, project):
        """Authenticate with deployment permissions."""
        session_id = self._generate_session_id()

        self.connecting_sessions[session_id] = {
            "login": login,
            "password": password,
            "project": project,
            "context": "deployment",
        }

        # Enhanced login with deployment rights request
        self.protocol.sendMessage(
            message_user.add_session,
            session_id,
            login,
            password,
            1,  # was_connected
            "1234",  # protocol version
            "deployment",  # additional context for deployment rights
        )

        self.pending_deployment_auth = session_id
        return session_id

    def on_login_ok(self, session_id, user_id, explorer_id):
        """Handle successful login with deployment rights check."""
        super(ConfigurableCcxmlClient, self).on_login_ok(
            session_id, user_id, explorer_id
        )

        if (
            hasattr(self, "pending_deployment_auth")
            and session_id == self.pending_deployment_auth
        ):
            # Check deployment permissions
            self.protocol.sendMessage(message_user.get_rights, session_id)

    def on_rights(self, session_id, rights):
        """Handle rights response for deployment permissions."""
        if session_id == getattr(self, "pending_deployment_auth", None):
            deployment_rights = [
                r for r in rights if "deploy" in r.lower() or "config" in r.lower()
            ]

            if deployment_rights:
                self.authenticated_for_deployment = True
                self.deployment_permissions.update(deployment_rights)
                log.system_message(
                    "Deployment permissions granted: %s" % deployment_rights
                )
            else:
                log.error_message("No deployment permissions granted")

            self.pending_deployment_auth = None

    def deploy_configuration(self, project, ccxml_content, backup=True, validate=True):
        """Deploy CCXML configuration to server."""
        if not self.authenticated_for_deployment:
            raise Exception("Not authenticated for deployment")

        deployment_id = self._generate_deployment_id()

        log.system_message("Starting deployment: %s" % deployment_id)

        try:
            # Create backup if requested
            if backup:
                self._create_remote_backup(project, deployment_id)

            # Validate configuration if requested
            if validate:
                validation_result = self._validate_configuration(
                    deployment_id, ccxml_content
                )
                if not validation_result.get("valid", False):
                    raise Exception(
                        "Configuration validation failed: %s"
                        % validation_result.get("errors", [])
                    )

            # Send deployment request
            self.protocol.sendMessage(
                message_config.config_deploy_request,
                deployment_id,
                project,
                ccxml_content,
                backup,
                validate,
                int(time.time()),  # timestamp
            )

            log.system_message("Deployment request sent: %s" % deployment_id)
            return deployment_id

        except Exception as e:
            log.error_message("Deployment failed: %s" % e)
            raise

    def _create_remote_backup(self, project, deployment_id):
        """Create remote backup of current configuration."""
        self.protocol.sendMessage(
            message_config.config_backup_request,
            deployment_id,
            project,
            "auto_backup_before_deploy_%s" % deployment_id,
        )

    def _validate_configuration(self, deployment_id, ccxml_content):
        """Validate CCXML configuration."""
        # Basic validation
        if not ccxml_content or len(ccxml_content.strip()) == 0:
            return {"valid": False, "errors": ["Empty CCXML content"]}

        if not ccxml_content.strip().startswith("<?xml"):
            return {"valid": False, "errors": ["Invalid XML format"]}

        # Send validation request to server
        self.protocol.sendMessage(
            message_config.config_validate_request, deployment_id, ccxml_content
        )

        # Return placeholder - actual validation comes via response
        return {"valid": True, "errors": []}

    def validate_configuration(self, ccxml_content):
        """Validate CCXML configuration asynchronously."""
        validation_id = self._generate_validation_id()

        self.protocol.sendMessage(
            message_config.config_validate_request, validation_id, ccxml_content
        )

        return validation_id

    def get_deployment_status(self, deployment_id):
        """Get deployment status."""
        self.protocol.sendMessage(
            message_config.deployment_status_request, deployment_id
        )

    def rollback_configuration(self, project, backup_name=None):
        """Rollback to previous configuration."""
        rollback_id = self._generate_rollback_id()

        self.protocol.sendMessage(
            message_config.config_rollback_request,
            rollback_id,
            project,
            backup_name or "last_backup",
        )

        return rollback_id

    def _generate_deployment_id(self):
        """Generate unique deployment ID."""
        return str(uuid.uuid4())[:8].upper()

    def _generate_validation_id(self):
        """Generate unique validation ID."""
        return "VAL_%s" % str(uuid.uuid4())[:6].upper()

    def _generate_rollback_id(self):
        """Generate unique rollback ID."""
        return "ROLL_%s" % str(uuid.uuid4())[:6].upper()

    def _generate_session_id(self):
        """Generate unique session ID."""
        return 1000 + len(self.connected_sessions) + len(self.connecting_sessions)

    # Enhanced message handlers
    def on_config_deploy_response(self, deployment_id, success, message, details):
        """Handle deployment response from server."""
        log.system_message("Deployment response: %s - %s" % (deployment_id, success))

        if deployment_id in self.deployment_callbacks:
            callback = self.deployment_callbacks.pop(deployment_id)
            if callable(callback):
                callback(success, message, details)

    def on_config_validate_response(self, validation_id, valid, errors):
        """Handle validation response."""
        log.system_message("Validation response: %s - %s" % (validation_id, valid))

        if validation_id in self.deployment_callbacks:
            callback = self.deployment_callbacks.pop(validation_id)
            if callable(callback):
                callback(valid, errors)

    def on_config_backup_response(self, deployment_id, backup_path, success):
        """Handle backup response."""
        log.system_message("Backup response: %s - %s" % (deployment_id, success))

    def on_config_rollback_response(self, rollback_id, success, message):
        """Handle rollback response."""
        log.system_message("Rollback response: %s - %s" % (rollback_id, success))

    def on_deployment_status_response(self, deployment_id, status, details):
        """Handle deployment status response."""
        log.system_message("Status response: %s - %s" % (deployment_id, status))

    def on_config_chunk_response(self, chunk_id, success, message):
        """Handle chunk response for large file transfers."""
        log.system_message("Chunk response: %s - %s" % (chunk_id, success))

    # Register additional message handlers
    def register_deployment_callback(self, deployment_id, callback):
        """Register callback for deployment response."""
        self.deployment_callbacks[deployment_id] = callback

    def register_validation_callback(self, validation_id, callback):
        """Register callback for validation response."""
        self.deployment_callbacks[validation_id] = callback

    def has_deployment_permissions(self):
        """Check if authenticated for deployment."""
        return (
            self.authenticated_for_deployment and len(self.deployment_permissions) > 0
        )

    def get_deployment_permissions(self):
        """Get deployment permissions."""
        return list(self.deployment_permissions)
