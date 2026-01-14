#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's mcanal libraries.
# Interact-IV.com (c) 2013-2016
#
# Contact: softeam@interact-iv.com
# Authors:
#    - JTAG <jtag@interact-iv.com>

"""CCXML Configuration Management Module."""

import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import os
import re
from datetime import datetime
import tempfile
import shutil


class CcxmlConfigManager(object):
    """Manages CCXML configuration files and values."""

    def __init__(self, host, project, backup_dir="/tmp"):
        self.host = host
        self.project = project
        self.backup_dir = backup_dir
        self.remote_path = "/db/projects/%s/Ccxml.xml" % project
        self.backup_filename = os.path.join(backup_dir, "%s_old_Ccxml.xml" % project)
        self.updated_filename = os.path.join(backup_dir, "%s_new_Ccxml.xml" % project)
        self.root = None
        self.tree = None

        # Deployment manager integration
        self.deployment_manager = None

    def load_ccxml(self, file_path=None):
        """Load CCXML file for editing."""
        if file_path is None:
            file_path = self.backup_filename

        if not os.path.exists(file_path):
            raise Exception("CCXML file not found: %s" % file_path)

        try:
            self.tree = ET.parse(file_path)
            self.root = self.tree.getroot()
            return True
        except ET.ParseError as e:
            raise Exception("Error parsing CCXML file: %s" % e)

    def save_ccxml(self, file_path=None, format_xml=True):
        """Save CCXML file."""
        if self.tree is None:
            raise Exception("No CCXML tree loaded")

        if file_path is None:
            file_path = self.updated_filename

        # Create directory if needed
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Save tree
        self.tree.write(file_path, encoding="ISO-8859-1", xml_declaration=True)

        # Format XML for readability
        if format_xml:
            with open(file_path, "r") as f:
                content = f.read()

            # Pretty format XML
            dom = minidom.parseString(content)
            pretty_xml = dom.toprettyxml(indent="  ")

            # Remove empty lines
            pretty_xml = re.sub(r">\s+<", ">\n<", pretty_xml)
            pretty_xml = "\n".join(
                line for line in pretty_xml.split("\n") if line.strip()
            )

            with open(file_path, "w") as f:
                f.write(pretty_xml)

        return True

    def backup_current_file(self):
        """Create backup of current CCXML file."""
        if os.path.exists(self.backup_filename):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_with_timestamp = "%s.%s" % (
                os.path.splitext(self.backup_filename)[0],
                timestamp,
            )
            shutil.copy2(self.backup_filename, backup_with_timestamp)

    def get_named_object_value(self, section_name, value_name):
        """Get value from named objects section."""
        if self.root is None:
            raise Exception("CCXML not loaded")

        section = self.root.find(".//%s" % section_name)
        if section is None:
            return None

        for value in section.findall(
            ".//com.consistent.protocol.consistent_protocol_named_object_value_string"
        ):
            name = value.get("name")
            if name == value_name:
                return value.get("value")

        return None

    def set_named_object_value(self, section_name, value_name, value):
        """Set value in named objects section."""
        if self.root is None:
            raise Exception("CCXML not loaded")

        section = self.root.find(".//%s" % section_name)
        if section is None:
            # Create section if it doesn't exist
            section = ET.Element(section_name)
            self.root.append(section)

        # Find existing value
        for value_elem in section.findall(
            ".//com.consistent.protocol.consistent_protocol_named_object_value_string"
        ):
            name = value_elem.get("name")
            if name == value_name:
                old_value = value_elem.get("value")
                value_elem.set("value", value)
                return old_value

        # Create new value if not found
        new_id = "_new_%d" % len(section.findall(".//*"))
        new_value = ET.Element(
            "com.consistent.protocol.consistent_protocol_named_object_value_string",
            id=new_id,
            name=value_name,
            value=value,
        )
        section.append(new_value)
        return None

    def get_ccxml_entries(self):
        """Get all CCXML entries."""
        if self.root is None:
            raise Exception("CCXML not loaded")

        entries = []
        entrys_section = self.root.find(".//entrys")
        if entrys_section is None:
            return entries

        for entry in entrys_section.findall(".//ccenter_ccxml_entry"):
            entry_data = {
                "id": entry.get("id"),
                "name": entry.get("name"),
                "scenario": entry.get("scenario"),
                "disconnected_timeout": entry.get("disconnected_timeout"),
                "values": {},
            }

            # Get entry values
            values_section = entry.find(".//values")
            if values_section is not None:
                for value in values_section.findall(
                    ".//com.consistent.protocol.consistent_protocol_named_object_value_string"
                ):
                    name = value.get("name")
                    val = value.get("value")
                    entry_data["values"][name] = val

            entries.append(entry_data)

        return entries

    def add_ccxml_entry(self, name, scenario, values=None, disconnected_timeout="0"):
        """Add new CCXML entry."""
        if self.root is None:
            raise Exception("CCXML not loaded")

        # Find or create entrys section
        entrys_section = self.root.find(".//entrys")
        if entrys_section is None:
            entrys_section = ET.Element("entrys")
            self.root.append(entrys_section)

        # Generate unique ID
        existing_ids = [
            int(e.get("id").lstrip("_"))
            for e in entrys_section.findall(".//ccenter_ccxml_entry")
            if e.get("id", "").lstrip("_").isdigit()
        ]
        new_id = max(existing_ids + [0]) + 1

        # Create new entry
        entry = ET.Element(
            "ccenter_ccxml_entry",
            id="_%d" % new_id,
            name=name,
            scenario=scenario,
            disconnected_timeout=disconnected_timeout,
        )

        # Add values if provided
        if values:
            values_section = ET.Element("values")
            for value_name, value_data in values.items():
                value_id = "_%d_%d" % (new_id, len(values_section))
                value_elem = ET.Element(
                    "com.consistent.protocol.consistent_protocol_named_object_value_string",
                    id=value_id,
                    name=value_name,
                    value=value_data,
                )
                values_section.append(value_elem)
            entry.append(values_section)

        entrys_section.append(entry)
        return entry

    def remove_ccxml_entry(self, name):
        """Remove CCXML entry by name."""
        if self.root is None:
            raise Exception("CCXML not loaded")

        entrys_section = self.root.find(".//entrys")
        if entrys_section is None:
            return False

        for entry in entrys_section.findall(".//ccenter_ccxml_entry"):
            if entry.get("name") == name:
                entrys_section.remove(entry)
                return True

        return False

    def get_project_config(self):
        """Get project configuration values."""
        config = {}
        sections = ["users_values", "entries_values"]
        value_names = [
            "country_cfg",
            "whitelabel_cfg",
            "project_cfg",
            "p_asserted_identity_cfg",
        ]

        for section in sections:
            config[section] = {}
            for value_name in value_names:
                value = self.get_named_object_value(section, value_name)
                config[section][value_name] = value

        return config

    def set_project_config(self, country=None, whitelabel=None, project=None, pai=None):
        """Set project configuration values."""
        changes = {}
        values = {
            "country_cfg": country,
            "whitelabel_cfg": whitelabel,
            "project_cfg": project,
            "p_asserted_identity_cfg": pai,
        }

        sections = ["users_values", "entries_values"]
        for section in sections:
            for value_name, value in values.items():
                if value is not None:
                    old_value = self.set_named_object_value(section, value_name, value)
                    if old_value != value:
                        changes["%s.%s" % (section, value_name)] = {
                            "old": old_value,
                            "new": value,
                        }

        return changes

    def clean_ccxml_file(self):
        """Remove user-specific entries from CCXML."""
        if self.tree is None:
            raise Exception("CCXML not loaded")

        # Remove lines containing user-specific data
        cleaned_lines = []
        with open(self.backup_filename, "r") as f:
            for line in f:
                if "com.consistent.ccenter.ccxml.ccenter_ccxml_user-:" not in line:
                    cleaned_lines.append(line)

        with open(self.updated_filename, "w") as f:
            f.writelines(cleaned_lines)

        # Reload cleaned file
        return self.load_ccxml(self.updated_filename)

    def validate_ccxml(self):
        """Validate CCXML structure."""
        if self.root is None:
            return False, "CCXML not loaded"

        # Check for required sections
        required_sections = ["entrys"]
        for section in required_sections:
            if self.root.find(".//%s" % section) is None:
                return False, "Missing required section: %s" % section

        # Check entries structure
        entries = self.get_ccxml_entries()
        for entry in entries:
            if not entry.get("name"):
                return False, "Entry missing name attribute"
            if not entry.get("scenario"):
                return False, "Entry missing scenario attribute"

        return True, "CCXML validation passed"

    def set_deployment_manager(self, deployment_manager):
        """Set deployment manager for configuration deployment."""
        self.deployment_manager = deployment_manager

    def deploy_configuration(self, backup=True, validate=True):
        """Deploy current configuration to server."""
        if not self.deployment_manager:
            raise Exception("Deployment manager not configured")

        # Ensure configuration is saved
        self.save_ccxml()

        # Deploy through deployment manager
        return self.deployment_manager.deploy_configuration(
            config_changes={
                "ccxml_file": self.updated_filename,
                "project": self.project,
                "method": "auto",
            },
            backup=backup,
            validate=validate,
        )
