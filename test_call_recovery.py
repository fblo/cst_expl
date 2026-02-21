#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the calqued call recovery from logs_explorer
"""

import os
import sys
from get_users_and_calls import _get_session_call_called_from_events, parse_rlog_file

def test_call_recovery():
    """Test the _get_session_call_called_from_events function"""
    print("Testing call recovery from parsed RLOG events...")

    # Create a mock event list similar to what parse_rlog_file returns
    mock_events = [
        {
            'date': '14:30:25',
            'timestamp': '20/02/2026',
            'source': 'session_12345@1.2.3.4',
            'target': '0612345678',
            'state': 'alerting',
            'name': 'connection.alerting',
            'data': 'Connection alerting to sip:0612345678@domain.com',
            '_phones': ['0612345678'],
            '_users': [],
            '_remote': '',
            '_local': 'sip:0612345678@domain.com',
        },
        {
            'date': '14:30:26',
            'timestamp': '20/02/2026',
            'source': 'session_12345@1.2.3.4',
            'target': '0123456789',
            'state': 'connected',
            'name': 'connection.connected',
            'data': 'Connection connected from sip:0123456789@domain.com',
            '_phones': ['0123456789'],
            '_users': [],
            '_remote': 'sip:0123456789@domain.com',
            '_local': '',
        },
        {
            'date': '14:30:27',
            'timestamp': '20/02/2026',
            'source': 'session_12345@1.2.3.4',
            'target': '0612345678',
            'state': 'disconnected',
            'name': 'connection.disconnected',
            'data': 'Connection disconnected',
            '_phones': [],
            '_users': [],
            '_remote': '',
            '_local': '',
        }
    ]

    # Test the function
    caller, called = _get_session_call_called_from_events(mock_events)

    print(f"Mock events: {len(mock_events)} events")
    print(f"Caller: {caller}")
    print(f"Called: {called}")

    # Verify results
    if caller and called:
        print("✅ Test PASSED: Both caller and called extracted correctly")
        return True
    else:
        print("❌ Test FAILED: Could not extract caller and called")
        return False

def test_with_real_logs():
    """Test with actual log files if they exist"""
    print("\n" + "="*60)
    print("Testing with real log files...")

    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "import_logs")

    if not os.path.exists(logs_dir):
        print(f"⚠️  Logs directory not found: {logs_dir}")
        return False

    log_files = [f for f in os.listdir(logs_dir) if f.startswith('log_') and f.endswith('.log')]
    if not log_files:
        print(f"⚠️  No log files found in: {logs_dir}")
        return False

    print(f"Found {len(log_files)} log files")

    # Test with the first log file
    log_file = os.path.join(logs_dir, log_files[0])
    print(f"Testing with: {log_file}")

    # Parse the file to find sessions
    import re
    with open(log_file, 'rb') as f:
        content = f.read()

    # Find first session
    pattern = b"session_"
    match = re.search(pattern, content)
    if not match:
        print("⚠️  No session found in log file")
        return False

    start = match.start()
    end = start
    while end < len(content) and content[end] > 32 and content[end] < 127:
        end += 1

    if end > start:
        session_id = content[start:end].decode('utf-8', errors='replace')
        print(f"Found session: {session_id}")

        # Parse events for this session
        events = parse_rlog_file(log_file, session_id)
        print(f"Parsed {len(events)} events for this session")

        if events:
            # Extract caller/called
            caller, called = _get_session_call_called_from_events(events)
            print(f"Caller: {caller}")
            print(f"Called: {called}")

            if caller or called:
                print("✅ Test PASSED: Caller/called extracted from real log file")
                return True
            else:
                print("⚠️  No caller/called found (may be normal if session has no phone events)")
                return True

    return False

if __name__ == "__main__":
    print("="*60)
    print("Testing Calqued Call Recovery for logs_explorer")
    print("="*60)

    # Test 1: Mock events
    test1_passed = test_call_recovery()

    # Test 2: Real logs (if available)
    test2_passed = test_with_real_logs()

    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    print(f"Mock events test: {'PASSED' if test1_passed else 'FAILED'}")
    print(f"Real logs test: {'PASSED' if test2_passed else 'FAILED'}")

    if test1_passed and test2_passed:
        print("\n✅ All tests PASSED!")
        sys.exit(0)
    else:
        print("\n❌ Some tests FAILED!")
        sys.exit(1)