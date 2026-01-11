#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#    - PEMO <pemo@interact-iv.com>

from cccp.protocols.ccc_types import (
    t_any_object,
    t_boolean,
    t_data,
    t_date,
    t_int_32,
    t_object,
    t_real,
    t_string,
    t_uint_32,
    t_uint_64
)

all_methods_by_id = {
    103: {
        0: ('server_ask_to_disconnect', []),
        103: ("initialize", [t_uint_32, t_boolean]),
        10019: ("add_update_node_binary", [t_uint_32, t_uint_32, t_uint_64, t_boolean, t_data]), # NOQA
        10014: ("client_event", [t_uint_32, t_string, t_string, t_string, t_real, t_string, (t_object, "consistent_protocol_named_object")]), # NOQA
        10015: ("client_log", [t_uint_32, t_string, t_string, t_string]),
        10016: ("client_log_event", [t_uint_32, t_string, t_string, t_string, t_string, t_boolean, t_object]), # NOQA
        10048: ("client_void", []),
        10003: ("_create_node", [t_uint_32, t_uint_32, t_string]),
        10021: ("_delete_node", [t_uint_32, t_uint_32, t_string]),
        10020: ("end_update_node_binary", [t_uint_32, t_uint_32]),
        10000: ("login", [t_uint_32, t_string, t_string, t_uint_32, t_boolean]), # NOQA
        10030: ("logout", [t_uint_32]),
        10045: ("_move_node", [t_uint_32, t_uint_32, t_string, t_string]),
        10017: ("needs_naming_space", [t_string]),
        10011: ("query_list", [t_uint_32, t_uint_32, t_string, t_uint_32, t_string, t_string, t_uint_32, t_string, t_uint_32]), # NOQA
        10043: ("query_list_add_field", [t_uint_32, t_uint_32, t_uint_32, t_uint_32, t_string, t_string]), # NOQA
        10028: ("query_node_binary_content", [t_uint_32, t_uint_32, t_string, t_uint_32]), # NOQA
        10029: ("query_node_binary_content_ack", [t_uint_32, t_uint_32, t_uint_32]), # NOQA
        10009: ("query_node_children", [t_uint_32, t_uint_32, t_string]),
        10007: ("query_node_header", [t_uint_32, t_uint_32, t_string]),
        10008: ("query_node_object_content", [t_uint_32, t_uint_32, t_string, t_boolean, t_boolean, t_string]), # NOQA
        10041: ("query_node_object_content_create_object", [t_uint_32, t_uint_32, t_uint_32, t_string, t_string]), # NOQA
        10022: ("query_node_object_content_remove_field", [t_uint_32, t_uint_32, t_string, t_string, t_uint_32]), # NOQA
        10047: ("query_node_object_content_update", [t_uint_32, t_uint_32, t_uint_32, (t_object, "consistent_update")]), # NOQA
        10025: ("query_node_object_content_update_field_boolean", [t_uint_32, t_uint_32, t_string, t_string, t_boolean, t_uint_32]), # NOQA
        10026: ("query_node_object_content_update_field_date", [t_uint_32, t_uint_32, t_string, t_string, t_date, t_uint_32]), # NOQA
        10040: ("query_node_object_content_update_field_direct_reference", [t_uint_32, t_uint_32, t_string, t_string, t_uint_32, t_uint_32]), # NOQA
        10039: ("query_node_object_content_update_field_external_reference", [t_uint_32, t_uint_32, t_string, t_string, t_string, t_uint_32, t_uint_32]), # NOQA
        10032: ("query_node_object_content_update_field_int_32", [t_uint_32, t_uint_32, t_string, t_string, t_uint_32, t_int_32, t_uint_32]), # NOQA
        10038: ("query_node_object_content_update_field_internal_reference", [t_uint_32, t_uint_32, t_string, t_string, t_uint_32, t_uint_32]), # NOQA
        10036: ("query_node_object_content_update_field_list_insert_after", [t_uint_32, t_uint_32, t_string, t_string, t_uint_32, t_uint_32, t_uint_32]), # NOQA
        10035: ("query_node_object_content_update_field_list_insert_before", [t_uint_32, t_uint_32, t_string, t_string, t_uint_32, t_uint_32, t_uint_32]), # NOQA
        10037: ("query_node_object_content_update_field_list_remove", [t_uint_32, t_uint_32, t_string, t_string, t_uint_32, t_uint_32]), # NOQA
        10033: ("query_node_object_content_update_field_number", [t_uint_32, t_uint_32, t_string, t_string, t_uint_32, t_real, t_uint_32]), # NOQA
        10023: ("query_node_object_content_update_field_real", [t_uint_32, t_uint_32, t_string, t_string, t_uint_32, t_real, t_uint_32]), # NOQA
        10024: ("query_node_object_content_update_field_string", [t_uint_32, t_uint_32, t_string, t_string, t_uint_32, t_string, t_uint_32]), # NOQA
        10031: ("query_node_object_content_update_field_uint_32", [t_uint_32, t_uint_32, t_string, t_string, t_uint_32, t_uint_32, t_uint_32]), # NOQA
        10034: ("query_node_object_content_update_field_uint_64", [t_uint_32, t_uint_32, t_string, t_string, t_uint_32, t_uint_64, t_uint_32]), # NOQA
        10012: ("query_object", [t_uint_32, t_uint_32, t_string, t_uint_32, t_uint_32, t_uint_32]), # NOQA
        10042: ("query_object_add_field", [t_uint_32, t_uint_32, t_string, t_uint_32, t_uint_32, t_uint_32, t_string, t_string]), # NOQA
        10044: ("select_and_query_object", [t_uint_32, t_uint_32, t_string, t_uint_32, t_string, t_string, t_uint_32, t_uint_32]), # NOQA
        10010: ("set_object_format", [t_uint_32, t_object]),
        10018: ("start_update_node_binary", [t_uint_32, t_uint_32, t_string, t_string, t_string, t_boolean]), # NOQA
        10013: ("stop_query", [t_uint_32, t_uint_32]),
        10001: ("update_class", [t_uint_32, t_uint_32, t_string, t_string, (t_object, "consistent_class")]), # NOQA
        10002: ("update_naming_space", [t_uint_32, t_string]),
        10046: ("update_node_attributes", [t_uint_32, t_uint_32, t_string, t_data]), # NOQA
        10006: ("update_node_binary", [t_uint_32, t_uint_32, t_string, t_string, t_string, t_data]), # NOQA
        10005: ("update_node_object", [t_uint_32, t_uint_32, t_string, t_string, t_any_object]), # NOQA
        10049: ("use_default_namespaces_index", []),

        20010: ("class_updated", [t_string, t_string, (t_object, "consistent_protocol_named_object")]), # NOQA
        20000: ("connection_ok", [t_uint_32, t_date]),
        20034: ("list_object_response", [t_uint_32, t_uint_32, (t_object, "consistent_protocol_object")]), # NOQA
        20007: ("list_response", [t_uint_32, t_uint_32, (t_object, "consistent_protocol_list")]), # NOQA
        20002: ("login_failed", [t_uint_32, t_string]),
        20001: ("login_ok", [t_uint_32, t_string, t_string]),
        20021: ("logout_ok", [t_uint_32]),
        20011: ("naming_space_updated", [t_string]),
        20019: ("node_binary_content_response", [t_uint_32, t_uint_32, t_uint_64, t_boolean, t_data, t_boolean, t_uint_32]), # NOQA
        20020: ("node_binary_content_response_update", [t_uint_32, t_uint_32, t_boolean]), # NOQA
        20033: ("node_binary_content_size", [t_uint_32, t_uint_32, t_uint_64, t_uint_32]), # NOQA
        20006: ("node_children_response", [t_uint_32, t_uint_32, t_object, t_uint_32]), # NOQA
        20004: ("node_header_response", [t_uint_32, t_uint_32, (t_object, "consistent_protocol_header"), t_uint_32]), # NOQA
        20005: ("node_object_content_response", [t_uint_32, t_uint_32, t_object, t_uint_32]), # NOQA
        20032: ("node_object_content_response_create_object", [t_uint_32, t_uint_32, t_uint_32, t_uint_32, t_string, t_string]), # NOQA
        20013: ("node_object_content_response_remove_field", [t_uint_32, t_uint_32, t_string, t_string, t_uint_32]), # NOQA
        20016: ("node_object_content_response_update_field_boolean", [t_uint_32, t_uint_32, t_string, t_string, t_boolean, t_uint_32]), # NOQA
        20017: ("node_object_content_response_update_field_date", [t_uint_32, t_uint_32, t_string, t_string, t_date, t_uint_32]), # NOQA
        20031: ("node_object_content_response_update_field_direct_reference", [t_uint_32, t_uint_32, t_string, t_string, t_uint_32, t_uint_32]), # NOQA
        20030: ("node_object_content_response_update_field_external_reference", [t_uint_32, t_uint_32, t_string, t_string, t_string, t_uint_32, t_uint_32]), # NOQA
        20024: ("node_object_content_response_update_field_int_32", [t_uint_32, t_uint_32, t_string, t_string, t_int_32, t_uint_32]), # NOQA
        20029: ("node_object_content_response_update_field_internal_reference", [t_uint_32, t_uint_32, t_string, t_string, t_uint_32, t_uint_32]), # NOQA
        20027: ("node_object_content_response_update_field_list_insert_after", [t_uint_32, t_uint_32, t_string, t_string, t_uint_32, t_uint_32, t_uint_32]), # NOQA
        20026: ("node_object_content_response_update_field_list_insert_before", [t_uint_32, t_uint_32, t_string, t_string, t_uint_32, t_uint_32, t_uint_32]), # NOQA
        20028: ("node_object_content_response_update_field_list_remove", [t_uint_32, t_uint_32, t_string, t_string, t_uint_32, t_uint_32]), # NOQA
        20014: ("node_object_content_response_update_field_real", [t_uint_32, t_uint_32, t_string, t_string, t_real, t_uint_32]), # NOQA
        20015: ("node_object_content_response_update_field_string", [t_uint_32, t_uint_32, t_string, t_string, t_string, t_uint_32]), # NOQA
        20022: ("node_object_content_response_update_field_uint_32", [t_uint_32, t_uint_32, t_string, t_string, t_uint_32, t_uint_32]), # NOQA
        20025: ("node_object_content_response_update_field_uint_64", [t_uint_32, t_uint_32, t_string, t_string, t_uint_64, t_uint_32]), # NOQA
        20035: ("node_object_content_update_result", [t_uint_32, t_uint_32, t_uint_32, t_uint_32]), # NOQA
        20023: ("node_raw_object_content_response", [t_uint_32, t_uint_32, t_object, t_uint_32, t_uint_32]), # NOQA
        20008: ("object_response", [t_uint_32, t_uint_32, t_object, t_uint_32]), # NOQA
        20037: ("restart_connection", []),
        20003: ("result", [t_uint_32, t_uint_32, t_uint_32]),
        20009: ("server_event", [t_uint_32, t_string, t_string, t_real, t_string, t_object]), # NOQA
        20036: ("server_void", []),
        20012: ("start_result", [t_uint_32, t_uint_32, t_uint_32]),
        20038: ("use_default_namespaces_index_ok", [])
    },
    100: {
        100: ("initialize", [t_uint_32]),
        10020: ("add_single_login", [t_string, t_string, t_string]),
        10021: ("check_single_login", [t_uint_32, t_string, t_string, t_string]), # NOQA
        10017: ("connections_stat", [t_string, t_date, t_uint_32, t_uint_32, t_uint_32]), # NOQA
        10024: ("managed_module_debug_level", [t_uint_32, t_uint_32]),
        10011: ("managed_module_id_managed", [t_uint_32, t_string]),
        10012: ("managed_module_id_unmanaged", [t_uint_32, t_string]),
        10016: ("managed_module_info", [t_uint_32, t_string]),
        10014: ("managed_module_needs_port", [t_uint_32, t_boolean, t_uint_32, t_string, t_uint_32]), # NOQA
        10008: ("managed_module_ready", [t_uint_32, t_uint_32]),
        10025: ("set_process_debug_level", [t_string, t_uint_32]),
        10007: ("managed_module_started", [t_uint_32, t_string, t_uint_32, t_string, t_string, t_string, t_string, t_string, t_string, t_string, t_string, t_uint_32, t_string]), # NOQA
        10006: ("managed_module_state", [t_uint_32, t_uint_32]),
        10018: ("needs_port_range", [t_uint_32, t_uint_32, t_uint_32]),
        10023: ("process_debug_level", [t_uint_32]),
        10009: ("process_id_managed", [t_string]),
        10010: ("process_id_unmanaged", [t_string]),
        10015: ("process_info", [t_string]),
        10000: ("process_initialize", [t_uint_32, t_string, t_string, t_string, t_string, t_string, t_string, t_string, t_string]), # NOQA
        10003: ("process_needs_children", [t_string]),
        10005: ("process_needs_naming_space", [t_string]),
        10004: ("process_needs_node", [t_string]),
        10013: ("process_needs_port", [t_boolean, t_uint_32, t_string, t_uint_32]), # NOQA
        10001: ("process_ready", [t_uint_32]),
        10002: ("process_state", [t_uint_32]),
        10019: ("release_port_range", [t_uint_32]),
        10022: ("update_stat", [t_string, t_string, t_int_32, t_uint_32]),

        20014: ("can_use_port", [t_uint_32, t_uint_32, t_uint_32, t_uint_32]),
        20017: ("set_debug_level", [t_uint_32]),
        20006: ("class_updated", [t_string, t_string, t_object]),
        20000: ("connection_ok", [t_uint_32, t_string, t_string, t_string, t_uint_32]), # NOQA
        20019: ("downto_head_set_process_debug_level", [t_string, t_uint_32]),
        20018: ("process_debug_level_set", [t_string]),
        20012: ("module_id_managed", [t_uint_32, t_string]),
        20013: ("module_id_unmanaged", [t_uint_32, t_string]),
        20009: ("module_ready", [t_uint_32, t_uint_32]),
        20008: ("module_started", [t_uint_32, t_string, t_uint_32, t_string, t_string, t_string, t_string, t_string, t_string, t_string, t_string, t_uint_32, t_string]), # NOQA
        20010: ("module_state", [t_uint_32, t_uint_32]),
        20007: ("naming_space_updated", [t_string]),
        20005: ("node_binary_updated", [t_string, t_string, t_string, t_data]),
        20001: ("node_created", [t_string]),
        20002: ("node_deleted", [t_string]),
        20003: ("node_empty", [t_string]),
        20004: ("node_object_updated", [t_string, t_string, t_string, t_data]),
        20015: ("port_range_result", [t_uint_32, t_uint_32]),
        20011: ("set_server_address", [t_string]),
        20016: ("single_login_result", [t_uint_32, t_boolean])
    },
    0x40000002: {
        0: ('server_ask_to_disconnect', []),
        0x40000002: ("initialize", [t_uint_32]),
        10000: ("add_session", [t_uint_32, t_string, t_string, t_uint_32, t_boolean, t_uint_32, t_string]), # NOQA
        10001: ("logout", [t_uint_32]),
        10002: ("client_event", [t_uint_32, t_string, t_string, t_real, t_string, (t_object, "consistent_protocol_named_object")]), # NOQA
        10003: ("register_sip", [t_string, t_string, (t_object, "consistent_protocol_contacts_list")]), # NOQA
        10005: ("client_log", [t_uint_32, t_string, t_string]),
        10006: ("client_log_event", [t_uint_32, t_string, t_string, t_string, t_boolean, (t_object, "consistent_protocol_named_object")]), # NOQA
        10007: ("disconnected", [t_uint_32]),
        10008: ("get_rights", [t_uint_32, t_string]),
        10009: ("no_receive", [t_uint_32, t_real]),
        10010: ("no_write", [t_uint_32, t_real]),
        10011: ("set_can_disconnect", [t_uint_32, t_boolean]),
        10012: ("add_reply_value_string", [t_uint_32, t_string, t_uint_32, t_uint_32, t_string]), # NOQA
        10013: ("add_reply_value_number", [t_uint_32, t_string, t_uint_32, t_uint_32, t_real]), # NOQA
        10014: ("needs_context", [t_uint_32, t_string, t_uint_32, t_uint_32]),
        10015: ("control_ok", [t_uint_32]),
        10016: ("control_nok", [t_uint_32]),
        10017: ("send_engine_state", [t_uint_32, t_boolean, (t_object, "consistent_engine_context")]), # NOQA
        10018: ("add_reply_value_undefined", [t_uint_32, t_string, t_uint_32, t_uint_32]), # NOQA
        10019: ("remove_reply_value", [t_uint_32, t_string]),
        10020: ("init_reply_values", [t_uint_32, (t_object, "consistent_engine_context")]), # NOQA
        10021: ("add_request", [t_uint_32, t_string]),
        10022: ("add_request_column", [t_uint_32, t_string, t_string, t_string, t_int_32, t_int_32]), # NOQA
        10023: ("add_request_value", [t_uint_32, t_string, t_string, t_string]), # NOQA
        10024: ("add_request_source", [t_uint_32, t_string, t_string, t_uint_32, t_string, t_string]), # NOQA
        10025: ("add_array", [t_uint_32, t_string, t_uint_32, t_string, t_string, t_string]), # NOQA
        10026: ("add_array_column", [t_uint_32, t_string, t_string, t_string, t_string, t_string]), # NOQA
        10027: ("add_array_row", [t_uint_32, t_string, t_string, t_string]),
        10028: ("add_array_source", [t_uint_32, t_string, t_string]),
        10029: ("add_graphic", [t_uint_32, t_string, t_uint_32, t_string, t_string, t_uint_32, t_uint_32]), # NOQA
        10030: ("add_graphic_row", [t_uint_32, t_string, t_string, t_string, t_string]), # NOQA

        20000: ("connection_ok", [t_uint_32]),
        20001: ("reject", [t_uint_32, t_string]),
        20002: ("login_ok", [t_uint_32, t_string, t_string, t_string, t_uint_32, t_uint_32]), # NOQA
        20003: ("server_event", [t_uint_32, t_string, t_string, t_real, t_string, (t_object, "consistent_protocol_named_object")]), # NOQA
        20004: ("register_sip_result", [t_string, t_boolean]),
        20005: ("logout_ok", [t_uint_32]),
        20006: ("rights", [t_uint_32, t_uint_32, t_string]),
        20007: ("server_void", [t_uint_32]),
        20008: ("restart_connection", [t_uint_32]),
        20009: ("needs_control", [t_uint_32, t_boolean]),
        20010: ("reply_values", [t_uint_32, (t_object, "consistent_engine_context"), t_string, t_string, t_string]), # NOQA
        20011: ("context_busy", [t_uint_32]),
        20012: ("test_register", [t_string, t_string])
    }
}
