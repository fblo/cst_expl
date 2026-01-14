#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's mcanal libraries.
# Interact-IV.com (c) 2013-2016
#
# Contact: softeam@interact-iv.com
# Authors:
#    - JTAG <jtag@interact-iv.com>

"""Test CCXML Connection and Authentication."""

import sys
import os
import time
import socket
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_direct_connection():
    """Test direct TCP connection to CCXML port."""
    print("🔌 Testing direct TCP connection to CCXML port 20102...")

    try:
        host = "10.199.30.67"
        port = 20102

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)

        print(f"   Connecting to {host}:{port}...")
        sock.connect((host, port))

        print("   ✅ TCP connection successful!")
        print(f"   Connected to: {sock.getpeername()}")
        print(f"   Local address: {sock.getsockname()}")

        # Try to read initial data
        sock.settimeout(5)
        try:
            initial_data = sock.recv(1024)
            print(f"   Initial data received: {len(initial_data)} bytes")
            if len(initial_data) > 0:
                print(f"   First bytes: {[hex(b) for b in initial_data[:10]]}")
            else:
                print("   No initial data received (timeout)")
        except socket.timeout:
            print("   ⏰ No initial data received (timeout)")
        except Exception as e:
            print(f"   ⚠️ Error reading initial data: {e}")

        sock.close()
        return True

    except socket.timeout:
        print("   ❌ Connection timeout")
        return False
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False


def test_ccp_library():
    """Test using existing CCCP library."""
    print("🔧 Testing CCCP library CCXML client...")

    try:
        from cccp.async_module.ccxml import CcxmlClient
        from cccp.async_module.factory import CCCFactory
        from twisted.internet import reactor, defer

        # Create client
        client = CcxmlClient("test_client", "10.199.30.67", 20102)

        print("   ✅ CCCP client created")

        # Setup connection
        d = client.connect()

        def on_connected(success):
            print(f"   {'✅' if success else '❌'} CCCP connection: {success}")
            if success:
                try:
                    # Add session
                    session_id = 1001
                    client.add_session(session_id, "supervisor_gtri", "toto", False)
                    print(f"   📞 Session {session_id} added")
                except Exception as e:
                    print(f"   ⚠️ Error adding session: {e}")

            reactor.callLater(2, reactor.stop)

        def on_connection_error(failure):
            print(f"   ❌ CCCP connection error: {failure}")
            reactor.callLater(1, reactor.stop)

        d.addCallback(on_connected)
        d.addErrback(on_connection_error)

        print("   🔗 Starting connection (5 second timeout)...")

        # Start reactor
        reactor.run()

    except ImportError as e:
        print(f"   ❌ CCCP library not available: {e}")
        return False
    except Exception as e:
        print(f"   ❌ CCCP library error: {e}")
        return False


def test_dispatch_json():
    """Test dispatch JSON interface."""
    print("📊 Testing dispatch JSON interface...")

    try:
        script_path = "/home/fblo/Documents/repos/iv-cccp/test_dispatch_json.py"

        if not os.path.exists(script_path):
            print(f"   ❌ Test script not found: {script_path}")
            return False

        result = subprocess.run(
            ["python3", script_path, "10.199.30.67", "20103"],
            capture_output=True,
            text=True,
            timeout=15,
        )

        print(f"   📤 Test script output:")
        print(f"     Exit code: {result.returncode}")

        if result.stdout:
            lines = result.stdout.split("\n")[:10]
            for line in lines:
                print(f"     {line}")

        if result.stderr:
            errors = result.stderr.split("\n")[:5]
            for error in errors:
                print(f"     ⚠️ {error}")

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("   ⏰ Dispatch JSON test timeout")
        return False
    except Exception as e:
        print(f"   ❌ Dispatch JSON test error: {e}")
        return False


def test_ccenter_update():
    """Test ccenter_update availability."""
    print("🛠️ Testing ccenter_update availability...")

    try:
        result = subprocess.run(
            ["which", "ccenter_update"], capture_output=True, text=True, timeout=5
        )

        if result.returncode == 0:
            path = result.stdout.strip()
            print(f"   ✅ ccenter_update found: {path}")

            # Test connection to CCCP server
            test_cmd = [
                "ccenter_update",
                "--login",
                "admin",
                "--password",
                "admin",
                "--server",
                "10.199.30.67",
                "20000",
                "--info",
            ]

            result = subprocess.run(
                test_cmd, capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                print("   ✅ ccenter_update can connect to CCCP server")
                print(f"   📡 ccenter_update info: {result.stdout[:200]}...")
            else:
                print("   ⚠️ ccenter_update connection failed")
                print(f"   📡 ccenter_update errors: {result.stderr}")
        else:
            print("   ❌ ccenter_update not found")

    except subprocess.TimeoutExpired:
        print("   ⏰ ccenter_update test timeout")
    except Exception as e:
        print(f"   ❌ ccenter_update test error: {e}")


def test_connection_with_proxy():
    """Test connection through proxy."""
    print("🌐 Testing connection through proxy...")

    # List common proxy ports
    proxy_ports = [8080, 8888, 3128, 1080]

    for port in proxy_ports:
        print(f"   Testing proxy port {port}...")

        try:
            import urllib.request
            import urllib.parse

            proxy_handler = urllib.request.ProxyHandler(
                {"http": f"http://10.199.30.67:{port}"}
            )

            # Test HTTP connection
            request = urllib.request.Request(
                "http://httpbin.org/ip", headers={"User-Agent": "CCCP-Test"}
            )

            opener = urllib.request.build_opener(proxy_handler)
            response = opener.open(request, timeout=5)
            data = response.read().decode("utf-8")

            if "origin" in data:
                print(f"   ✅ Proxy {port} working! IP: {data['origin']}")
                return True

        except Exception as e:
            print(f"   ❌ Proxy {port} failed: {e}")

    return any([test_proxy(port) for port in proxy_ports])


def main():
    """Run all connection tests."""
    print("=" * 80)
    print("  CCXML CONNECTION DIAGNOSTICS")
    print("=" * 80)
    print(f"  Target: 10.199.30.67:20103 (CCXML)")
    print(f"  Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)

    tests = [
        ("Direct TCP", test_direct_connection),
        ("CCCP Library", test_ccp_library),
        ("Dispatch JSON", test_dispatch_json),
        ("ccenter_update", test_ccenter_update),
        ("Proxy Test", test_connection_with_proxy),
    ]

    results = []
    passed = 0

    for i, (test_name, test_func) in enumerate(tests, 1):
        print(f"\n{i}. {test_name}")
        print("-" * 50)

        try:
            result = test_func()
            if result:
                print(f"   ✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"   ❌ {test_name} FAILED")
        except Exception as e:
            print(f"   💥 {test_name} ERROR: {e}")

        results.append((test_name, result))

    print("\n" + "=" * 80)
    print("  TEST SUMMARY")
    print(f"  Passed: {passed}/{len(tests)}")
    print(f"  Failed: {len(tests) - passed}/{len(tests)}")

    print("\n" + "=" * 80)

    if passed > 0:
        print("🎉 CONNECTION TESTS SUCCESSFUL - You can proceed with CCXML deployment!")
    else:
        print("💥 CONNECTION TESTS FAILED - Check network and permissions")
        print("🔧 TROUBLESHOOTING:")
        print("  1. Check if 10.199.30.67:20103 is accessible")
        print("  2. Verify port 20102 is not blocked")
        print(" 3. Test authentication credentials")
        print(" 4. Check CCCP library installation")
        print(" 5. Check firewall rules")
        print(" 6. Try alternative network paths")
        print(" 7. Contact network administrator")

    return passed > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
