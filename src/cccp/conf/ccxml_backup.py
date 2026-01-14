#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's mcanal libraries.
# Interact-IV.com (c) 2013-2016
#
# Contact: softeam@interact-iv.com
# Authors:
#    - JTAG <jtag@interact-iv.com>

"""CCXML Backup and Restore Management Module."""

import os
import json
import shutil
import zipfile
from datetime import datetime
from cccp.conf.ccxml_config import CcxmlConfigManager
from cccp.conf.ccxml_values import CcxmlValuesManager
from cccp.conf.ccxml_entries import CcxmlEntriesManager
from cccp.conf.ccxml_template import CcxmlTemplateManager


class CcxmlBackupManager(object):
    """Manages CCXML configuration backups and restores."""

    def __init__(self, host, project, backup_dir="/tmp/cccp_backups"):
        self.host = host
        self.project = project
        self.backup_dir = backup_dir
        self.config_manager = CcxmlConfigManager(host, project, backup_dir)
        self.values_manager = CcxmlValuesManager(host, project, backup_dir)
        self.entries_manager = CcxmlEntriesManager(host, project, backup_dir)
        self.template_manager = CcxmlTemplateManager(host, project, backup_dir)

        # Ensure backup directory exists
        os.makedirs(backup_dir, exist_ok=True)

    def create_backup(self, backup_name=None, description=""):
        """Create a complete backup of CCXML configuration."""
        try:
            if backup_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{self.project}_{timestamp}"

            backup_path = os.path.join(self.backup_dir, backup_name)
            os.makedirs(backup_path, exist_ok=True)

            # Create backup metadata
            metadata = {
                "backup_name": backup_name,
                "project": self.project,
                "host": self.host,
                "created_at": datetime.now().isoformat(),
                "description": description,
                "version": "1.0",
                "files": {},
            }

            # Backup CCXML file
            try:
                self.config_manager.backup_current_file()
                ccxml_source = self.config_manager.backup_filename
                ccxml_target = os.path.join(backup_path, "Ccxml.xml")

                if os.path.exists(ccxml_source):
                    shutil.copy2(ccxml_source, ccxml_target)
                    metadata["files"]["ccxml"] = "Ccxml.xml"
                else:
                    # Create current CCXML backup
                    self.config_manager.load_ccxml()
                    self.config_manager.save_ccxml(ccxml_target)
                    metadata["files"]["ccxml"] = "Ccxml.xml"

            except Exception as e:
                raise Exception("Failed to backup CCXML file: %s" % e)

            # Export configuration values
            try:
                values = self.values_manager.get_current_values()
                values_file = os.path.join(backup_path, "values.json")
                with open(values_file, "w") as f:
                    json.dump(values, f, indent=2)
                metadata["files"]["values"] = "values.json"
            except Exception as e:
                # Non-critical error
                print(f"Warning: Failed to backup values: {e}")

            # Export entries
            try:
                entries = self.entries_manager.get_all_entries()
                entries_file = os.path.join(backup_path, "entries.json")
                with open(entries_file, "w") as f:
                    json.dump(entries, f, indent=2)
                metadata["files"]["entries"] = "entries.json"
            except Exception as e:
                # Non-critical error
                print(f"Warning: Failed to backup entries: {e}")

            # Save metadata
            metadata_file = os.path.join(backup_path, "backup_metadata.json")
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

            return {
                "success": True,
                "backup_name": backup_name,
                "backup_path": backup_path,
                "metadata": metadata,
            }
        except Exception as e:
            raise Exception("Failed to create backup: %s" % e)

    def list_backups(self):
        """List all available backups."""
        try:
            backups = []
            if not os.path.exists(self.backup_dir):
                return backups

            for item in os.listdir(self.backup_dir):
                backup_path = os.path.join(self.backup_dir, item)
                if os.path.isdir(backup_path):
                    metadata_file = os.path.join(backup_path, "backup_metadata.json")
                    if os.path.exists(metadata_file):
                        try:
                            with open(metadata_file, "r") as f:
                                metadata = json.load(f)

                            # Add file size info
                            total_size = 0
                            for root, dirs, files in os.walk(backup_path):
                                total_size += sum(
                                    os.path.getsize(os.path.join(root, name))
                                    for name in files
                                )

                            metadata["backup_path"] = backup_path
                            metadata["total_size_mb"] = round(
                                total_size / (1024 * 1024), 2
                            )
                            metadata["is_project_backup"] = (
                                metadata.get("project") == self.project
                            )

                            backups.append(metadata)
                        except Exception as e:
                            print(f"Warning: Invalid metadata in {item}: {e}")
                            continue

            # Sort by creation date (newest first)
            backups.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return backups
        except Exception as e:
            raise Exception("Failed to list backups: %s" % e)

    def get_backup_details(self, backup_name):
        """Get detailed information about a specific backup."""
        try:
            backup_path = os.path.join(self.backup_dir, backup_name)
            if not os.path.exists(backup_path):
                raise Exception(f"Backup '{backup_name}' not found")

            metadata_file = os.path.join(backup_path, "backup_metadata.json")
            if not os.path.exists(metadata_file):
                raise Exception(f"Backup metadata not found for '{backup_name}'")

            with open(metadata_file, "r") as f:
                metadata = json.load(f)

            # Add file details
            file_details = {}
            if "files" in metadata:
                for file_type, filename in metadata["files"].items():
                    file_path = os.path.join(backup_path, filename)
                    if os.path.exists(file_path):
                        stat = os.stat(file_path)
                        file_details[file_type] = {
                            "filename": filename,
                            "size_bytes": stat.st_size,
                            "size_mb": round(stat.st_size / (1024 * 1024), 2),
                            "modified": datetime.fromtimestamp(
                                stat.st_mtime
                            ).isoformat(),
                        }

            metadata["file_details"] = file_details
            return metadata
        except Exception as e:
            raise Exception(f"Failed to get backup details: {e}")

    def restore_backup(self, backup_name, components=None, create_backup_before=True):
        """Restore configuration from backup."""
        try:
            backup_path = os.path.join(self.backup_dir, backup_name)
            if not os.path.exists(backup_path):
                raise Exception(f"Backup '{backup_name}' not found")

            # Get backup details
            backup_details = self.get_backup_details(backup_name)

            # Default to restoring all components
            if components is None:
                components = ["ccxml", "values", "entries"]

            # Create backup before restore if requested
            if create_backup_before:
                pre_restore_backup = (
                    f"pre_restore_{backup_name}_{datetime.now().strftime('%H%M%S')}"
                )
                self.create_backup(
                    pre_restore_backup, f"Auto backup before restoring {backup_name}"
                )

            restore_results = {}

            # Restore CCXML file
            if "ccxml" in components and "ccxml" in backup_details["files"]:
                try:
                    ccxml_source = os.path.join(
                        backup_path, backup_details["files"]["ccxml"]
                    )
                    if os.path.exists(ccxml_source):
                        self.config_manager.backup_current_file()
                        shutil.copy2(ccxml_source, self.config_manager.backup_filename)
                        restore_results["ccxml"] = "success"
                    else:
                        restore_results["ccxml"] = "source_file_missing"
                except Exception as e:
                    restore_results["ccxml"] = f"error: {e}"

            # Restore values
            if "values" in components and "values" in backup_details["files"]:
                try:
                    values_source = os.path.join(
                        backup_path, backup_details["files"]["values"]
                    )
                    if os.path.exists(values_source):
                        with open(values_source, "r") as f:
                            values_data = json.load(f)

                        # Apply values to current configuration
                        self.values_manager.import_values(
                            {
                                f"{section}.{key}": value
                                for section, section_values in values_data.items()
                                for key, value in section_values.items()
                            }
                        )
                        restore_results["values"] = "success"
                    else:
                        restore_results["values"] = "source_file_missing"
                except Exception as e:
                    restore_results["values"] = f"error: {e}"

            # Restore entries
            if "entries" in components and "entries" in backup_details["files"]:
                try:
                    entries_source = os.path.join(
                        backup_path, backup_details["files"]["entries"]
                    )
                    if os.path.exists(entries_source):
                        with open(entries_source, "r") as f:
                            entries_data = json.load(f)

                        # Clear existing entries and import from backup
                        current_entries = self.entries_manager.get_all_entries()
                        for entry in current_entries:
                            self.entries_manager.remove_entry(
                                entry["name"], backup=False
                            )

                        self.entries_manager.import_entries_from_template(
                            entries_data, backup=False
                        )
                        restore_results["entries"] = "success"
                    else:
                        restore_results["entries"] = "source_file_missing"
                except Exception as e:
                    restore_results["entries"] = f"error: {e}"

            return {
                "success": True,
                "backup_name": backup_name,
                "restored_components": components,
                "results": restore_results,
                "pre_restore_backup": pre_restore_backup
                if create_backup_before
                else None,
            }
        except Exception as e:
            raise Exception(f"Failed to restore backup: {e}")

    def delete_backup(self, backup_name):
        """Delete a backup."""
        try:
            backup_path = os.path.join(self.backup_dir, backup_name)
            if not os.path.exists(backup_path):
                raise Exception(f"Backup '{backup_name}' not found")

            shutil.rmtree(backup_path)
            return {"success": True, "backup_name": backup_name}
        except Exception as e:
            raise Exception(f"Failed to delete backup: {e}")

    def export_backup(self, backup_name, export_path=None):
        """Export backup as zip file."""
        try:
            backup_path = os.path.join(self.backup_dir, backup_name)
            if not os.path.exists(backup_path):
                raise Exception(f"Backup '{backup_name}' not found")

            if export_path is None:
                export_path = f"{backup_name}.zip"

            # Create zip file
            with zipfile.ZipFile(export_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(backup_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, backup_path)
                        zipf.write(file_path, arcname)

            return {
                "success": True,
                "backup_name": backup_name,
                "export_path": os.path.abspath(export_path),
                "size_mb": round(os.path.getsize(export_path) / (1024 * 1024), 2),
            }
        except Exception as e:
            raise Exception(f"Failed to export backup: {e}")

    def import_backup(self, import_path, backup_name=None):
        """Import backup from zip file."""
        try:
            if not os.path.exists(import_path):
                raise Exception(f"Import file '{import_path}' not found")

            if backup_name is None:
                backup_name = f"imported_{os.path.splitext(os.path.basename(import_path))[0]}_{datetime.now().strftime('%H%M%S')}"

            backup_path = os.path.join(self.backup_dir, backup_name)
            os.makedirs(backup_path, exist_ok=True)

            # Extract zip file
            with zipfile.ZipFile(import_path, "r") as zipf:
                zipf.extractall(backup_path)

            # Validate imported backup
            metadata_file = os.path.join(backup_path, "backup_metadata.json")
            if not os.path.exists(metadata_file):
                raise Exception("Invalid backup file: missing metadata")

            return {
                "success": True,
                "backup_name": backup_name,
                "import_path": os.path.abspath(import_path),
                "backup_path": backup_path,
            }
        except Exception as e:
            raise Exception(f"Failed to import backup: {e}")

    def cleanup_old_backups(self, keep_count=10, days_old=30):
        """Clean up old backups based on count and age."""
        try:
            backups = self.list_backups()
            deleted_backups = []
            kept_backups = []

            current_time = datetime.now()

            for backup in backups:
                backup_name = backup.get("backup_name")
                created_at = datetime.fromisoformat(backup.get("created_at", ""))
                age_days = (current_time - created_at).days

                # Keep if recent or within count limit
                if age_days <= days_old or len(kept_backups) < keep_count:
                    kept_backups.append(backup_name)
                else:
                    try:
                        self.delete_backup(backup_name)
                        deleted_backups.append(
                            {"name": backup_name, "age_days": age_days}
                        )
                    except Exception as e:
                        print(f"Warning: Failed to delete backup {backup_name}: {e}")

            return {
                "success": True,
                "deleted_backups": deleted_backups,
                "kept_backups": kept_backups,
                "total_kept": len(kept_backups),
                "total_deleted": len(deleted_backups),
            }
        except Exception as e:
            raise Exception(f"Failed to cleanup old backups: {e}")

    def get_backup_statistics(self):
        """Get backup storage statistics."""
        try:
            backups = self.list_backups()

            total_size = 0
            total_count = len(backups)

            if total_count > 0:
                for backup in backups:
                    total_size += backup.get("total_size_mb", 0)

            # Get oldest and newest
            oldest_backup = backups[-1] if backups else None
            newest_backup = backups[0] if backups else None

            return {
                "total_backups": total_count,
                "total_size_mb": round(total_size, 2),
                "oldest_backup": {
                    "name": oldest_backup.get("backup_name"),
                    "created_at": oldest_backup.get("created_at"),
                }
                if oldest_backup
                else None,
                "newest_backup": {
                    "name": newest_backup.get("backup_name"),
                    "created_at": newest_backup.get("created_at"),
                }
                if newest_backup
                else None,
                "backup_directory": self.backup_dir,
            }
        except Exception as e:
            raise Exception(f"Failed to get backup statistics: {e}")

    def schedule_backup(self, schedule_type="daily", max_backups=7):
        """Schedule automatic backups (placeholder for future implementation)."""
        return {
            "message": "Backup scheduling not implemented yet",
            "schedule_type": schedule_type,
            "max_backups": max_backups,
        }
