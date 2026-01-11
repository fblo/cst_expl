#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#    - PEMO <pemo@interact-iv.com>

from cccp.protocols.cclib import CDEPSocket
import cccp.protocols.messages.head as msg

class head:
    def __init__(self, address, port):
        self.socket = CDEPSocket(self, address, port, msg.initialize)
        self.socket.connect()
        self.socket.send(msg.initialize) # client_version fixe
        self.socket.step()

    def step(self):
            return self.socket.step()

    def step_done(self,step_result=None):
            self.socket.step_done(step_result)

    def get_step_result(self):
            return self.socket.step_result()

    step_result = property(get_step_result)

    def process_initialize(self, process_pid, process_class, project_name, process_name, explorer_login, explorer_password, path, process_id, process_edition):
        self.socket.send(msg.process_initialize, process_pid, process_class, project_name, process_name, explorer_login, explorer_password, path, process_id, process_edition)

    def process_ready(self, listen_port):
        self.socket.send(msg.process_ready, listen_port)

    def process_state(self, state):
        self.socket.send(msg.process_state, state)

    def process_info(self, info):
        self.socket.send(msg.process_info, info)

    def process_id_managed(self, id):
        self.socket.send(msg.process_id_managed, id)

    def process_id_unmanaged(self, id):
        self.socket.send(msg.process_id_unmanaged, id)

    def process_needs_children(self, node_path):
        self.socket.send(msg.process_needs_children,node_path)

    def process_needs_node(self, node_path):
        self.socket.send(msg.process_needs_node,node_path)

    def process_needs_naming_space(self, class_path):
        self.socket.send(msg.process_needs_naming_space,class_path)

    def process_needs_port(self, last_was_busy, system_id, name, range):
        self.socket.send(msg.process_needs_port, last_was_busy, system_id, name, range)

    def managed_module_started(self, id, address, pid, process_class, project_name, location_path, instance_name, explorer_login, explorer_password, path, process_id, version, edition):
        self.socket.send(msg.managed_module_started, id, address, pid, process_class, project_name, location_path, instance_name, explorer_login, explorer_password, path, process_id, version, edition)

    def managed_module_ready(self, id, listen_port):
        self.socket.send(msg.managed_module_ready,id, listen_port)

    def managed_module_state(self, id, state):
        self.socket.send(msg.managed_module_state,id, state)

    def managed_module_info(self, id, info):
        self.socket.send(msg.managed_module_info, id, info)

    def managed_module_id_managed(self, id, id_managed):
        self.socket.send(msg.managed_module_id_managed, id, id_managed)

    def managed_module_id_unmanaged(self, id, id_unmanaged):
        self.socket.send(msg.managed_module_id_unmanaged, id, id_unmanaged)

    def managed_module_needs_port(self, id, last_was_busy, system_id, name, range):
        self.socket.send(msg.managed_module_needs_port, id, last_was_busy, system_id, name, range)

    def set_process_debug_level(self, process_id, debug_level):
        self.socket.send(msg.set_process_debug_level, process_id, debug_level)

    def connections_stat(self, project, date, incomings, agents, outgoings):
        self.socket.send(msg.connections_stat, project, date, incomings, agents, outgoings)

    def update_stat(self, project, name, delta, increment):
        self.socket.send(msg.update_stat, project, name, delta, increment)

    def needs_port_range(self, id, first_port, last_port):
        self.socket.send(msg.needs_port_range, id, first_port, last_port)

    def release_port_range(self, id):
        self.socket.send(msg.release_port_range, id)

    def add_single_login(self, project, user, login):
        self.socket.send(msg.add_single_login, project, user, login)

    def check_single_login(self, id, project, user, login):
        self.socket.send(msg.check_single_login, id, project, user, login)
