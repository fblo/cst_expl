#!/usr/bin/env python3
import sys

sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/src")
sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/ivcommons/src")

try:
    from cccp.async_module.dispatch import DispatchClient

    print("OK - DispatchClient imported")
except Exception as e:
    import traceback

    print(f"ERROR: {e}")
    traceback.print_exc()
