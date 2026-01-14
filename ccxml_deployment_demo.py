#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's mcanal libraries.
# Interact-IV.com (c) 2013-2016
#
# Contact: softeam@interact-iv.com
# Authors:
#    - JTAG <jtag@interact-iv.com>

"""CCXML Deployment Demo - Testing deployment functionality."""

import sys
import os
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from cccp.conf.deployment_manager import CcxmlDeploymentManager
from cccp.conf.ccxml_config import CcxmlConfigManager
from cccp.conf.ccxml_values import CcxmlValuesManager
from cccp.conf.ccxml_entries import CcxmlEntriesManager
from cccp.conf.ccxml_template import CcxmlTemplateManager


class CcxmlDeploymentDemo(object):
    """Demo class for CCXML deployment functionality."""

    def __init__(self, host="10.199.30.67", project="DEMO_DEPLOY"):
        self.host = host
        self.project = project
        self.config_dir = "/tmp/ccxml_demo"

        # Create config directory
        os.makedirs(self.config_dir, exist_ok=True)

        # Initialize managers
        self.deployment_manager = CcxmlDeploymentManager(
            host, project, method="auto", config_dir=self.config_dir
        )
        self.config_manager = CcxmlConfigManager(host, project, self.config_dir)
        self.values_manager = CcxmlValuesManager(host, project, self.config_dir)
        self.entries_manager = CcxmlEntriesManager(host, project, self.config_dir)
        self.template_manager = CcxmlTemplateManager(host, project, self.config_dir)

        print("=" * 80)
        print("  CCXML DEPLOYMENT DEMO")
        print("=" * 80)
        print(f"  Host: {host}")
        print(f"  Project: {project}")
        print(f"  Config Dir: {self.config_dir}")
        print("=" * 80)

    def demo_1_deployment_readiness(self):
        """Demo: Check deployment readiness."""
        print("\n1. DEPLOYMENT READINESS CHECK")
        print("-" * 50)

        try:
            readiness = self.deployment_manager.validate_deployment_readiness()
            print(f"Overall Ready: {'✅ Yes' if readiness['ready'] else '❌ No'}")

            for check, status in readiness["checks"].items():
                status_icon = "✅" if status else "❌"
                print(f"   {status_icon} {check}: {status}")

            print("✅ Deployment readiness check completed")

        except Exception as e:
            print(f"❌ Readiness check failed: {e}")

    def demo_2_configuration_changes(self):
        """Demo: Apply configuration changes."""
        print("\n2. APPLYING CONFIGURATION CHANGES")
        print("-" * 50)

        try:
            # Update project values
            print("📝 Updating project values...")
            self.values_manager.update_project_values(
                country="FR",
                whitelabel="DEMO_DEPLOY",
                project=self.project,
                pai="<sip:0987654321@deploy.demo>",
            )
            print("   ✅ Project values updated")

            # Add inbound entry
            print("\n➕ Adding inbound entry...")
            self.entries_manager.add_entry(
                name="deploy_demo_inbound",
                scenario="Agent.xml",
                values={
                    "accueil": "welcome_demo.xml",
                    "project_type_cfg": "inbound",
                    "delay_cfg": "3",
                },
            )
            print("   ✅ Inbound entry added")

            # Add outbound entry
            print("\n➕ Adding outbound entry...")
            self.entries_manager.add_outbound_entry("deploy_demo_outbound")
            print("   ✅ Outbound entry added")

            print("✅ Configuration changes applied")

        except Exception as e:
            print(f"❌ Configuration changes failed: {e}")

    def demo_3_template_creation(self):
        """Demo: Create CCXML from template."""
        print("\n3. TEMPLATE CREATION")
        print("-" * 50)

        try:
            # Create standard project
            print("🏗️  Creating standard project CCXML...")
            ccxml_content = self.template_manager.create_standard_project(
                country="DE",
                whitelabel="DEPLOYMENT_DEMO",
                project=f"{self.project}_TEMPLATE",
                pai="<sip:01234567890@template.deploy>",
                include_outbound=True,
            )

            # Save template file
            template_file = self.template_manager.save_project_ccxml(ccxml_content)
            file_size = os.path.getsize(template_file)

            print(f"   ✅ Template created: {template_file}")
            print(f"   📄 File size: {file_size} bytes")

            # Validate template
            print("\n🔍 Validating template...")
            self.config_manager.load_ccxml(template_file)
            valid, message = self.config_manager.validate_ccxml()
            print(f"   {'✅' if valid else '❌'} Validation: {message}")

            print("✅ Template creation completed")

        except Exception as e:
            print(f"❌ Template creation failed: {e}")

    def demo_4_deployment_simulation(self):
        """Demo: Simulate deployment (dry run)."""
        print("\n4. DEPLOYMENT SIMULATION (DRY RUN)")
        print("-" * 50)

        try:
            # Initialize deployment clients
            print("🔧 Initializing deployment clients...")
            self.deployment_manager.initialize_clients()

            # Check connection status
            status = self.deployment_manager.get_deployment_status()
            print(
                f"   CCXML Client: {'✅ Available' if status['ccxml_client_available'] else '❌ Not Available'}"
            )
            print(
                f"   Fallback Client: {'✅ Available' if status['fallback_client_available'] else '❌ Not Available'}"
            )

            # Create deployment plan
            print("\n📋 Creating deployment plan...")
            config_changes = {
                "values": {
                    "country_cfg": "US",
                    "whitelabel_cfg": "DEPLOYMENT_SIM",
                    "project_cfg": self.project,
                    "p_asserted_identity_cfg": "<sip:1234567890@sim.deploy>",
                },
                "entries": {
                    "action": "add",
                    "name": "sim_entry",
                    "scenario": "Agent.xml",
                    "values": {
                        "accueil": "sim_welcome.xml",
                        "project_type_cfg": "inbound",
                    },
                },
            }

            # Simulate deployment without actual deployment
            deployment_plan = self.deployment_manager._create_deployment_plan(
                config_changes
            )
            print(f"   ✅ Plan created: {deployment_plan['deployment_id']}")
            print(f"   📝 Changes: {len(config_changes)} change types")
            print(f"   📄 CCXML File: {deployment_plan['local_ccxml_file']}")

            # Validate plan
            print("\n🔍 Validating deployment plan...")
            validation = self.deployment_manager._validate_configuration(
                deployment_plan
            )
            print(
                f"   {'✅' if validation['valid'] else '❌'} Validation: {validation['valid']}"
            )

            if not validation["valid"]:
                for error in validation["errors"]:
                    print(f"      ❌ Error: {error}")

            print("✅ Deployment simulation completed")

        except Exception as e:
            print(f"❌ Deployment simulation failed: {e}")

    def demo_5_deployment_execution(self):
        """Demo: Execute actual deployment."""
        print("\n5. ACTUAL DEPLOYMENT EXECUTION")
        print("-" * 50)

        try:
            print("⚠️  WARNING: This will attempt actual deployment!")
            print("   Make sure you want to modify server configuration")
            print()

            # Ask for confirmation (simplified for demo)
            print("Proceeding with deployment in 3 seconds...")
            time.sleep(3)

            # Execute deployment
            print("🚀 Executing deployment...")
            success, message, details = self.deployment_manager.deploy_configuration(
                config_changes={
                    "values": {
                        "country_cfg": "FR",
                        "whitelabel_cfg": "ACTUAL_DEPLOY",
                        "project_cfg": self.project,
                        "p_asserted_identity_cfg": "<sip:5555555555@actual.deploy>",
                    }
                },
                backup=True,
                validate=True,
            )

            if success:
                print(f"   ✅ Deployment successful!")
                print(f"   📝 Message: {message}")
                if details:
                    print(
                        f"   📊 Details: Method used - {details.get('method_used', 'Unknown')}"
                    )

                # Show deployment history
                history = self.deployment_manager.get_deployment_history()
                print(f"\n📜 Deployment History: {len(history)} deployments")
                for i, record in enumerate(history[-3:], 1):  # Show last 3
                    print(f"   {i}. {record['deployment_id']} - {record['timestamp']}")

            else:
                print(f"   ❌ Deployment failed!")
                print(f"   💥 Error: {message}")
                return 1

        except Exception as e:
            print(f"💥 Deployment execution error: {e}")
            return 1

        return 0

    def demo_6_status_and_monitoring(self):
        """Demo: Check status and monitoring."""
        print("\n6. STATUS CHECK AND MONITORING")
        print("-" * 50)

        try:
            # Get final status
            status = self.deployment_manager.get_deployment_status()
            print("📊 Final Deployment Status:")
            print(
                f"   CCXML Client: {'✅ Available' if status['ccxml_client_available'] else '❌ Not Available'}"
            )
            print(
                f"   Fallback Client: {'✅ Available' if status['fallback_client_available'] else '❌ Not Available'}"
            )
            print(f"   Current Method: {status['current_method']}")
            print(f"   Total Deployments: {status['deployment_count']}")

            if status["last_deployment"]:
                last = status["last_deployment"]
                print(f"\n📋 Last Deployment Details:")
                print(f"   ID: {last['deployment_id']}")
                print(f"   Timestamp: {last['timestamp']}")
                print(f"   Method: {last.get('method_used', 'Unknown')}")

                attempts = last.get("plan", {}).get("deployment_attempts", [])
                if attempts:
                    print(f"   Attempts: {len(attempts)}")
                    for i, attempt in enumerate(attempts, 1):
                        print(
                            f"     {i}. {attempt.get('method', 'Unknown')} - {'✅ Success' if attempt.get('success') else '❌ Failed'}"
                        )

            # Test fallback client info
            if self.deployment_manager.fallback_client:
                print("\n🔧 Fallback Client Info:")
                server_info = self.deployment_manager.fallback_client.get_server_info()
                if server_info["success"]:
                    print(f"   ✅ ccenter_update available")
                    print(f"   📡 Server: {self.host}")
                    print(f"   🔐 Auth: {self.deployment_manager.auth['login']}")
                else:
                    print(
                        f"   ❌ ccenter_update issue: {server_info.get('error', 'Unknown')}"
                    )

            print("✅ Status check completed")

        except Exception as e:
            print(f"❌ Status check failed: {e}")

    def run_all_demos(self):
        """Run all deployment demos."""
        print("\n🚀 Starting all CCXML deployment demos...")

        demos = [
            self.demo_1_deployment_readiness,
            self.demo_2_configuration_changes,
            self.demo_3_template_creation,
            self.demo_4_deployment_simulation,
            self.demo_5_deployment_execution,
            self.demo_6_status_and_monitoring,
        ]

        for i, demo_func in enumerate(demos, 1):
            try:
                demo_func()
                print(f"\n✨ Demo {i}/6 completed successfully!\n")
            except Exception as e:
                print(f"\n💥 Demo {i}/6 failed: {e}\n")

        print("\n🎉 All deployment demos completed!")
        print("=" * 80)
        print("Summary:")
        print("  - Deployment readiness verification")
        print("  - Configuration changes application")
        print("  - Template creation and validation")
        print("  - Deployment simulation (dry run)")
        print("  - Actual deployment execution")
        print("  - Status check and monitoring")
        print("=" * 80)


def main():
    """Main demo entry point."""
    # Check command line arguments
    host = "10.199.30.67"
    project = "DEMO_DEPLOY"

    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        project = sys.argv[2]

    # Create and run demo
    demo = CcxmlDeploymentDemo(host, project)
    demo.run_all_demos()


if __name__ == "__main__":
    main()
