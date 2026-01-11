#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#    - PEMO <pemo@interact-iv.com>

from cccp.protocols.ccthread import CDEPSocket
import cccp.protocols.messages.explorer as msg

EXPLORER_SESSION_ID=1
EXPLORER_FORMAT_ID=1
EXPLORER_LIST_ID=1

class dispatch_explorer:
    def __init__(self, address, port, login = "admin", password = "admin"):
        self.socket = CDEPSocket(self, address, port, msg.initialize)
        self.socket.start()
        self.socket.send(msg.initialize, 1234, True) # client_version fixe et can_compress
        self.step()
        self.login(EXPLORER_SESSION_ID, login, password, 0, False)
        self.step()

    def set_object_format(self, session_id, format):
        self.socket.send(msg.set_object_format, session_id, format)

    def step(self):
        self.socket.step_result = None
        return self.socket.step()

    def step_done(self, step_result=None):
        self.socket.step_done(step_result)

    @property
    def step_result(self):
        return self.socket.step_result

    def stop(self):
        self.socket.stop()
        self.socket.join()

    def on_connection_ok(self, server_version, date):
        self.step_done()

    def login(self, session_id, login, password, instances_count, has_been_connected):
        self.socket.send(msg.login, session_id, login, password, instances_count, has_been_connected)

    def on_login_ok(self,session_id, user_id, explorer_id):
        self.step_done()

    def on_login_failed(self,session_id, reason):
        self.step_done()

    def logout(self, session_id):
        self.socket.send(msg.logout, session_id)

    def query_list(self, session_id, system_id, path, object_id, field, filter, page_size, window_field, window_duration):
        self.socket.send(msg.query_list, session_id, system_id, path, object_id, field, filter, page_size, window_field, window_duration)

    def query_object(self, session_id, system_id, path, object_id, format_id, list_system_id):
        self.socket.send(msg.query_object, session_id, system_id, path, object_id, format_id, list_system_id)


