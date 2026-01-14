#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Add paths we know work
sys.path.insert(0, '/home/fblo/Documents/repos/explo-cst/src')
sys.path.insert(0, '/home/fblo/Documents/repos/explo-cst/../iv-cccp/src')
sys.path.insert(0, '/home/fblo/Documents/repos/explo-cst/../iv-cccp/iv-commons/src')

def get_real_dispatch_users():
    """Get REAL users from dispatch that we saw working"""
    try:
        from cccp.async.dispatch import DispatchClient
        from cccp.async_module.helper import get_connection_params
        
        params = get_connection_params()
        
        def user_callback(data):
            if hasattr(data, 'user') and hasattr(data.user, 'login'):
                users.append({
                    'login': data.user.login,
                    'name': getattr(data.user, 'display_name', data.user.login),
                    'state': getattr(data, 'state', 'unknown'),
                    'type': 'supervisor' if 'supervisor' in data.user.login.lower() else 'agent',
                    'phone': getattr(data.user, 'phone_number', 'N/A'),
                    'session_id': getattr(data, 'session_id', None)
                })
        
        # Create client and connect
        client = DispatchClient(*params)
        client.connect()
        
        users = []
        client.on_user_updated = user_callback
        
        # Get current users
        client.get_all_users()
        
        return users
        
    except Exception as e:
        print(f'Dispatch error: {e}')
        return []

if __name__ == '__main__':
    users = get_real_dispatch_users()
    print(f'Found {len(users)} users')
    for user in users:
        print(f'  {user[\"login\"]} - {user[\"state\"]}')
    print(json.dumps(users, indent=2))