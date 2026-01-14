#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's mcanal libraries.
# Interact-IV.com (c) 2013-2016
#
# Contact: softeam@interact-iv.com
# Authors:
#    - JTAG <jtag@interact-iv.com>

"""CCXML Entries Management Module."""

import re
from cccp.conf.ccxml_config import CcxmlConfigManager


class CcxmlEntriesManager(object):
    """Manages CCXML entries and their scenarios."""

    def __init__(self, host, project, backup_dir="/tmp"):
        self.config_manager = CcxmlConfigManager(host, project, backup_dir)
        self.host = host
        self.project = project

    def get_all_entries(self):
        """Get all CCXML entries."""
        try:
            self.config_manager.load_ccxml()
            return self.config_manager.get_ccxml_entries()
        except Exception as e:
            raise Exception("Failed to get entries: %s" % e)

    def get_entry_by_name(self, name):
        """Get specific entry by name."""
        try:
            entries = self.get_all_entries()
            for entry in entries:
                if entry["name"] == name:
                    return entry
            return None
        except Exception as e:
            raise Exception("Failed to get entry by name: %s" % e)

    def add_entry(
        self, name, scenario, values=None, disconnected_timeout="0", backup=True
    ):
        """Add new CCXML entry."""
        try:
            if backup:
                self.config_manager.backup_current_file()

            self.config_manager.load_ccxml()
            self.config_manager.add_ccxml_entry(
                name, scenario, values, disconnected_timeout
            )
            self.config_manager.save_ccxml()

            return {"name": name, "scenario": scenario, "status": "created"}
        except Exception as e:
            raise Exception("Failed to add entry: %s" % e)

    def remove_entry(self, name, backup=True):
        """Remove CCXML entry by name."""
        try:
            if backup:
                self.config_manager.backup_current_file()

            self.config_manager.load_ccxml()
            removed = self.config_manager.remove_ccxml_entry(name)
            self.config_manager.save_ccxml()

            return {"name": name, "removed": removed}
        except Exception as e:
            raise Exception("Failed to remove entry: %s" % e)

    def update_entry(self, name, **updates):
        """Update CCXML entry."""
        try:
            self.config_manager.backup_current_file()
            self.config_manager.load_ccxml()

            entries = self.config_manager.get_ccxml_entries()
            entry_found = False

            for entry in entries:
                if entry["name"] == name:
                    entry_found = True
                    # Remove existing entry
                    self.config_manager.remove_ccxml_entry(name)
                    break

            if not entry_found:
                raise Exception("Entry '%s' not found" % name)

            # Apply updates
            scenario = updates.get("scenario", entry["scenario"])
            values = updates.get("values", entry.get("values", {}))
            disconnected_timeout = updates.get(
                "disconnected_timeout", entry.get("disconnected_timeout", "0")
            )

            # Add updated entry
            self.config_manager.add_ccxml_entry(
                name, scenario, values, disconnected_timeout
            )
            self.config_manager.save_ccxml()

            return {"name": name, "updates": updates, "status": "updated"}
        except Exception as e:
            raise Exception("Failed to update entry: %s" % e)

    def get_entry_value(self, entry_name, value_name):
        """Get specific value from an entry."""
        try:
            entry = self.get_entry_by_name(entry_name)
            if not entry:
                raise Exception("Entry '%s' not found" % entry_name)

            return entry.get("values", {}).get(value_name)
        except Exception as e:
            raise Exception("Failed to get entry value: %s" % e)

    def set_entry_value(self, entry_name, value_name, value):
        """Set specific value in an entry."""
        try:
            entry = self.get_entry_by_name(entry_name)
            if not entry:
                raise Exception("Entry '%s' not found" % entry_name)

            values = entry.get("values", {})
            values[value_name] = value

            return self.update_entry(entry_name, values=values)
        except Exception as e:
            raise Exception("Failed to set entry value: %s" % e)

    def list_entries_by_scenario(self, scenario):
        """List all entries using a specific scenario."""
        try:
            entries = self.get_all_entries()
            return [entry for entry in entries if entry["scenario"] == scenario]
        except Exception as e:
            raise Exception("Failed to list entries by scenario: %s" % e)

    def list_scenarios(self):
        """List all unique scenarios used by entries."""
        try:
            entries = self.get_all_entries()
            scenarios = set()
            for entry in entries:
                if entry["scenario"]:
                    scenarios.add(entry["scenario"])
            return sorted(list(scenarios))
        except Exception as e:
            raise Exception("Failed to list scenarios: %s" % e)

    def validate_entry(self, name, scenario, values=None, disconnected_timeout="0"):
        """Validate entry parameters."""
        try:
            errors = []

            # Validate name
            if not name:
                errors.append("Entry name cannot be empty")
            elif not re.match(r"^[a-zA-Z0-9_]+$", name):
                errors.append(
                    "Entry name must contain only alphanumeric characters and underscore"
                )

            # Validate scenario
            if not scenario:
                errors.append("Scenario cannot be empty")
            elif not scenario.endswith(".xml"):
                errors.append("Scenario must end with .xml extension")
            elif not re.match(r"^[a-zA-Z0-9_\-\.]+\.xml$", scenario):
                errors.append("Invalid scenario format")

            # Validate disconnected_timeout
            try:
                timeout = int(disconnected_timeout)
                if timeout < 0:
                    errors.append("Disconnected timeout must be non-negative")
            except ValueError:
                errors.append("Disconnected timeout must be a number")

            # Validate values if provided
            if values:
                for value_name, value_data in values.items():
                    if not value_name:
                        errors.append("Value name cannot be empty")
                    if value_data is None:
                        errors.append("Value data cannot be None for %s" % value_name)

            return len(errors) == 0, errors
        except Exception as e:
            return False, ["Validation error: %s" % e]

    def add_outbound_entry(self, name="agent_outbound", backup=True):
        """Add standard outbound entry."""
        try:
            outbound_values = {
                "accueil": "sda_default.xml",
                "project_type_cfg": "outbound",
                "delay_cfg": "0",
            }

            return self.add_entry(
                name=name,
                scenario="Outbound.xml",
                values=outbound_values,
                disconnected_timeout="0",
                backup=backup,
            )
        except Exception as e:
            raise Exception("Failed to add outbound entry: %s" % e)

    def check_outbound_support(self):
        """Check if project has outbound support configured."""
        try:
            outbound_entries = self.list_entries_by_scenario("Outbound.xml")
            return len(outbound_entries) > 0
        except Exception as e:
            raise Exception("Failed to check outbound support: %s" % e)

    def upgrade_to_outbound(self, backup=True):
        """Upgrade project to support outbound calls."""
        try:
            if self.check_outbound_support():
                return {
                    "status": "already_upgraded",
                    "message": "Outbound support already configured",
                }

            return self.add_outbound_entry(backup=backup)
        except Exception as e:
            raise Exception("Failed to upgrade to outbound: %s" % e)

    def get_entries_by_project_type(self, project_type):
        """Get entries filtered by project_type_cfg value."""
        try:
            entries = self.get_all_entries()
            filtered_entries = []

            for entry in entries:
                values = entry.get("values", {})
                if values.get("project_type_cfg") == project_type:
                    filtered_entries.append(entry)

            return filtered_entries
        except Exception as e:
            raise Exception("Failed to get entries by project type: %s" % e)

    def duplicate_entry(self, source_name, target_name, **value_overrides):
        """Duplicate an entry with optional value overrides."""
        try:
            source_entry = self.get_entry_by_name(source_name)
            if not source_entry:
                raise Exception("Source entry '%s' not found" % source_name)

            # Check if target already exists
            if self.get_entry_by_name(target_name):
                raise Exception("Target entry '%s' already exists" % target_name)

            # Copy values and apply overrides
            values = source_entry.get("values", {}).copy()
            values.update(value_overrides)

            return self.add_entry(
                name=target_name,
                scenario=source_entry["scenario"],
                values=values,
                disconnected_timeout=source_entry.get("disconnected_timeout", "0"),
            )
        except Exception as e:
            raise Exception("Failed to duplicate entry: %s" % e)

    def import_entries_from_template(self, template_entries, backup=True):
        """Import entries from template data."""
        try:
            if backup:
                self.config_manager.backup_current_file()

            self.config_manager.load_ccxml()
            imported_entries = []
            errors = []

            for entry_data in template_entries:
                try:
                    name = entry_data.get("name")
                    scenario = entry_data.get("scenario")
                    values = entry_data.get("values", {})
                    disconnected_timeout = entry_data.get("disconnected_timeout", "0")

                    if not name or not scenario:
                        errors.append("Entry missing name or scenario: %s" % entry_data)
                        continue

                    # Validate entry
                    valid, validation_errors = self.validate_entry(
                        name, scenario, values, disconnected_timeout
                    )
                    if not valid:
                        errors.append(
                            "Validation failed for %s: %s"
                            % (name, "; ".join(validation_errors))
                        )
                        continue

                    # Check if entry already exists
                    existing = self.get_entry_by_name(name)
                    if existing:
                        errors.append("Entry %s already exists" % name)
                        continue

                    # Add entry
                    self.config_manager.add_ccxml_entry(
                        name, scenario, values, disconnected_timeout
                    )
                    imported_entries.append(name)

                except Exception as e:
                    errors.append("Error importing entry: %s" % e)

            if imported_entries:
                self.config_manager.save_ccxml()

            return {
                "imported": imported_entries,
                "errors": errors,
                "total": len(template_entries),
            }
        except Exception as e:
            raise Exception("Failed to import entries from template: %s" % e)

    def export_entries_to_template(self, entry_names=None):
        """Export entries to template format."""
        try:
            entries = self.get_all_entries()
            template_entries = []

            for entry in entries:
                if entry_names and entry["name"] not in entry_names:
                    continue

                template_entries.append(
                    {
                        "name": entry["name"],
                        "scenario": entry["scenario"],
                        "values": entry.get("values", {}),
                        "disconnected_timeout": entry.get("disconnected_timeout", "0"),
                    }
                )

            return template_entries
        except Exception as e:
            raise Exception("Failed to export entries to template: %s" % e)
