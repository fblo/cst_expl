#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's mcanal libraries.
# Interact-IV.com (c) 2013-2016
#
# Contact: softeam@interact-iv.com
# Authors:
#    - JTAG <jtag@interact-iv.com>

"""CCCP CCXML API Server - Start the complete CCXML management API."""

import sys
import os
import argparse

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from cccp.usage.monitoring_api import CccpMonitoringAPI


def main():
    """Start the CCCP CCXML API server."""
    parser = argparse.ArgumentParser(description="CCCP CCXML API Server")
    parser.add_argument("--host", default="10.199.30.67", help="CCCP host address")
    parser.add_argument("--project", default="default", help="Project name")
    parser.add_argument("--port", type=int, default=5000, help="API server port")
    parser.add_argument("--bind", default="0.0.0.0", help="Bind address")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument(
        "--no-monitoring", action="store_true", help="Disable auto-start monitoring"
    )
    parser.add_argument(
        "--deployment-method",
        choices=["auto", "ccxml", "ccenter"],
        default="auto",
        help="Deployment method for CCXML changes",
    )

    args = parser.parse_args()

    print("=" * 80)
    print("  CCCP CCXML API SERVER")
    print("=" * 80)
    print(f"  CCCP Host: {args.host}")
    print(f"  Project: {args.project}")
    print(f"  API Port: {args.port}")
    print(f"  Debug Mode: {args.debug}")
    print(f"  Auto Monitoring: {not args.no_monitoring}")
    print("=" * 80)

    # Create API instance
    api = CccpMonitoringAPI(host=args.host, project=args.project, debug=args.debug)

    # Set deployment method if specified
    if hasattr(api.deployment_manager, "method"):
        api.deployment_manager.method = args.deployment_method
        print(f"📝 Deployment method set to: {args.deployment_method}")

    # Start server
    try:
        api.start(
            host=args.bind, port=args.port, auto_start_monitoring=not args.no_monitoring
        )
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped by user")
        api.stop()
    except Exception as e:
        print(f"❌ Server error: {e}")
        api.stop()


if __name__ == "__main__":
    main()
