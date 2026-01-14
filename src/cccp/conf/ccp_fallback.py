#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's mcanal libraries.
# Interact-IV.com (c) 2013-2016
#
# Contact: softeam@interact-iv.com
# Authors:
#    - JTAG <jtag@interact-iv.com>

"""CCenter Update Fallback for CCXML Deployment."""

import subprocess
import os
import tempfile
import time
from cccp.utils.log import Log

log = Log("cccp.fallback")


class CcenterUpdateFallback(object):
    """Fallback deployment using ccenter_update tool."""

    def __init__(self, host, project, auth=None):
        self.host = host
        self.project = project
        self.auth = auth or {"login": "admin", "password": "admin"}
        self.port = 20000
        self.remote_path = "/db/projects/%s/Ccxml.xml" % project

    def deploy_ccxml(self, ccxml_file, backup=True):
        """Deploy CCXML using ccenter_update."""
        try:
            log.system_message("Deploying via ccenter_update fallback")

            # Step 1: Create backup if requested
            backup_file = None
            if backup:
                backup_file = self._download_current_ccxml()
                if backup_file:
                    log.system_message("Current CCXML backed up to: %s" % backup_file)

            # Step 2: Deploy new configuration
            success, stdout, stderr = self._ccenter_put(self.remote_path, ccxml_file)

            if success:
                log.system_message("CCXML deployment successful via ccenter_update")
                return (
                    True,
                    "Deployment successful via ccenter_update",
                    {
                        "method": "ccenter_update",
                        "backup_file": backup_file,
                        "stdout": stdout,
                    },
                )
            else:
                log.error_message("ccenter_update failed: %s" % stderr)
                return (
                    False,
                    "ccenter_update failed: %s" % stderr,
                    {"method": "ccenter_update", "stderr": stderr},
                )

        except Exception as e:
            log.error_message("Fallback deployment error: %s" % e)
            return (
                False,
                "Fallback deployment error: %s" % e,
                {"method": "ccenter_update"},
            )

    def _download_current_ccxml(self):
        """Download current CCXML from server."""
        try:
            backup_dir = tempfile.gettempdir()
            timestamp = int(time.time())
            backup_filename = "%s_ccxml_backup_%d.xml" % (self.project, timestamp)
            backup_file = os.path.join(backup_dir, backup_filename)

            success, stdout, stderr = self._ccenter_get(self.remote_path, backup_file)

            if success:
                return backup_file
            else:
                log.warning_message("Could not backup current CCXML: %s" % stderr)
                return None

        except Exception as e:
            log.error_message("Backup failed: %s" % e)
            return None

    def _ccenter_get(self, remote_path, local_path):
        """Execute ccenter_update get command."""
        cmd = [
            "ccenter_update",
            "-login",
            self.auth["login"],
            "-password",
            self.auth["password"],
            "-server",
            self.host,
            str(self.port),
            "-content",
            remote_path,
        ]

        log.system_message("Executing: %s" % " ".join(cmd))

        try:
            with open(local_path, "w") as f:
                result = subprocess.run(
                    cmd, stdout=f, stderr=subprocess.PIPE, text=True, timeout=30
                )

            return result.returncode == 0, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            error = "ccenter_get timeout"
            log.error_message(error)
            return False, "", error
        except FileNotFoundError:
            error = "ccenter_update not found"
            log.error_message(error)
            return False, "", error

    def _ccenter_put(self, remote_path, local_path):
        """Execute ccenter_update put command."""
        cmd = [
            "ccenter_update",
            "-login",
            self.auth["login"],
            "-password",
            self.auth["password"],
            "-server",
            self.host,
            str(self.port),
            "-path",
            remote_path,
            "-file",
            local_path,
            "-create",
        ]

        log.system_message("Executing: %s" % " ".join(cmd))

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            return result.returncode == 0, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            error = "ccenter_put timeout"
            log.error_message(error)
            return False, "", error
        except FileNotFoundError:
            error = "ccenter_update not found"
            log.error_message(error)
            return False, "", error

    def validate_ccxml_access(self):
        """Validate access to CCXML file."""
        try:
            success, stdout, stderr = self._ccenter_get(
                self.remote_path, "/tmp/test_access.xml"
            )
            os.unlink("/tmp/test_access.xml")

            return success, stderr

        except Exception as e:
            return False, str(e)

    def get_server_info(self):
        """Get server information via ccenter_update."""
        try:
            cmd = [
                "ccenter_update",
                "-login",
                self.auth["login"],
                "-password",
                self.auth["password"],
                "-server",
                self.host,
                str(self.port),
                "-info",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_projects(self):
        """List available projects on server."""
        try:
            cmd = [
                "ccenter_update",
                "-login",
                self.auth["login"],
                "-password",
                self.auth["password"],
                "-server",
                self.host,
                str(self.port),
                "-list",
                "/db/projects",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)

            if result.returncode == 0:
                projects = [
                    line.strip() for line in result.stdout.split("\n") if line.strip()
                ]
                return {"success": True, "projects": projects}
            else:
                return {"success": False, "error": result.stderr}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def check_ccxml_exists(self):
        """Check if CCXML file exists on server."""
        try:
            success, stdout, stderr = self._ccenter_get(
                self.remote_path, "/tmp/check_exists.xml"
            )

            try:
                os.unlink("/tmp/check_exists.xml")
            except:
                pass

            return success, "CCXML file exists" if success else "CCXML file not found"

        except Exception as e:
            return False, str(e)
