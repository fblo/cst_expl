#if !defined(_Windows) && !defined(MacOS)
//ident "@(#)ccenter/report/explorer_client.C (c) Copyright Consistent Software 2002-2005"
#endif

#include "define.h"
#include "idl.h"

// }{ -------------------------------------------------------------------------

T_explorer_client::T_explorer_client(T_report_system * new_system, const char * new_server_address, wow_uint_16 new_server_port)
	: T_consistent_client(new_system, new_server_address, new_server_port) {
	connected_once = FALSE;
	waiting_objects = 0;
}

T_explorer_client::~T_explorer_client() {
}

void T_explorer_client::load_naming_space(const char * path) {
//wow_trace("load classes <%s>\n", path);
	explorer_needs_naming_space(path);
}

void T_explorer_client::connected(void) {
	if (wow_debug_level >= 2) wow_log("connected\n");

	explorer_initialize(product_version, FALSE);
	connected_once = TRUE;
}

void T_explorer_client::server_ask_to_disconnect(void) {
	if (wow_debug_level >= 2) wow_log("asked to disconnect\n");

	if (get_connection() != NULL) get_connection()->set_to_be_deleted(TO_BE_DELETED_ARGUMENTS);
}

void T_explorer_client::explorer_connection_ok(wow_uint_32 /*server_version*/, const T_wow_date * /*date*/) {
	explorer_login(1, get_system()->get_login(), get_system()->get_password(), 1, FALSE);
}

void T_explorer_client::explorer_login_ok(wow_uint_32 /*session_id*/, const char * /*user_id*/, const char * /*explorer_id*/) {
	if (get_system()->is_query_list()) {
		explorer_query_list(1, 1, get_system()->get_path(), get_system()->get_object_id(), get_system()->get_field_name(), get_system()->get_filter(), 0, NULL, 0);
	}
	else if (get_system()->is_query_count()) {
		get_system()->set_system_ended();
		get_connection()->set_to_be_deleted(TO_BE_DELETED_ARGUMENTS);
	}
	else if (get_system()->is_query_object()) {
		explorer_set_object_format(1, get_system()->get_object_format());
		explorer_query_object(1, 1, get_system()->get_path(), get_system()->get_object_id(), 1, 0);
		waiting_objects = 1;
	}
}

void T_explorer_client::explorer_login_failed(wow_uint_32 /*session_id*/, const char * reason) {
	wow_log("bad login : %s\n", reason);
	get_system()->set_system_ended();
	get_connection()->set_to_be_deleted(TO_BE_DELETED_ARGUMENTS);
}

void T_explorer_client::explorer_logout_ok(wow_uint_32 /*session_id*/) {
}

void T_explorer_client::explorer_use_default_namespaces_index_ok(void) {
}

void T_explorer_client::explorer_restart_connection(void) {
}

void T_explorer_client::explorer_server_void(void) {
}

void T_explorer_client::explorer_result(wow_uint_32 /*session_id*/, wow_uint_32 /*system_id*/, wow_uint_32 /*result*/) {
}

void T_explorer_client::explorer_start_result(wow_uint_32 /*session_id*/, wow_uint_32 /*system_id*/, wow_uint_32 /*result*/) {
}

void T_explorer_client::explorer_class_updated(const char * /*class_path*/, const char * /*class_name*/, const T_consistent_class * /*object_class*/) {
}

void T_explorer_client::explorer_naming_space_updated(const char * /*path*/) {
}

void T_explorer_client::explorer_node_header_response(wow_uint_32 /*session_id*/, wow_uint_32 /*system_id*/, const T_consistent_protocol_header * /*header*/, wow_uint_32 /*result*/) {
}

void T_explorer_client::explorer_node_object_content_response(wow_uint_32 /*session_id*/, wow_uint_32 /*system_id*/, const T_wow_xml_object * /*object*/, wow_uint_32 /*result*/) {
}

void T_explorer_client::explorer_node_raw_object_content_response(wow_uint_32 /*session_id*/, wow_uint_32 /*system_id*/, const T_wow_data * /*data*/, wow_uint_32 /*uncompressed_size*/, wow_uint_32 /*result*/) {
}

void T_explorer_client::explorer_node_object_content_response_remove_field(wow_uint_32 /*session_id*/, wow_uint_32 /*system_id*/, const char * /*selection*/, const char * /*field_name*/, wow_uint_32 /*request_id*/) {
}

void T_explorer_client::explorer_node_object_content_response_update_field_uint_32(wow_uint_32 /*session_id*/, wow_uint_32 /*system_id*/, const char * /*selection*/, const char * /*field_name*/, wow_uint_32 /*value*/, wow_uint_32 /*request_id*/) {
}

void T_explorer_client::explorer_node_object_content_response_update_field_int_32(wow_uint_32 /*session_id*/, wow_uint_32 /*system_id*/, const char * /*selection*/, const char * /*field_name*/, wow_int_32 /*value*/, wow_uint_32 /*request_id*/) {
}

void T_explorer_client::explorer_node_object_content_response_update_field_real(wow_uint_32 /*session_id*/, wow_uint_32 /*system_id*/, const char * /*selection*/, const char * /*field_name*/, double /*value*/, wow_uint_32 /*request_id*/) {
}

void T_explorer_client::explorer_node_object_content_response_update_field_string(wow_uint_32 /*session_id*/, wow_uint_32 /*system_id*/, const char * /*selection*/, const char * /*field_name*/, const char * /*value*/, wow_uint_32 /*request_id*/) {
}

void T_explorer_client::explorer_node_object_content_response_update_field_boolean(wow_uint_32 /*session_id*/, wow_uint_32 /*system_id*/, const char * /*selection*/, const char * /*field_name*/, int /*value*/, wow_uint_32 /*request_id*/) {
}

void T_explorer_client::explorer_node_object_content_response_update_field_date(wow_uint_32 /*session_id*/, wow_uint_32 /*system_id*/, const char * /*selection*/, const char * /*field_name*/, const T_wow_date * /*value*/, wow_uint_32 /*request_id*/) {
}

void T_explorer_client::explorer_node_object_content_response_update_field_uint_64(wow_uint_32 /*session_id*/, wow_uint_32 /*system_id*/, const char * /*selection*/, const char * /*field_name*/, wow_uint_64 /*value*/, wow_uint_32 /*request_id*/) {
}

void T_explorer_client::explorer_node_object_content_response_update_field_list_insert_before(wow_uint_32 /*session_id*/, wow_uint_32 /*system_id*/, const char * /*selection*/, const char * /*field_name*/, wow_uint_32 /*value*/, wow_uint_32 /*before*/, wow_uint_32 /*request_id*/) {
}

void T_explorer_client::explorer_node_object_content_response_update_field_list_insert_after(wow_uint_32 /*session_id*/, wow_uint_32 /*system_id*/, const char * /*selection*/, const char * /*field_name*/, wow_uint_32 /*value*/, wow_uint_32 /*after*/, wow_uint_32 /*request_id*/) {
}

void T_explorer_client::explorer_node_object_content_response_update_field_list_remove(wow_uint_32 /*session_id*/, wow_uint_32 /*system_id*/, const char * /*selection*/, const char * /*field_name*/, wow_uint_32 /*value*/, wow_uint_32 /*request_id*/) {
}

void T_explorer_client::explorer_node_object_content_response_update_field_internal_reference(wow_uint_32 /*session_id*/, wow_uint_32 /*system_id*/, const char * /*selection*/, const char * /*field_name*/, wow_uint_32 /*value*/, wow_uint_32 /*request_id*/) {
}

void T_explorer_client::explorer_node_object_content_response_update_field_external_reference(wow_uint_32 /*session_id*/, wow_uint_32 /*system_id*/, const char * /*selection*/, const char * /*field_name*/, const char * /*value*/, wow_uint_32 /*value_index*/, wow_uint_32 /*request_id*/) {
}

void T_explorer_client::explorer_node_object_content_response_update_field_direct_reference(wow_uint_32 /*session_id*/, wow_uint_32 /*system_id*/, const char * /*selection*/, const char * /*field_name*/, wow_uint_32 /*value*/, wow_uint_32 /*request_id*/) {
}

void T_explorer_client::explorer_node_object_content_response_create_object(wow_uint_32 /*session_id*/, wow_uint_32 /*system_id*/, wow_uint_32 /*creation_id*/, wow_uint_32 /*object_index*/, const char * /*name_space*/, const char * /*class_name*/) {
}

void T_explorer_client::explorer_node_object_content_update_result(wow_uint_32 /*session_id*/, wow_uint_32 /*system_id*/, wow_uint_32 /*request_id*/, wow_uint_32 /*errors_count*/) {
}

void T_explorer_client::explorer_node_binary_content_size(wow_uint_32 /*session_id*/, wow_uint_32 /*system_id*/, wow_uint_64 /*size*/, wow_uint_32 /*result*/) {
}

void T_explorer_client::explorer_node_binary_content_response(wow_uint_32 /*session_id*/, wow_uint_32 /*system_id*/, wow_uint_64 /*offset*/, int /*inserted*/, const T_wow_data * /*data*/, int /*more_data*/, wow_uint_32 /*result*/) {
}

void T_explorer_client::explorer_node_binary_content_response_update(wow_uint_32 /*session_id*/, wow_uint_32 /*system_id*/, int /*truncated*/) {
}

void T_explorer_client::explorer_node_children_response(wow_uint_32 /*session_id*/, wow_uint_32 /*system_id*/, const T_consistent_protocol_children * /*children*/, wow_uint_32 /*result*/) {
}

void use_object_values(T_ecma_result_object * dst, T_consistent_protocol_object_format_field * format_field, T_consistent_protocol_object_value ** value) {
	while (format_field != NULL) {
		if (format_field->get_first_field() != NULL) {
			T_ecma_result_object * object_loc = NEW T_ecma_result_object(NULL, format_field->get_field_index());
			T_ecma_variable * variable = dst->create_variable(format_field->get_name());
			variable->get_variable_value_address()->set_with_linked_object(object_loc);
			use_object_values(object_loc, format_field->get_first_field(), value);
		}
		else if ((*value != NULL) && (format_field->get_field_index() == (*value)->get_field_index())) {
			if (format_field->get_query() == NULL) {
				T_ecma_variable * variable = dst->create_variable(format_field->get_name());
				(*value)->assign_to(variable->get_variable_value_address());
			}
			else {
				T_ecma_result_object_query * query = dst->create_query(format_field->get_name(), format_field->get_query());
				(*value)->assign_to(query->get_value_address());
			}

			*value = (*value)->get_next();
		}

		format_field = format_field->get_next();
	}
}

void T_explorer_client::explorer_object_response(wow_uint_32 /*session_id*/, wow_uint_32 /*system_id*/, const T_consistent_protocol_object * new_object, wow_uint_32 /*list_system_id*/) {
	if (new_object != NULL) {
		T_ecma_scope * scope = NEW T_ecma_scope(get_system(), get_system()->get_scope());
		T_ecma_result_object * row_object = NEW T_ecma_result_object(NULL, 0);
		scope->create_variable("row")->get_variable_value_address()->set_object(row_object AND_TO_BE_DELETED_ARGUMENTS);
		T_consistent_protocol_object_value * value = new_object->get_first_value();
		use_object_values(row_object, get_system()->get_object_format()->get_first_field(), &value);
//T_wow_file_stream stream(stderr);
//row_object->dump_object(&stream, 0);
		T_report_column * column = get_system()->get_first_column();

		while (column != NULL) {
			T_ecma_value value;

			if (column->get_expression() != NULL) column->get_expression()->execute_for_value(&value, scope, TRUE, FALSE);

			if (get_system()->is_query_raw_dates() && value.is_object() && value.get_object()->is_date())
				printf("%f%s", ((T_ecma_date_object *)value.get_object())->get_date()->get_date(), get_system()->get_separator());
			else {
				value.to_string();
				printf("%s%s", value.get_string()->get_string(), get_system()->get_separator());
			}
			column = column->get_next();
		}

		printf("\n");
		row_object->sub_link(TO_BE_DELETED_ARGUMENTS);
		scope->sub_link(TO_BE_DELETED_ARGUMENTS);
	}

	if (--waiting_objects == 0) {
		get_system()->set_system_ended();
		get_connection()->set_to_be_deleted(TO_BE_DELETED_ARGUMENTS);
	}
}

void T_explorer_client::explorer_list_response(wow_uint_32 /*session_id*/, wow_uint_32 /*system_id*/, const T_consistent_protocol_list * list) {
//wow_log("format=%p items=%d\n", get_system()->get_object_format(), (list == NULL) ? 0 : list->get_items_count());
	if ((list == NULL) || (list->get_items_count() == 0)) {
		get_system()->set_system_ended();
		get_connection()->set_to_be_deleted(TO_BE_DELETED_ARGUMENTS);
	}
	else if (get_system()->get_object_format() != NULL) {
		explorer_set_object_format(1, get_system()->get_object_format());
		wow_uint_32 id_loc = 2;
		const T_consistent_protocol_list_item * item = list->get_first_item();
		T_wow_string_stream buffer(strlen(get_system()->get_path()) + 128);

		while (item != NULL) {
			if (item->get_path() == NULL) {
				explorer_query_object(1, id_loc++, get_system()->get_path(), item->get_item_id(), 1, 0);
			}
			else {
				//TODO: traiter_les_path_absolus;
				buffer.reset();
				buffer.add("%s/%s", get_system()->get_path(), item->get_path());
				explorer_query_object(1, id_loc++, buffer.get_data(), item->get_item_id(), 1, 0);
			}

			item = item->get_next();
		}

		waiting_objects = list->get_items_count();
	}
	else {
		const T_consistent_protocol_list_item * item = list->get_first_item();

		while (item != NULL) {
			if (item->get_path() != NULL) printf("%d@%s%s\n", item->get_item_id(), item->get_path(), get_system()->get_separator());
			else printf("%d%s\n", item->get_item_id(), get_system()->get_separator());

			item = item->get_next();
		}

		get_system()->set_system_ended();
		get_connection()->set_to_be_deleted(TO_BE_DELETED_ARGUMENTS);
	}
}

void T_explorer_client::explorer_list_object_response(wow_uint_32 /*session_id*/, wow_uint_32 /*system_id*/, const T_consistent_protocol_object * /*object*/) {
}

void T_explorer_client::explorer_server_event(wow_uint_32 /*session_id*/, const char * /*source*/, const char * /*target*/, double /*delay*/, const char * /*event_name*/, const T_consistent_protocol_named_object * /*object*/) {
}

// }{ -------------------------------------------------------------------------
