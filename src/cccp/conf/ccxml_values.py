#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's mcanal libraries.
# Interact-IV.com (c) 2013-2016
#
# Contact: softeam@interact-iv.com
# Authors:
#    - JTAG <jtag@interact-iv.com>

"""CCXML Values Management Module."""

from cccp.conf.ccxml_config import CcxmlConfigManager


class CcxmlValuesManager(object):
    """Manages CCXML configuration values."""

    def __init__(self, host, project, backup_dir="/tmp"):
        self.config_manager = CcxmlConfigManager(host, project, backup_dir)
        self.host = host
        self.project = project

    def get_current_values(self):
        """Get all current CCXML values."""
        try:
            self.config_manager.load_ccxml()
            return self.config_manager.get_project_config()
        except Exception as e:
            raise Exception("Failed to get current values: %s" % e)

    def update_project_values(
        self, country=None, whitelabel=None, project=None, pai=None, backup=True
    ):
        """Update project configuration values."""
        try:
            if backup:
                self.config_manager.backup_current_file()

            self.config_manager.load_ccxml()
            changes = self.config_manager.set_project_config(
                country=country, whitelabel=whitelabel, project=project, pai=pai
            )

            self.config_manager.save_ccxml()
            return changes
        except Exception as e:
            raise Exception("Failed to update project values: %s" % e)

    def get_user_values(self):
        """Get user-specific configuration values."""
        try:
            config = self.get_current_values()
            return config.get("users_values", {})
        except Exception as e:
            raise Exception("Failed to get user values: %s" % e)

    def get_entry_values(self):
        """Get entry-specific configuration values."""
        try:
            config = self.get_current_values()
            return config.get("entries_values", {})
        except Exception as e:
            raise Exception("Failed to get entry values: %s" % e)

    def set_user_values(self, **values):
        """Set user-specific configuration values."""
        try:
            self.config_manager.load_ccxml()
            changes = {}

            for name, value in values.items():
                old_value = self.config_manager.set_named_object_value(
                    "users_values", name, value
                )
                if old_value != value:
                    changes["users_values.%s" % name] = {"old": old_value, "new": value}

            self.config_manager.save_ccxml()
            return changes
        except Exception as e:
            raise Exception("Failed to set user values: %s" % e)

    def set_entry_values(self, **values):
        """Set entry-specific configuration values."""
        try:
            self.config_manager.load_ccxml()
            changes = {}

            for name, value in values.items():
                old_value = self.config_manager.set_named_object_value(
                    "entries_values", name, value
                )
                if old_value != value:
                    changes["entries_values.%s" % name] = {
                        "old": old_value,
                        "new": value,
                    }

            self.config_manager.save_ccxml()
            return changes
        except Exception as e:
            raise Exception("Failed to set entry values: %s" % e)

    def get_value_by_path(self, path):
        """Get value by dotted path (e.g., 'users_values.country_cfg')."""
        try:
            section, value_name = path.split(".", 1)
            self.config_manager.load_ccxml()
            return self.config_manager.get_named_object_value(section, value_name)
        except Exception as e:
            raise Exception("Failed to get value by path %s: %s" % (path, e))

    def set_value_by_path(self, path, value):
        """Set value by dotted path (e.g., 'users_values.country_cfg')."""
        try:
            section, value_name = path.split(".", 1)
            self.config_manager.load_ccxml()
            old_value = self.config_manager.set_named_object_value(
                section, value_name, value
            )
            self.config_manager.save_ccxml()
            return {"old": old_value, "new": value}
        except Exception as e:
            raise Exception("Failed to set value by path %s: %s" % (path, e))

    def list_all_values(self):
        """List all configurable values with their current state."""
        try:
            config = self.get_current_values()
            all_values = []

            sections = ["users_values", "entries_values"]
            for section in sections:
                section_values = config.get(section, {})
                for name, value in section_values.items():
                    all_values.append(
                        {
                            "path": "%s.%s" % (section, name),
                            "section": section,
                            "name": name,
                            "value": value,
                            "description": self._get_value_description(name),
                        }
                    )

            return all_values
        except Exception as e:
            raise Exception("Failed to list all values: %s" % e)

    def _get_value_description(self, name):
        """Get description for a value name."""
        descriptions = {
            "country_cfg": "Country configuration (e.g., FR, PT, UK)",
            "whitelabel_cfg": "Whitelabel configuration (e.g., COLT, CONNECTICS)",
            "project_cfg": "Project identifier (e.g., INT101, IVMID)",
            "p_asserted_identity_cfg": "P-Asserted-Identity SIP header value",
        }
        return descriptions.get(name, "Custom configuration value")

    def validate_value(self, name, value):
        """Validate a configuration value."""
        try:
            if name == "country_cfg":
                if not value or len(value) != 2 or not value.isalpha():
                    return False, "Country must be 2-letter code (e.g., FR, PT)"
            elif name == "whitelabel_cfg":
                if not value or len(value) < 2:
                    return False, "Whitelabel must be at least 2 characters"
            elif name == "project_cfg":
                if not value or not re.match(r"^[A-Za-z0-9_]+$", value):
                    return (
                        False,
                        "Project must contain only alphanumeric characters and underscore",
                    )
            elif name == "p_asserted_identity_cfg":
                if (
                    not value
                    or not value.startswith("<sip:")
                    or not value.endswith(">")
                ):
                    return (
                        False,
                        "P-Asserted-Identity must be in format <sip:number@domain>",
                    )
            else:
                # Generic validation
                if value is None:
                    return False, "Value cannot be None"

            return True, "Validation passed"
        except Exception as e:
            return False, "Validation error: %s" % e

    def import_values(self, values_dict, backup=True):
        """Import multiple values from a dictionary."""
        try:
            if backup:
                self.config_manager.backup_current_file()

            self.config_manager.load_ccxml()
            all_changes = {}

            for path, value in values_dict.items():
                try:
                    section, value_name = path.split(".", 1)
                    old_value = self.config_manager.set_named_object_value(
                        section, value_name, value
                    )
                    if old_value != value:
                        all_changes[path] = {"old": old_value, "new": value}
                except Exception as e:
                    # Continue with other values even if one fails
                    all_changes[path] = {"error": str(e)}

            self.config_manager.save_ccxml()
            return all_changes
        except Exception as e:
            raise Exception("Failed to import values: %s" % e)

    def export_values(self, paths=None):
        """Export values to dictionary format."""
        try:
            if paths is None:
                return self.get_current_values()
            else:
                exported = {}
                for path in paths:
                    try:
                        value = self.get_value_by_path(path)
                        section, name = path.split(".", 1)
                        if section not in exported:
                            exported[section] = {}
                        exported[section][name] = value
                    except Exception:
                        exported[path] = "Error retrieving value"
                return exported
        except Exception as e:
            raise Exception("Failed to export values: %s" % e)

    def sync_values_between_sections(self, value_names=None):
        """Synchronize values between users_values and entries_values sections."""
        try:
            if value_names is None:
                value_names = ["country_cfg", "whitelabel_cfg", "project_cfg"]

            self.config_manager.load_ccxml()
            changes = {}

            for name in value_names:
                # Get current value from users_values
                users_value = self.config_manager.get_named_object_value(
                    "users_values", name
                )

                if users_value:
                    # Set same value in entries_values
                    entries_value = self.config_manager.set_named_object_value(
                        "entries_values", name, users_value
                    )
                    if entries_value != users_value:
                        changes["entries_values.%s" % name] = {
                            "old": entries_value,
                            "new": users_value,
                            "synced": True,
                        }

            if changes:
                self.config_manager.save_ccxml()

            return changes
        except Exception as e:
            raise Exception("Failed to sync values: %s" % e)
