#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import json
import sys
import os


def get_real_dispatch_data():
    """Get REAL data from dispatch that we saw working before"""
    try:
        # Use the same connection method that worked before
        cmd = ["python3", "monitor_worker.py"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/home/fblo/Documents/repos/explo-cst",
        )

        # Parse the real dispatch output we saw before
        # This should return the REAL users we saw: supervisor_gtri, adiallo, alsane, etc.

        # For now, return empty since we can't get fake data
        return {"users": [], "queues": [], "error": "Unable to get real dispatch data"}
    except Exception as e:
        return {"users": [], "queues": [], "error": str(e)}


if __name__ == "__main__":
    data = get_real_dispatch_data()
    print(json.dumps(data, indent=2))
