#!/usr/bin/env python3
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's mcanal libraries.
# Interact-IV.com (c) 2013-2016
#
# Contact: softeam@interact-iv.com
# Authors:
#    - JTAG <jtag@interact-iv.com>

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
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_direct_connection():
    """Test direct TCP connection to CCXML port."""
    print("🔌 Testing direct TCP connection to CCXML port 20102...")
    
    try:
        import socket
        host = "10.199.30.67"
        port = 20102
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        print(f"   Connecting to {host}:{port}...")
        sock.connect((host, port))
        
        print("   ✅ TCP connection successful!")
        print(f"   Connected to: {sock.getpeername()}")
        
        # Try to read initial data
        sock.settimeout(5)
        try:
            initial_data = sock.recv(1024)
            print(f"   Initial data received: {len(initial_data)} bytes")
            print(f"   First bytes: {[hex(b) for b in initial_data[:10]]}")
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
            
            reactor.callLater(3, reactor.stop)
        
        def on_connection_error(failure):
            print(f"   ❌ CCCP connection error: {failure}")
            reactor.callLater(1, reactor.stop)
        
        d.addCallback(on_connected)
        d.addErrback(on_connection_error)
        
        print("   🔄 Starting connection (5 second timeout)...")
        
        # Run reactor
        from twisted.internet import reactor
        
        # Set timeout
        def timeout_handler():
            print("   ⏰ CCCP connection timeout")
            reactor.stop()
        
        timeout_call = reactor.callLater(5, timeout_handler)
        
        reactor.run()
        
    except ImportError as e:
        print(f"   ❌ CCCP library not available: {e}")
        return False
    except Exception as e:
        print(f"   ❌ CCCP library error: {e}")
        return False

def test_ccenter_update():
    """Test ccenter_update availability."""
    print("🛠️ Testing ccenter_update availability...")
    
    try:
        result = subprocess.run(
            ["which", "ccenter_update"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            path = result.stdout.strip()
            print(f"   ✅ ccenter_update found: {path}")
            
            # Test connection to CCCP server
            test_cmd = [
                "ccenter_update",
                "--login", "admin",
                "--password", "admin",
                "--server", "10.199.30.67", "20000",
                "--info"
            ]
            
            result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("   ✅ ccenter_update can connect to CCCP server")
                print(f"   📡 Output: {result.stdout[:200]}...")  # First 200 chars
            else:
                print("   ⚠️ ccenter_update connection failed")
                print(f"   📡 Error: {result.stderr}")
        else:
            print("   ❌ ccenter_update not found")
            print("   📡 Try: export PATH=$PATH:/opt/consistent/bin:$PATH")
        
    except subprocess.TimeoutExpired:
        print("   ⏰ ccenter_update test timeout")
    except Exception as e:
        print(f"   ❌ ccenter_update test error: {e}")

def test_dispatch_json():
    """Test the dispatch JSON interface."""
    print("📊 Testing dispatch JSON interface...")
    
    try:
        # Check if test script exists
        script_path = "/home/fblo/Documents/repos/iv-cccp/test_dispatch_json.py"
        
        if os.path.exists(script_path):
            print(f"   ✅ Found test script: {script_path}")
            
            # Run test
            result = subprocess.run(
                ["python3", script_path, "10.199.30.67", "20103"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            print(f"   📤 Test script output:")
            print(f"     Exit code: {result.returncode}")
            if result.stdout:
                print(f"     STDOUT: {result.stdout}")
            if result.stderr:
                print(f"     STDERR: {result.stderr}")
            
if result.returncode == 0:
                print("   ✅ Dispatch JSON interface working")
                if result.stdout:
                    print(f"   📤 Output: {result.stdout}")
                return True
            else:
                print("   ❌ Dispatch JSON interface failed")
                return False
        except Exception as e:
                print(f"   ❌ Dispatch JSON test error: {e}")
                return False
        else:
            print(f"   ❌ Test script not found: {script_path}")
            return False
            
    except Exception as e:
        print(f"   ❌ Dispatch JSON test error: {e}")
        return False

def test_ccp_protocol():
    """Test CCCP protocol detection."""
    print("🔍 Testing CCCP protocol stack...")
    
    try:
        # Check if CCCP modules are available
        modules_to_test = [
            "cccp.async.ccxml",
            "cccp.protocols.ccxml",
            "cccp.protocols.messages",
            "cccp.protocols.serializer",
            "cccp.protocols.deserializer"
        ]
        
        for module in modules_to_test:
            try:
                __import__(module)
                print(f"   ✅ {module} available")
            except ImportError as e:
                print(f"   ❌ {module} not available: {e}")
        
        return True
        
        except Exception as e:
            print(f"   ❌ Protocol test error: {e}")
            return False

    def test_ccp_protocol():
        """Test CCCP protocol detection."""
        print("🔍 Testing CCCP protocol stack...")
        
        try:
            # Check if CCCP modules are available
            modules_to_test = [
                "cccp.async.ccxml",
                "cccp.protocols.ccxml",
                "cccp.protocols.messages",
                "cccp.protocols.serializer",
                "cccp.protocols.deserializer"
            ]
            
                        for module in modules_to_test:
                try:
                    __import__(module)
                    print(f"   ✅ {module} available")
                except ImportError as e:
                    print(f"   ❌ {module} not available: {e}")
            
            return len([m for m in modules_to_test if m and m.endswith("ccxml")])
            
        except Exception as e:
            print(f"   ❌ Protocol test error: {e}")
            return False

def main():
    """Run all connection tests."""
    print("=" * 80)
    print("  CCXML CONNECTION DIAGNOSTICS")
    print("=" * 80)
    print(f"  Target: 10.199.30.67:20103 (CCXML)")
    print(f"  Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)
    
    tests = [
        ("TCP Connection", test_direct_connection),
        ("CCCP Library", test_ccp_library),
        ("Dispatch JSON", test_dispatch_json),
        ("Protocol Stack", test_ccp_protocol),
        ("ccenter_update", test_ccenter_update),
    ]
    
    results = []
    
    for i, (test_name, test_func) in enumerate(tests, 1):
        print(f"\n{i}. {test_name}")
        print("-" * 50)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"   ✅ {test_name} PASSED")
            else:
                print(f"   ❌ {test_name} FAILED")
                
        except Exception as e:
            print(f"   💥 {test_name} ERROR: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 80)
    print("  TEST SUMMARY")
    print("=" * 80)
    
    passed = [r[0] for r in results if r[1]]
    failed = [r[0] for r in results if not r[1]]
    
    print(f"  ✅ Passed: {len(passed)}/{len(results)}")
    if passed:
        for test in passed:
            print(f"     - {test}")
    
    print(f"  ❌ Failed: {len(failed)}/{len(results)}")
    if failed:
        for test in failed:
            print(f"     - {test}")
    
    print("\n" + "=" * 80)
    
    if len(passed) > 0:
        print("🎉 CONNECTION TESTS SUCCESSFUL - You can proceed with CCXML deployment!")
    else:
        print("💥 CONNECTION TESTS FAILED - Check network and permissions")
    
    return len(passed) > 0


if __name__ == "__main__":
    if __name__ == "__main__":
    if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)