#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's mcanal libraries.
# Interact-IV.com (c) 2013-2016
#
# Contact: softeam@interact-iv.com
# Authors:
#    - JTAG <jtag@interact-iv.com>

"""CCXML Deployment CLI Tool."""

import sys
import os
import argparse
import json
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from cccp.conf.deployment_manager import CcxmlDeploymentManager
from cccp.conf.ccxml_config import CcxmlConfigManager
from cccp.conf.ccxml_values import CcxmlValuesManager
from cccp.conf.ccxml_entries import CcxmlEntriesManager
from cccp.conf.ccxml_template import CcxmlTemplateManager


def main():
    """Main deployment CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CCXML Deployment Tool - Deploy configurations to CCCP server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Deploy current configuration
  %(prog)s --host 10.199.30.67 --project DEMO_PROJECT deploy

  # Deploy with validation only
  %(prog)s --host 10.199.30.67 --project DEMO_PROJECT validate --file config.xml

  # Deploy from template
  %(prog)s --host 10.199.30.67 --project DEMO_PROJECT deploy-template --country FR --whitelabel DEMO

  # Deploy specific CCXML file
  %(prog)s --host 10.199.30.67 --project DEMO_PROJECT deploy-file --file my_config.xml
        """,
    )

    parser.add_argument(
        "--host",
        default="10.199.30.67",
        help="CCCP host address (default: 10.199.30.67)",
    )
    parser.add_argument("--project", required=True, help="Project name (required)")
    parser.add_argument(
        "--method",
        choices=["auto", "ccxml", "ccenter"],
        default="auto",
        help="Deployment method (default: auto)",
    )
    parser.add_argument("--login", default="admin", help="Login name (default: admin)")
    parser.add_argument("--password", default="admin", help="Password (default: admin)")
    parser.add_argument("--config-dir", default="/tmp", help="Configuration directory")
    parser.add_argument(
        "--no-backup", action="store_true", help="Skip backup before deployment"
    )
    parser.add_argument(
        "--no-validate", action="store_true", help="Skip validation before deployment"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    # Command subparsers
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy current configuration")
    deploy_parser.add_argument(
        "--dry-run", action="store_true", help="Dry run (validate and backup only)"
    )

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate configuration")
    validate_parser.add_argument("--file", help="CCXML file to validate")

    # Deploy template command
    deploy_template_parser = subparsers.add_parser(
        "deploy-template", help="Deploy from template"
    )
    deploy_template_parser.add_argument("--country", required=True, help="Country code")
    deploy_template_parser.add_argument(
        "--whitelabel", required=True, help="Whitelabel"
    )
    deploy_template_parser.add_argument("--project-cfg", help="Project configuration")
    deploy_template_parser.add_argument("--pai", help="P-Asserted-Identity")
    deploy_template_parser.add_argument(
        "--include-outbound",
        action="store_true",
        default=True,
        help="Include outbound support",
    )

    # Deploy file command
    deploy_file_parser = subparsers.add_parser(
        "deploy-file", help="Deploy specific CCXML file"
    )
    deploy_file_parser.add_argument(
        "--file", required=True, help="CCXML file to deploy"
    )

    # Status command
    status_parser = subparsers.add_parser("status", help="Check deployment status")

    # Test command
    test_parser = subparsers.add_parser("test", help="Test connection to server")
    test_parser.add_argument(
        "--test-ccxml", action="store_true", help="Test CCXML connection"
    )
    test_parser.add_argument(
        "--test-fallback", action="store_true", help="Test fallback connection"
    )

    args = parser.parse_args()

    # Initialize deployment manager
    deployment_manager = CcxmlDeploymentManager(
        args.host,
        args.project,
        method=args.method,
        auth={"login": args.login, "password": args.password},
        config_dir=args.config_dir,
    )

    try:
        if args.command == "deploy":
            return cmd_deploy(deployment_manager, args)
        elif args.command == "validate":
            return cmd_validate(deployment_manager, args)
        elif args.command == "deploy-template":
            return cmd_deploy_template(deployment_manager, args)
        elif args.command == "deploy-file":
            return cmd_deploy_file(deployment_manager, args)
        elif args.command == "status":
            return cmd_status(deployment_manager, args)
        elif args.command == "test":
            return cmd_test(deployment_manager, args)
        else:
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 130
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


def cmd_deploy(deployment_manager, args):
    """Deploy current configuration."""
    print(f"🚀 Deploying configuration to {args.project} on {args.host}")
    print(f"   Method: {args.method}")
    print(f"   Backup: {'No' if args.no_backup else 'Yes'}")
    print(f"   Validate: {'No' if args.no_validate else 'Yes'}")

    if args.dry_run:
        print("   ⚠️  DRY RUN MODE - No actual deployment")

    print()

    try:
        # Initialize clients
        deployment_manager.initialize_clients()

        # Check readiness
        readiness = deployment_manager.validate_deployment_readiness()
        if not readiness["ready"]:
            print("❌ System not ready for deployment:")
            for check, status in readiness["checks"].items():
                status_icon = "✅" if status else "❌"
                print(f"   {status_icon} {check}: {status}")
            return 1

        print("✅ System ready for deployment")

        # Execute deployment
        success, message, details = deployment_manager.deploy_configuration(
            backup=not args.no_backup, validate=not args.no_validate
        )

        if success:
            print(f"✅ Deployment successful: {message}")
            if details:
                print(f"   Details: {details}")
        else:
            print(f"❌ Deployment failed: {message}")
            return 1

    except Exception as e:
        print(f"💥 Deployment error: {e}")
        return 1

    return 0


def cmd_validate(deployment_manager, args):
    """Validate configuration."""
    if args.file:
        print(f"🔍 Validating CCXML file: {args.file}")

        try:
            # Load and validate file
            config_manager = deployment_manager.config_manager
            config_manager.load_ccxml(args.file)
            valid, message = config_manager.validate_ccxml()

            if valid:
                print(f"✅ Configuration is valid: {message}")
            else:
                print(f"❌ Configuration is invalid: {message}")
                return 1

        except Exception as e:
            print(f"❌ Validation error: {e}")
            return 1
    else:
        print("❌ No file specified for validation")
        return 1

    return 0


def cmd_deploy_template(deployment_manager, args):
    """Deploy from template."""
    print(f"🏗️  Creating deployment from template")
    print(f"   Country: {args.country}")
    print(f"   Whitelabel: {args.whitelabel}")
    print(f"   Project: {args.project_cfg or args.project}")

    try:
        # Create template
        template_manager = deployment_manager.template_manager

        ccxml_content = template_manager.create_standard_project(
            country=args.country,
            whitelabel=args.whitelabel,
            project=args.project_cfg or args.project,
            pai=args.pai,
            include_outbound=args.include_outbound,
        )

        # Save template to file
        template_file = os.path.join(args.config_dir, f"{args.project}_template.xml")
        with open(template_file, "w") as f:
            f.write(ccxml_content)

        print(f"✅ Template created: {template_file}")

        # Deploy the template
        config_changes = {"ccxml_file": template_file}

        success, message, details = deployment_manager.deploy_configuration(
            config_changes=config_changes, backup=True, validate=True
        )

        if success:
            print(f"✅ Template deployment successful: {message}")
        else:
            print(f"❌ Template deployment failed: {message}")
            return 1

    except Exception as e:
        print(f"💥 Template deployment error: {e}")
        return 1

    return 0


def cmd_deploy_file(deployment_manager, args):
    """Deploy specific CCXML file."""
    print(f"📄 Deploying CCXML file: {args.file}")

    try:
        if not os.path.exists(args.file):
            print(f"❌ File not found: {args.file}")
            return 1

        # Validate file first
        config_manager = deployment_manager.config_manager
        config_manager.load_ccxml(args.file)
        valid, message = config_manager.validate_ccxml()

        if not valid:
            print(f"❌ Invalid CCXML file: {message}")
            return 1

        print("✅ CCXML file is valid")

        # Deploy the file
        config_changes = {"ccxml_file": args.file}

        success, message, details = deployment_manager.deploy_configuration(
            config_changes=config_changes,
            backup=True,
            validate=False,  # Already validated
        )

        if success:
            print(f"✅ File deployment successful: {message}")
        else:
            print(f"❌ File deployment failed: {message}")
            return 1

    except Exception as e:
        print(f"💥 File deployment error: {e}")
        return 1

    return 0


def cmd_status(deployment_manager, args):
    """Check deployment status."""
    print(f"📊 Deployment status for {args.project} on {args.host}")
    print()

    try:
        # Initialize clients
        deployment_manager.initialize_clients()

        # Check readiness
        readiness = deployment_manager.validate_deployment_readiness()
        print("System Readiness:")
        for check, status in readiness["checks"].items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {check}: {status}")

        print()

        # Get deployment status
        status = deployment_manager.get_deployment_status()
        print("Deployment Status:")
        print(
            f"   CCXML Client: {'Available' if status['ccxml_client_available'] else 'Not Available'}"
        )
        print(
            f"   Fallback Client: {'Available' if status['fallback_client_available'] else 'Not Available'}"
        )
        print(f"   Current Method: {status['current_method']}")
        print(f"   Deployment Count: {status['deployment_count']}")

        if status["last_deployment"]:
            last = status["last_deployment"]
            print()
            print("Last Deployment:")
            print(f"   ID: {last['deployment_id']}")
            print(f"   Timestamp: {last['timestamp']}")
            print(f"   Method: {last.get('method_used', 'Unknown')}")

        print()
        print("✅ Status check completed")

    except Exception as e:
        print(f"💥 Status check error: {e}")
        return 1

    return 0


def cmd_test(deployment_manager, args):
    """Test connection to server."""
    print(f"🔧 Testing connection to {args.host}")

    try:
        # Initialize clients
        deployment_manager.initialize_clients()

        success_count = 0
        total_tests = 0

        if args.test_ccxml or not args.test_fallback:
            total_tests += 1
            print("\nTesting CCXML connection (port 20102)...")
            if deployment_manager.ccxml_client:
                print("✅ CCXML client initialized")
                success_count += 1
            else:
                print("❌ CCXML client failed to initialize")

        if args.test_fallback or not args.test_ccxml:
            total_tests += 1
            print("\nTesting ccenter_update fallback (port 20000)...")
            if deployment_manager.fallback_client:
                status = deployment_manager.fallback_client.get_server_info()
                if status["success"]:
                    print("✅ ccenter_update connection successful")
                    success_count += 1
                else:
                    print(f"❌ ccenter_update failed: {status.get('error', 'Unknown')}")
            else:
                print("❌ ccenter_update client failed to initialize")

        print(f"\n📊 Test Results: {success_count}/{total_tests} successful")

        if success_count == total_tests:
            print("✅ All tests passed")
            return 0
        else:
            print("❌ Some tests failed")
            return 1

    except Exception as e:
        print(f"💥 Connection test error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
