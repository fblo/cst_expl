#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's mcanal libraries.
# Interact-IV.com (c) 2013-2016
#
# Contact: softeam@interact-iv.com
# Authors:
#    - JTAG <jtag@interact-iv.com>

"""CCCP CCXML Demo Script - Demonstrates all CCXML management features."""

import sys
import os
import json
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from cccp.conf.ccxml_values import CcxmlValuesManager
from cccp.conf.ccxml_entries import CcxmlEntriesManager
from cccp.conf.ccxml_template import CcxmlTemplateManager
from cccp.conf.ccxml_backup import CcxmlBackupManager
from cccp.usage.monitoring_api import CccpMonitoringAPI
from cccp.usage.realtime_monitor import CccpRealtimeMonitor


class CccpDemo(object):
    """Demo class for CCCP CCXML functionality."""

    def __init__(self, host="10.199.30.67", project="DEMO_PROJECT"):
        self.host = host
        self.project = project
        self.backup_dir = "/tmp/cccp_demo"

        # Initialize managers
        self.values_manager = CcxmlValuesManager(host, project, self.backup_dir)
        self.entries_manager = CcxmlEntriesManager(host, project, self.backup_dir)
        self.template_manager = CcxmlTemplateManager(host, project, self.backup_dir)
        self.backup_manager = CcxmlBackupManager(host, project, self.backup_dir)

        print("=" * 80)
        print("  CCP CCP CCXML DEMO SCRIPT")
        print("=" * 80)
        print(f"  Host: {host}")
        print(f"  Project: {project}")
        print(f"  Backup Directory: {self.backup_dir}")
        print("=" * 80)

    def demo_1_values_management(self):
        """Demo: CCXML Values Management."""
        print("\n1. CCXML VALUES MANAGEMENT")
        print("-" * 50)

        try:
            # List current values
            print("📋 Listing current CCXML values...")
            values = self.values_manager.list_all_values()
            for value in values:
                print(f"   {value['path']}: {value['value']} ({value['description']})")

            # Update project values
            print("\n🔧 Updating project configuration values...")
            changes = self.values_manager.update_project_values(
                country="FR",
                whitelabel="DEMO_LABEL",
                project=self.project,
                pai="<sip:0123456789@demo.com>",
            )

            print("   Changes made:")
            for path, change in changes.items():
                print(f"   {path}: {change['old']} → {change['new']}")

            # Set user-specific values
            print("\n👥 Setting user-specific values...")
            user_changes = self.values_manager.set_user_values(
                country_cfg="FR", whitelabel_cfg="DEMO_LABEL"
            )

            print("   User value changes:")
            for path, change in user_changes.items():
                print(f"   {path}: {change['old']} → {change['new']}")

            print("✅ Values management demo completed successfully!")

        except Exception as e:
            print(f"❌ Values management demo failed: {e}")

    def demo_2_entries_management(self):
        """Demo: CCXML Entries Management."""
        print("\n2. CCXML ENTRIES MANAGEMENT")
        print("-" * 50)

        try:
            # List current entries
            print("📋 Listing current CCXML entries...")
            entries = self.entries_manager.get_all_entries()
            print(f"   Found {len(entries)} entries:")
            for entry in entries:
                print(f"   - {entry['name']} → {entry['scenario']}")

            # Add standard inbound entry
            print("\n➕ Adding standard inbound entry...")
            inbound_values = {
                "accueil": "sda_default.xml",
                "project_type_cfg": "inbound",
                "delay_cfg": "0",
            }
            result = self.entries_manager.add_entry(
                name="agent_inbound_demo", scenario="Agent.xml", values=inbound_values
            )
            print(f"   Added entry: {result}")

            # Add outbound entry
            print("\n➕ Adding outbound entry...")
            outbound_result = self.entries_manager.add_outbound_entry(
                "agent_outbound_demo"
            )
            print(f"   Added outbound entry: {outbound_result}")

            # Check outbound support
            print("\n🔍 Checking outbound support...")
            has_outbound = self.entries_manager.check_outbound_support()
            print(f"   Outbound support: {has_outbound}")

            # List scenarios
            print("\n📽️  Listing all scenarios...")
            scenarios = self.entries_manager.list_scenarios()
            print(f"   Available scenarios: {scenarios}")

            print("✅ Entries management demo completed successfully!")

        except Exception as e:
            print(f"❌ Entries management demo failed: {e}")

    def demo_3_template_generation(self):
        """Demo: CCXML Template Generation."""
        print("\n3. CCXML TEMPLATE GENERATION")
        print("-" * 50)

        try:
            # Get standard template
            print("📋 Getting standard CCXML template structure...")
            template = self.template_manager.get_standard_template()
            print(f"   Template root: {template['root']['tag']}")
            print(f"   Sections: {list(template['sections'].keys())}")

            # Create new project CCXML
            print("\n🆕 Creating new project CCXML...")
            ccxml_content = self.template_manager.create_standard_project(
                country="FR",
                whitelabel="DEMO_LABEL",
                project=f"{self.project}_TEMPLATE",
                pai="<sip:0987654321@demo.com>",
                include_outbound=True,
            )

            # Save to file
            ccxml_file = self.template_manager.save_project_ccxml(ccxml_content)
            print(f"   Saved CCXML to: {ccxml_file}")
            print(f"   File size: {os.path.getsize(ccxml_file)} bytes")

            print("✅ Template generation demo completed successfully!")

        except Exception as e:
            print(f"❌ Template generation demo failed: {e}")

    def demo_4_backup_restore(self):
        """Demo: Backup and Restore."""
        print("\n4. BACKUP AND RESTORE")
        print("-" * 50)

        try:
            # Create backup
            print("💾 Creating backup...")
            backup_result = self.backup_manager.create_backup(
                backup_name=f"{self.project}_demo_backup",
                description="Demo backup created by script",
            )
            print(f"   Backup created: {backup_result['backup_name']}")
            print(f"   Location: {backup_result['backup_path']}")

            # List backups
            print("\n📋 Listing available backups...")
            backups = self.backup_manager.list_backups()
            print(f"   Found {len(backups)} backups:")
            for backup in backups[:3]:  # Show first 3
                print(f"   - {backup['backup_name']} ({backup['created_at']})")

            # Get backup details
            if backups:
                print(f"\n🔍 Getting details for: {backups[0]['backup_name']}")
                details = self.backup_manager.get_backup_details(
                    backups[0]["backup_name"]
                )
                print(f"   Project: {details['project']}")
                print(f"   Host: {details['host']}")
                print(f"   Files: {list(details['files'].keys())}")

                # Export backup
                print(f"\n📤 Exporting backup to zip...")
                export_result = self.backup_manager.export_backup(
                    backups[0]["backup_name"]
                )
                print(f"   Exported to: {export_result['export_path']}")
                print(f"   Size: {export_result['size_mb']} MB")

            # Cleanup old backups
            print("\n🧹 Cleaning up old backups (keep 2)...")
            cleanup_result = self.backup_manager.cleanup_old_backups(keep_count=2)
            print(f"   Deleted: {cleanup_result['total_deleted']} backups")
            print(f"   Kept: {cleanup_result['total_kept']} backups")

            # Get statistics
            print("\n📊 Backup storage statistics...")
            stats = self.backup_manager.get_backup_statistics()
            print(f"   Total backups: {stats['total_backups']}")
            print(f"   Total size: {stats['total_size_mb']} MB")

            print("✅ Backup and restore demo completed successfully!")

        except Exception as e:
            print(f"❌ Backup and restore demo failed: {e}")

    def demo_5_monitoring_setup(self):
        """Demo: Monitoring Setup."""
        print("\n5. MONITORING SETUP")
        print("-" * 50)

        try:
            # Initialize monitor
            print("🔍 Initializing real-time monitor...")
            monitor = CccpRealtimeMonitor(
                data_file="/tmp/cccp_demo_monitoring.json", update_interval=5
            )

            # Start monitoring (just for demo, will stop)
            print("▶️  Starting monitoring (5 seconds test)...")
            monitor.start_monitoring()

            # Wait a bit to see if it connects
            import time

            time.sleep(2)

            # Get current data
            print("📊 Getting current monitoring data...")
            data = monitor.get_current_data()
            print(f"   Connected: {data.get('connected', False)}")
            print(f"   Users: {len(data.get('users', []))}")
            print(f"   Queues: {len(data.get('queues', []))}")
            print(f"   Active calls: {data.get('calls', {}).get('active', 0)}")

            # Stop monitoring
            print("⏹️  Stopping monitoring...")
            monitor.stop_monitoring()

            # Initialize API
            print("\n🌐 Initializing monitoring API...")
            api = CccpMonitoringAPI(host=self.host, project=self.project, debug=False)

            print("   API endpoints available:")
            print("   - GET  /api/status")
            print("   - GET  /api/users")
            print("   - GET  /api/queues")
            print("   - GET  /api/calls")
            print("   - GET  /api/sse (Server-Sent Events)")
            print("   - POST /api/ccxml/outbound/upgrade")
            print("   - GET  /api/ccxml/values")
            print("   - POST /api/ccxml/backup/create")

            print("✅ Monitoring setup demo completed successfully!")

        except Exception as e:
            print(f"❌ Monitoring setup demo failed: {e}")

    def demo_6_integration_example(self):
        """Demo: Complete Integration Example."""
        print("\n6. COMPLETE INTEGRATION EXAMPLE")
        print("-" * 50)

        try:
            # Step 1: Create backup before changes
            print("📦 Step 1: Creating pre-change backup...")
            pre_backup = self.backup_manager.create_backup(
                backup_name=f"{self.project}_pre_integration",
                description="Backup before integration demo",
            )

            # Step 2: Configure project values
            print("\n⚙️  Step 2: Configuring project values...")
            self.values_manager.update_project_values(
                country="FR",
                whitelabel="INTEGRATION_DEMO",
                project=self.project,
                pai="<sip:integration@demo.com>",
            )

            # Step 3: Setup entries with inbound and outbound
            print("\n📞 Step 3: Setting up call routing entries...")

            # Add inbound entry
            self.entries_manager.add_entry(
                name="integration_inbound",
                scenario="Agent.xml",
                values={
                    "accueil": "welcome.xml",
                    "project_type_cfg": "inbound",
                    "delay_cfg": "5",
                },
            )

            # Add outbound entry
            self.entries_manager.add_outbound_entry("integration_outbound")

            # Step 4: Upgrade to outbound support
            print("\n🔄 Step 4: Ensuring outbound support...")
            upgrade_result = self.entries_manager.upgrade_to_outbound()
            print(f"   Outbound upgrade result: {upgrade_result}")

            # Step 5: Create post-change backup
            print("\n💾 Step 5: Creating post-change backup...")
            post_backup = self.backup_manager.create_backup(
                backup_name=f"{self.project}_post_integration",
                description="Backup after integration demo",
            )

            # Step 6: Generate project report
            print("\n📊 Step 6: Generating project report...")

            # Get current state
            entries = self.entries_manager.get_all_entries()
            values = self.values_manager.get_current_values()
            backups = self.backup_manager.list_backups()

            report = {
                "project": self.project,
                "timestamp": datetime.now().isoformat(),
                "configuration": {
                    "entries_count": len(entries),
                    "entries": [e["name"] for e in entries],
                    "values": values,
                    "outbound_enabled": self.entries_manager.check_outbound_support(),
                },
                "backups": {
                    "total": len(backups),
                    "latest": backups[0]["backup_name"] if backups else None,
                    "pre_integration": pre_backup["backup_name"],
                    "post_integration": post_backup["backup_name"],
                },
            }

            # Save report
            report_file = os.path.join(
                self.backup_dir, f"{self.project}_integration_report.json"
            )
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)

            print(f"   Integration report saved to: {report_file}")
            print(f"   Entries configured: {len(entries)}")
            print(f"   Outbound enabled: {report['configuration']['outbound_enabled']}")

            print("✅ Complete integration demo finished successfully!")

        except Exception as e:
            print(f"❌ Integration demo failed: {e}")

    def run_all_demos(self):
        """Run all demo functions."""
        print("\n🚀 Starting all CCCP CCXML demos...")

        demos = [
            self.demo_1_values_management,
            self.demo_2_entries_management,
            self.demo_3_template_generation,
            self.demo_4_backup_restore,
            self.demo_5_monitoring_setup,
            self.demo_6_integration_example,
        ]

        for i, demo_func in enumerate(demos, 1):
            try:
                demo_func()
                print(f"\n✨ Demo {i}/6 completed successfully!\n")
            except Exception as e:
                print(f"\n💥 Demo {i}/6 failed: {e}\n")

        print("\n🎉 All demos completed!")
        print("=" * 80)


def main():
    """Main demo entry point."""
    # Check command line arguments
    host = "10.199.30.67"
    project = "DEMO_PROJECT"

    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        project = sys.argv[2]

    # Create and run demo
    demo = CccpDemo(host, project)

    if len(sys.argv) > 3:
        # Run specific demo
        demo_num = int(sys.argv[3])
        demo_methods = [
            None,  # Placeholder for 1-based indexing
            demo.demo_1_values_management,
            demo.demo_2_entries_management,
            demo.demo_3_template_generation,
            demo.demo_4_backup_restore,
            demo.demo_5_monitoring_setup,
            demo.demo_6_integration_example,
        ]

        if 1 <= demo_num <= len(demo_methods) - 1:
            demo_methods[demo_num]()
        else:
            print(f"Invalid demo number. Available: 1-{len(demo_methods) - 1}")
    else:
        # Run all demos
        demo.run_all_demos()


if __name__ == "__main__":
    main()
