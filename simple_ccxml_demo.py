#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's mcanal libraries.
# Interact-IV.com (c) 2013-2016
#
# Contact: softeam@interact-iv.com
# Authors:
#    - JTAG <jtag@interact-iv.com>

"""Simplified CCXML Deployment Demo - Testing deployment functionality."""

import sys
import os
import time
import xml.etree.ElementTree as ET
from datetime import datetime


class SimpleCcxmlManager(object):
    """Simple CCXML manager for demo."""

    def __init__(self, host, project, config_dir="/tmp"):
        self.host = host
        self.project = project
        self.config_dir = config_dir
        self.ccxml_file = os.path.join(config_dir, f"{project}_Ccxml.xml")

    def create_simple_ccxml(
        self, country="FR", whitelabel="DEMO", project_cfg=None, pai=None
    ):
        """Create simple CCXML configuration."""
        root = ET.Element("com.consistent.ccenter.ccxml.ccenter_ccxml")
        root.set("id", "_1")
        root.set("class_name", "ccenter_ccxml")

        # Add users_values section
        users_values = ET.SubElement(root, "users_values")
        if country:
            ET.SubElement(
                users_values,
                "com.consistent.protocol.consistent_protocol_named_object_value_string",
                id="_country",
                name="country_cfg",
                value=country,
            )
        if whitelabel:
            ET.SubElement(
                users_values,
                "com.consistent.protocol.consistent_protocol_named_object_value_string",
                id="_whitelabel",
                name="whitelabel_cfg",
                value=whitelabel,
            )
        if project_cfg:
            ET.SubElement(
                users_values,
                "com.consistent.protocol.consistent_protocol_named_object_value_string",
                id="_project",
                name="project_cfg",
                value=project_cfg,
            )
        if pai:
            ET.SubElement(
                users_values,
                "com.consistent.protocol.consistent_protocol_named_object_value_string",
                id="_pai",
                name="p_asserted_identity_cfg",
                value=pai,
            )

        # Add entries_values section
        entries_values = ET.SubElement(root, "entries_values")
        if country:
            ET.SubElement(
                entries_values,
                "com.consistent.protocol.consistent_protocol_named_object_value_string",
                id="_country2",
                name="country_cfg",
                value=country,
            )
        if whitelabel:
            ET.SubElement(
                entries_values,
                "com.consistent.protocol.consistent_protocol_named_object_value_string",
                id="_whitelabel2",
                name="whitelabel_cfg",
                value=whitelabel,
            )
        if project_cfg:
            ET.SubElement(
                entries_values,
                "com.consistent.protocol.consistent_protocol_named_object_value_string",
                id="_project2",
                name="project_cfg",
                value=project_cfg,
            )
        if pai:
            ET.SubElement(
                entries_values,
                "com.consistent.protocol.consistent_protocol_named_object_value_string",
                id="_pai2",
                name="p_asserted_identity_cfg",
                value=pai,
            )

        # Add entrys section
        entrys = ET.SubElement(root, "entrys")

        # Add inbound entry
        ET.SubElement(
            entrys,
            "ccenter_ccxml_entry",
            id="_inbound",
            name="agent_inbound",
            scenario="Agent.xml",
            disconnected_timeout="0",
        )

        # Add outbound entry
        ET.SubElement(
            entrys,
            "ccenter_ccxml_entry",
            id="_outbound",
            name="agent_outbound",
            scenario="Outbound.xml",
            disconnected_timeout="0",
        )

        tree = ET.ElementTree(root)
        tree.write(self.ccxml_file, encoding="ISO-8859-1", xml_declaration=True)

        return self.ccxml_file

    def validate_ccxml(self):
        """Simple CCXML validation."""
        if not os.path.exists(self.ccxml_file):
            return False, "CCXML file not found"

        try:
            tree = ET.parse(self.ccxml_file)
            root = tree.getroot()

            # Basic structure checks
            if root.tag != "com.consistent.ccenter.ccxml.ccenter_ccxml":
                return False, "Invalid root element"

            if root.find(".//entrys") is None:
                return False, "Missing entrys section"

            return True, "Validation passed"
        except ET.ParseError as e:
            return False, f"XML parsing error: {e}"


class SimpleDeploymentDemo(object):
    """Simplified deployment demo."""

    def __init__(self, host="10.199.30.67", project="DEMO_DEPLOY"):
        self.host = host
        self.project = project
        self.config_dir = "/tmp/ccxml_demo"

        # Create config directory
        os.makedirs(self.config_dir, exist_ok=True)

        # Initialize simple CCXML manager
        self.ccxml_manager = SimpleCcxmlManager(host, project, self.config_dir)

        print("=" * 80)
        print("  SIMPLIFIED CCXML DEPLOYMENT DEMO")
        print("=" * 80)
        print(f"  Host: {host}")
        print(f"  Project: {project}")
        print(f"  Config Dir: {self.config_dir}")
        print("=" * 80)

    def demo_1_simple_deployment(self):
        """Demo: Simple deployment workflow."""
        print("\n1. SIMPLE CCXML CREATION AND DEPLOYMENT")
        print("-" * 50)

        try:
            # Create CCXML with demo configuration
            print("🏗️  Creating CCXML with demo configuration...")
            ccxml_file = self.ccxml_manager.create_simple_ccxml(
                country="FR",
                whitelabel="SIMPLE_DEMO",
                project_cfg=self.project,
                pai="<sip:01234567890@simple.demo>",
            )

            file_size = os.path.getsize(ccxml_file)
            print(f"   ✅ CCXML created: {ccxml_file}")
            print(f"   📄 File size: {file_size} bytes")

            # Validate CCXML
            print("\n🔍 Validating created CCXML...")
            valid, message = self.ccxml_manager.validate_ccxml()
            print(f"   {'✅' if valid else '❌'} Validation: {message}")

            if not valid:
                return 1

            # Show deployment methods
            print("\n📋 Deployment Options:")
            print("   1. CCXML Protocol (port 20102) - Preferred method")
            print("   2. ccenter_update (port 20000) - Fallback method")
            print("   3. Manual deployment")
            print()

            print("⚠️  NOTE: This demo shows the CCXML creation workflow.")
            print("   For actual deployment, you would need:")
            print("   - CCXML client connection to port 20102")
            print("   - Or ccenter_update tool for port 20000")
            print("   - Proper authentication credentials")
            print()

            # Simulate deployment methods
            print("🔄 Simulating deployment methods...")

            # Method 1: CCXML Protocol
            print("\n📡 Method 1 - CCXML Protocol Simulation:")
            print("   ✅ Connection to {self.host}:20102")
            print("   ✅ Authentication with deployment permissions")
            print("   ✅ Sending configuration via binary protocol")
            print("   ✅ Receiving confirmation from server")
            print("   📋 Status: AVAILABLE (would work with proper server)")

            # Method 2: ccenter_update fallback
            print("\n🛠️  Method 2 - ccenter_update Fallback:")
            print("   ✅ Using ccenter_update binary")
            print(
                "   ✅ Command: ccenter_update -login admin -password admin -server {self.host} 20000"
            )
            print("   ✅ Command: -path /db/projects/{self.project}/Ccxml.xml")
            print("   ✅ Command: -file {ccxml_file} -create")
            print("   📋 Status: AVAILABLE (if ccenter_update is installed)")

            # Method 3: Manual deployment
            print("\n📝 Method 3 - Manual Deployment:")
            print("   ✅ File created at: {ccxml_file}")
            print(
                "   ✅ Copy to server: scp {ccxml_file} {self.host}:/db/projects/{self.project}/"
            )
            print("   ✅ Or use web interface if available")
            print("   📋 Status: READY")

            print("\n✅ Simple deployment demo completed successfully!")

        except Exception as e:
            print(f"❌ Simple deployment demo failed: {e}")
            return 1

        return 0

    def demo_2_deployment_info(self):
        """Demo: Show deployment information."""
        print("\n2. DEPLOYMENT METHODS INFORMATION")
        print("-" * 50)

        print("📊 CCXML Protocol Method (Port 20102):")
        print("   ✅ Direct TCP connection to CCCP CCXML process")
        print("   ✅ Uses existing CCCP library (cccp.async.ccxml)")
        print("   ✅ Binary protocol with 4-byte headers")
        print("   ✅ Message-based communication")
        print("   ✅ Built-in validation and error handling")
        print("   ✅ Real-time deployment feedback")
        print("   ❌ Requires: cccp.async.ccxml module working")

        print("\n🛠️  ccenter_update Method (Port 20000):")
        print("   ✅ Standard tool for CCCP file operations")
        print("   ✅ Uses admin/admin authentication")
        print("   ✅ File upload/download capabilities")
        print("   ✅ Backup and rollback support")
        print("   ✅ Wide compatibility")
        print("   ❌ Requires: ccenter_update binary installed")
        print("   ❌ Requires: Proper file permissions")

        print("\n🎯 Recommended Deployment Strategy:")
        print("   1. Try CCXML protocol first (port 20102)")
        print("   2. Fallback to ccenter_update (port 20000)")
        print("   3. Always backup before deployment")
        print("   4. Validate configuration before deployment")
        print("   5. Use monitoring to verify deployment success")

        print("\n📋 Required for Production Use:")
        print("   ✅ Proper authentication credentials")
        print("   ✅ Network connectivity to CCCP server")
        print("   ✅ File system permissions")
        print("   ✅ Backup procedures")
        print("   ✅ Rollback procedures")
        print("   ✅ Monitoring and alerting")

    def run_demos(self):
        """Run all simplified demos."""
        demos = [self.demo_1_simple_deployment, self.demo_2_deployment_info]

        for i, demo_func in enumerate(demos, 1):
            try:
                demo_func()
                print(f"\n✨ Demo {i}/2 completed successfully!\n")
            except Exception as e:
                print(f"\n💥 Demo {i}/2 failed: {e}\n")

        print("\n🎉 All simplified deployment demos completed!")
        print("=" * 80)
        print("Summary:")
        print("  - CCXML creation and validation")
        print("  - Deployment method simulation")
        print("  - Method comparison and recommendations")
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
    demo = SimpleDeploymentDemo(host, project)
    demo.run_demos()


if __name__ == "__main__":
    main()
