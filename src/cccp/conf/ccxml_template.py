#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's mcanal libraries.
# Interact-IV.com (c) 2013-2016
#
# Contact: softeam@interact-iv.com
# Authors:
#    - JTAG <jtag@interact-iv.com>

"""CCXML Templates Management Module."""

import os
import tempfile
from cccp.conf.ccxml_config import CcxmlConfigManager
from cccp.conf.ccxml_entries import CcxmlEntriesManager
from cccp.conf.ccxml_values import CcxmlValuesManager


class CcxmlTemplateManager(object):
    """Manages CCXML templates for new projects."""

    def __init__(self, host, project, backup_dir="/tmp"):
        self.host = host
        self.project = project
        self.backup_dir = backup_dir
        self.config_manager = CcxmlConfigManager(host, project, backup_dir)

    def get_standard_template(self):
        """Get standard CCXML template structure."""
        return {
            "header": {
                "version": "1.0",
                "encoding": "ISO-8859-1",
                "standalone": "yes",
            },
            "root": {
                "tag": "com.consistent.ccenter.ccxml.ccenter_ccxml",
                "id": "_1",
                "class_name": "ccenter_ccxml",
            },
            "sections": {
                "regular_days": self._get_regular_days_template(),
                "states": self._get_states_template(),
                "modes": self._get_modes_template(),
                "tasks": self._get_tasks_template(),
                "entrys": [],  # Will be populated separately
            },
            "values": {
                "users_values": self._get_users_values_template(),
                "entries_values": self._get_entries_values_template(),
            },
        }

    def _get_regular_days_template(self):
        """Get regular days configuration template."""
        days = []
        day_names = [
            "lundi",
            "mardi",
            "mercredi",
            "jeudi",
            "vendredi",
            "samedi",
            "dimanche",
        ]

        for i, day in enumerate(day_names, 1):
            days.append(
                {
                    "id": "_%d" % (i + 100),
                    "name": day,
                    "display_name": day.capitalize(),
                    "use_day_off": "False",
                }
            )

        # Add all_days
        days.append(
            {
                "id": "_108",
                "name": "all_days",
                "display_name": "Tous les jours",
                "use_day_off": "False",
            }
        )

        return days

    def _get_states_template(self):
        """Get states configuration template."""
        return [
            {
                "id": "_200",
                "name": "plugged",
                "display_name": "Branché",
                "can_dial": "True",
                "record_agent": "True",
                "record_warning": "True",
                "manage_calls": "True",
                "manage_outbound_calls": "True",
            },
            {
                "id": "_201",
                "name": "pause",
                "display_name": "Pause",
                "can_dial": "False",
                "record_agent": "False",
                "record_warning": "False",
                "manage_calls": "False",
                "manage_outbound_calls": "False",
            },
            {
                "id": "_202",
                "name": "ringing",
                "display_name": "Décroché",
                "can_dial": "False",
                "record_agent": "False",
                "record_warning": "False",
                "manage_calls": "True",
                "manage_outbound_calls": "True",
            },
            {
                "id": "_203",
                "name": "busy",
                "display_name": "Occupé",
                "can_dial": "False",
                "record_agent": "False",
                "record_warning": "False",
                "manage_calls": "True",
                "manage_outbound_calls": "True",
            },
        ]

    def _get_modes_template(self):
        """Get modes configuration template."""
        return [
            {
                "id": "_300",
                "name": "supervisor_interface",
                "display_name": "Interface Supervision",
                "can_dial": "True",
                "record_agent": "True",
                "record_warning": "True",
                "manage_calls": "True",
                "manage_outbound_calls": "True",
            },
            {
                "id": "_301",
                "name": "supervisor_unplug",
                "display_name": "Supervision Débranché",
                "can_dial": "True",
                "record_agent": "True",
                "record_warning": "True",
                "manage_calls": "True",
                "manage_outbound_calls": "True",
            },
            {
                "id": "_302",
                "name": "supervisor_plugged",
                "display_name": "Supervision Branché",
                "can_dial": "True",
                "record_agent": "True",
                "record_warning": "True",
                "manage_calls": "True",
                "manage_outbound_calls": "True",
            },
        ]

    def _get_tasks_template(self):
        """Get tasks configuration template."""
        return [
            {
                "id": "_400",
                "name": "inbound_calls",
                "display_name": "Appels entrants",
                "state_name": "plugged",
                "mode_name": "",
                "task_type": "1",
            },
            {
                "id": "_401",
                "name": "outbound_calls",
                "display_name": "Appels sortants",
                "state_name": "plugged",
                "mode_name": "",
                "task_type": "3",
            },
        ]

    def _get_users_values_template(self):
        """Get users values template."""
        return {
            "country_cfg": None,
            "whitelabel_cfg": None,
            "project_cfg": None,
            "p_asserted_identity_cfg": None,
        }

    def _get_entries_values_template(self):
        """Get entries values template."""
        return {
            "country_cfg": None,
            "whitelabel_cfg": None,
            "project_cfg": None,
            "p_asserted_identity_cfg": None,
        }

    def create_new_project_ccxml(
        self, project_values=None, entries=None, include_outbound=False
    ):
        """Create complete CCXML file for new project."""
        try:
            template = self.get_standard_template()

            # Set project values if provided
            if project_values:
                self._apply_project_values(template, project_values)

            # Add entries if provided
            if entries:
                template["sections"]["entrys"] = entries
            else:
                template["sections"]["entrys"] = self._get_standard_entries(
                    include_outbound
                )

            # Create XML file
            return self._generate_ccxml_xml(template)
        except Exception as e:
            raise Exception("Failed to create new project CCXML: %s" % e)

    def _apply_project_values(self, template, project_values):
        """Apply project values to template."""
        sections = ["users_values", "entries_values"]
        for section in sections:
            if section in template["values"]:
                for key, value in project_values.items():
                    if key in template["values"][section]:
                        template["values"][section][key] = value

    def _get_standard_entries(self, include_outbound=True):
        """Get standard CCXML entries."""
        entries = []

        # Standard inbound entry
        entries.append(
            {
                "id": "_4012070001",
                "name": "agent_inbound",
                "scenario": "Agent.xml",
                "disconnected_timeout": "0",
                "values": {
                    "accueil": "sda_default.xml",
                    "project_type_cfg": "inbound",
                    "delay_cfg": "0",
                },
            }
        )

        # Outbound entry if requested
        if include_outbound:
            entries.append(
                {
                    "id": "_4012070010",
                    "name": "agent_outbound",
                    "scenario": "Outbound.xml",
                    "disconnected_timeout": "0",
                    "values": {
                        "accueil": "sda_default.xml",
                        "project_type_cfg": "outbound",
                        "delay_cfg": "0",
                    },
                }
            )

        return entries

    def _generate_ccxml_xml(self, template):
        """Generate XML from template structure."""
        try:
            import xml.etree.ElementTree as ET
            from xml.dom import minidom

            # Create root element
            root_attrs = template["root"]
            root = ET.Element(
                root_attrs["tag"],
                id=root_attrs["id"],
                class_name=root_attrs["class_name"],
            )

            # Add sections
            sections = template["sections"]

            # Add regular_days
            if sections.get("regular_days"):
                regular_days_elem = ET.SubElement(root, "regular_days")
                for day in sections["regular_days"]:
                    day_elem = ET.SubElement(
                        regular_days_elem,
                        "com.consistent.ccenter.ccxml.ccenter_ccxml_regular_day",
                        id=day["id"],
                        name=day["name"],
                        display_name=day["display_name"],
                        use_day_off=day["use_day_off"],
                    )

            # Add states
            if sections.get("states"):
                states_elem = ET.SubElement(root, "states")
                for state in sections["states"]:
                    state_elem = ET.SubElement(
                        states_elem,
                        "com.consistent.ccenter.ccxml.ccenter_ccxml_state",
                        id=state["id"],
                        name=state["name"],
                        display_name=state["display_name"],
                        can_dial=state["can_dial"],
                        record_agent=state["record_agent"],
                        record_warning=state["record_warning"],
                        manage_calls=state["manage_calls"],
                        manage_outbound_calls=state["manage_outbound_calls"],
                    )

            # Add modes
            if sections.get("modes"):
                modes_elem = ET.SubElement(root, "modes")
                for mode in sections["modes"]:
                    mode_elem = ET.SubElement(
                        modes_elem,
                        "com.consistent.ccenter.ccxml.ccenter_ccxml_mode",
                        id=mode["id"],
                        name=mode["name"],
                        display_name=mode["display_name"],
                        can_dial=mode["can_dial"],
                        record_agent=mode["record_agent"],
                        record_warning=mode["record_warning"],
                        manage_calls=mode["manage_calls"],
                        manage_outbound_calls=mode["manage_outbound_calls"],
                    )

            # Add tasks
            if sections.get("tasks"):
                tasks_elem = ET.SubElement(root, "tasks")
                for task in sections["tasks"]:
                    task_elem = ET.SubElement(
                        tasks_elem,
                        "com.consistent.ccenter.ccxml.ccenter_ccxml_task",
                        id=task["id"],
                        name=task["name"],
                        display_name=task["display_name"],
                        state_name=task["state_name"],
                        mode_name=task["mode_name"],
                        task_type=task["task_type"],
                    )

            # Add entries
            if sections.get("entrys"):
                entrys_elem = ET.SubElement(root, "entrys")
                for entry in sections["entrys"]:
                    entry_elem = ET.SubElement(
                        entrys_elem,
                        "ccenter_ccxml_entry",
                        id=entry["id"],
                        name=entry["name"],
                        scenario=entry["scenario"],
                        disconnected_timeout=entry["disconnected_timeout"],
                    )

                    # Add values if present
                    if entry.get("values"):
                        values_elem = ET.SubElement(entry_elem, "values")
                        for value_name, value_data in entry["values"].items():
                            value_id = "_%d_%s" % (len(entry["values"]), value_name)
                            value_elem = ET.SubElement(
                                values_elem,
                                "com.consistent.protocol.consistent_protocol_named_object_value_string",
                                id=value_id,
                                name=value_name,
                                value=value_data,
                            )

            # Add values sections
            values = template["values"]

            # Add users_values
            if values.get("users_values"):
                users_values_elem = ET.SubElement(root, "users_values")
                for name, value in values["users_values"].items():
                    if value is not None:
                        value_elem = ET.SubElement(
                            users_values_elem,
                            "com.consistent.protocol.consistent_protocol_named_object_value_string",
                            id="_users_%s" % name,
                            name=name,
                            value=value,
                        )

            # Add entries_values
            if values.get("entries_values"):
                entries_values_elem = ET.SubElement(root, "entries_values")
                for name, value in values["entries_values"].items():
                    if value is not None:
                        value_elem = ET.SubElement(
                            entries_values_elem,
                            "com.consistent.protocol.consistent_protocol_named_object_value_string",
                            id="_entries_%s" % name,
                            name=name,
                            value=value,
                        )

            # Generate XML string
            tree = ET.ElementTree(root)
            temp_file = tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=".xml"
            )
            tree.write(temp_file.name, encoding="ISO-8859-1", xml_declaration=True)
            temp_file.close()

            # Pretty format
            with open(temp_file.name, "r") as f:
                xml_content = f.read()

            dom = minidom.parseString(xml_content)
            pretty_xml = dom.toprettyxml(indent="  ")

            # Clean up
            os.unlink(temp_file.name)

            return pretty_xml

        except Exception as e:
            raise Exception("Failed to generate CCXML XML: %s" % e)

    def create_standard_project(
        self, country, whitelabel, project, pai, include_outbound=True
    ):
        """Create standard project configuration."""
        try:
            project_values = {
                "country_cfg": country,
                "whitelabel_cfg": whitelabel,
                "project_cfg": project,
                "p_asserted_identity_cfg": pai,
            }

            return self.create_new_project_ccxml(
                project_values=project_values, include_outbound=include_outbound
            )
        except Exception as e:
            raise Exception("Failed to create standard project: %s" % e)

    def save_project_ccxml(self, ccxml_content, file_path=None):
        """Save CCXML content to file."""
        try:
            if file_path is None:
                file_path = os.path.join(self.backup_dir, "%s_Ccxml.xml" % self.project)

            with open(file_path, "w") as f:
                f.write(ccxml_content)

            return file_path
        except Exception as e:
            raise Exception("Failed to save project CCXML: %s" % e)

    def deploy_new_project(
        self, country, whitelabel, project, pai, include_outbound=True, backup=True
    ):
        """Deploy complete new project configuration."""
        try:
            # Create CCXML content
            ccxml_content = self.create_standard_project(
                country, whitelabel, project, pai, include_outbound
            )

            # Save to file
            ccxml_file = self.save_project_ccxml(ccxml_content)

            # Load into configuration manager
            self.config_manager.load_ccxml(ccxml_file)

            # Validate
            valid, message = self.config_manager.validate_ccxml()
            if not valid:
                raise Exception("Invalid CCXML: %s" % message)

            # Save to target location
            if backup:
                self.config_manager.backup_current_file()

            self.config_manager.save_ccxml()

            return {
                "project": project,
                "ccxml_file": ccxml_file,
                "outbound_enabled": include_outbound,
                "status": "deployed",
            }
        except Exception as e:
            raise Exception("Failed to deploy new project: %s" % e)
