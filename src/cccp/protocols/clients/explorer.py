#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#    - PEMO <pemo@interact-iv.com>

from cccp.protocols.cclib import CDEPSocket
import cccp.protocols.messages.explorer as msg

class explorer:
    def __init__(self, address, port):
        self.socket = CDEPSocket(self, address, port, msg.initialize)
        self.socket.start()
        self.socket.send(msg.initialize,1234,True) # client_version fixe et can_compress
        self.socket.step()

    def step(self):
        return self.socket.step()

    def step_done(self, step_result = None):
        self.socket.step_done(step_result)

    def get_step_result(self):
        return self.socket.step_result()

    step_result = property(get_step_result)

    def login(self, session_id, login, password, instances_count, has_been_connected):
        self.socket.send(msg.login, session_id, login, password, instances_count, has_been_connected)

    def logout(self, session_id):
        self.socket.send(msg.logout, session_id)

    def client_void(self):
        self.socket.send(msg.client_void)

    def use_default_namespaces_index(self):
        self.socket.send(msg.use_default_namespaces_index)

    def update_class(self, session_id, system_id, class_path, class_name, object_class):
        self.socket.send(msg.update_class, session_id, system_id, class_path, class_name, object_class)

    def update_naming_space(self, session_id, path):
        self.socket.send(msg.update_naming_space, session_id, path)

    def _create_node(self, session_id, system_id, node_name):
        self.socket.send(msg.create_node, session_id, system_id, node_name)

    def _delete_node(self, session_id, system_id, node_name):
        self.socket.send(msg.delete_node, session_id, system_id, node_name)

    def _move_node(self, session_id, system_id, node_name, new_node_name):
        self.socket.send(msg.move_node, session_id, system_id, node_name, new_node_name)

    def update_node_attributes(self, session_id, system_id, node_name, data):
        self.socket.send(msg.update_node_attributes, session_id, system_id, node_name, data)

    def update_node_object(self, session_id, system_id, node_name, objects):
        self.socket.send(msg.update_node_object, session_id, system_id, node_name, "",objects)

    def update_node_binary(self, session_id, system_id, node_name, mime, consistent_object_class, data):
        self.socket.send(msg.update_node_binary, session_id, system_id, node_name, mime, consistent_object_class, data)

    def start_update_node_binary(self, session_id, system_id, node_name, mime, consistent_object_class, truncate):
        self.socket.send(msg.start_update_node_binary, session_id, system_id, node_name, mime, consistent_object_class, truncate)

    def add_update_node_binary(self, session_id, system_id, offset, insert, data):
        self.socket.send(msg.add_update_node_binary, session_id, system_id, offset, insert, data)

    def end_update_node_binary(self, session_id, system_id):
        self.socket.send(msg.end_update_node_binary, session_id, system_id)

    def needs_naming_space(self, class_path):
        self.socket.send(msg.needs_naming_space, class_path)

    def query_node_header(self, session_id, system_id, path):
        self.socket.send(msg.query_node_header, session_id, system_id, path)

    def query_node_object_content(self, session_id, system_id, path, may_modify, raw_object, create_class_name):
        self.socket.send(msg.query_node_object_content, session_id, system_id, path, may_modify, raw_object, create_class_name)

    def query_node_object_content_remove_field(self, session_id, system_id, selection, field_name, request_id):
        self.socket.send(msg.query_node_object_content_remove_field, session_id, system_id, selection, field_name, request_id)

    def query_node_object_content_update_field_uint_32(self, session_id, system_id, selection, field_name, operation, value, request_id):
        self.socket.send(msg.query_node_object_content_update_field_uint_32, session_id, system_id, selection, field_name, operation, value, request_id)

    def query_node_object_content_update_field_int_32(self, session_id, system_id, selection, field_name, operation, value, request_id):
        self.socket.send(msg.query_node_object_content_update_field_int_32, session_id, system_id, selection, field_name, operation, value, request_id)

    def query_node_object_content_update_field_real(self, session_id, system_id, selection, field_name, operation, value, request_id):
        self.socket.send(msg.query_node_object_content_update_field_real, session_id, system_id, selection, field_name, operation, value, request_id)

    def query_node_object_content_update_field_number(self, session_id, system_id, selection, field_name, operation, value, request_id):
        self.socket.send(msg.query_node_object_content_update_field_number, session_id, system_id, selection, field_name, operation, value, request_id)

    def query_node_object_content_update_field_string(self, session_id, system_id, selection, field_name, operation, value, request_id):
        self.socket.send(msg.query_node_object_content_update_field_string, session_id, system_id, selection, field_name, operation, value, request_id)

    def query_node_object_content_update_field_boolean(self, session_id, system_id, selection, field_name, value, request_id):
        self.socket.send(msg.query_node_object_content_update_field_boolean, session_id, system_id, selection, field_name, value, request_id)

    def query_node_object_content_update_field_date(self, session_id, system_id, selection, field_name, value, request_id):
        self.socket.send(msg.query_node_object_content_update_field_date, session_id, system_id, selection, field_name, value, request_id)

    def query_node_object_content_update_field_uint_64(self, session_id, system_id, selection, field_name, operation, value, request_id):
        self.socket.send(msg.query_node_object_content_update_field_uint_64, session_id, system_id, selection, field_name, operation, value, request_id)

    def query_node_object_content_update_field_list_insert_before(self, session_id, system_id, selection, field_name, value, before, request_id):
        self.socket.send(msg.query_node_object_content_update_field_list_insert_before, session_id, system_id, selection, field_name, value, before, request_id)

    def query_node_object_content_update_field_list_insert_after(self, session_id, system_id, selection, field_name, value, after, request_id):
        self.socket.send(msg.query_node_object_content_update_field_list_insert_after, session_id, system_id, selection, field_name, value, after, request_id)

    def query_node_object_content_update_field_list_remove(self, session_id, system_id, selection, field_name, value, request_id):
        self.socket.send(msg.query_node_object_content_update_field_list_remove, session_id, system_id, selection, field_name, value, request_id)

    def query_node_object_content_update_field_internal_reference(self, session_id, system_id, selection, field_name, value, request_id):
        self.socket.send(msg.query_node_object_content_update_field_internal_reference, session_id, system_id, selection, field_name, value, request_id)

    def query_node_object_content_update_field_external_reference(self, session_id, system_id, selection, field_name, value, index_value, request_id):
        self.socket.send(msg.query_node_object_content_update_field_external_reference, session_id, system_id, selection, field_name, value, index_value, request_id)

    def query_node_object_content_update_field_direct_reference(self, session_id, system_id, selection, field_name, value, request_id):
        self.socket.send(msg.query_node_object_content_update_field_direct_reference, session_id, system_id, selection, field_name, value, request_id)

    def query_node_object_content_create_object(self, session_id, system_id, creation_id, name_space, class_name):
        self.socket.send(msg.query_node_object_content_create_object, session_id, system_id, creation_id, name_space, class_name)

    def query_node_object_content_update(self, session_id, system_id, request_id, update):
        self.socket.send(msg.query_node_object_content_update, session_id, system_id, request_id, update)

    def query_node_binary_content(self, session_id, system_id, path, window_size):
        self.socket.send(msg.query_node_binary_content, session_id, system_id, path, window_size)

    def query_node_binary_content_ack(self, session_id, system_id, received_size):
        self.socket.send(msg.query_node_binary_content_ack, session_id, system_id, received_size)

    def query_node_children(self, session_id, system_id, path):
        self.socket.send(msg.query_node_children, session_id, system_id, path)

    def set_object_format(self, session_id, format):
        self.socket.send(msg.set_object_format, session_id, format)

    def query_list(self, session_id, system_id, path, object_id, field, filter, page_size, window_field, window_duration):
        self.socket.send(msg.query_list, session_id, system_id, path, object_id, field, filter, page_size, window_field, window_duration)

    def query_list_add_field(self, session_id, system_id, father_field_index, field_index, field_name, field_query):
        self.socket.send(msg.query_list_add_field, session_id, system_id, father_field_index, field_index, field_name, field_query)

    def query_object(self, session_id, system_id, path, object_id, format_id, list_system_id):
        self.socket.send(msg.query_object, session_id, system_id, path, object_id, format_id, list_system_id)

    def select_and_query_object(self, session_id, system_id, path, object_id, field, filter, format_id, list_system_id):
        self.socket.send(msg.select_and_query_object, session_id, system_id, path, object_id, field, filter, format_id, list_system_id)

    def query_object_add_field(self, session_id, system_id, path, object_id, father_field_index, field_index, field_name, field_query):
        self.socket.send(msg.query_object_add_field, session_id, system_id, path, object_id, father_field_index, field_index, field_name, field_query)

    def stop_query(self, session_id, system_id):
        self.socket.send(msg.stop_query, session_id, system_id)

    def client_event(self, session_id, path, source, target, delay, event_name, object):
        self.socket.send(msg.client_event, session_id, path, source, target, delay, event_name, object)

    def client_log(self, session_id, path, source, data):
        self.socket.send(msg.client_log, session_id, path, source, data)

    def client_log_event(self, session_id, path, source, target, event_name, managed, object):
        self.socket.send(msg.client_log_event, session_id, path, source, target, event_name, managed, object)
