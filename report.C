#if !defined(_Windows) && !defined(MacOS)
//ident "@(#)ccenter/report/report.C (c) Copyright Consistent Software 2002-2005"
#endif

#include "define.h"
#include "idl.h"

// }{ -------------------------------------------------------------------------

T_report_system::T_report_system(void)
	: T_ccenter_system("-login login -password password -server address port [-verbose] (-list | -count | -content) [-raw_dates] -path path_name [-object object_id] -field field_name [-filter request_filter] [-fields fields_list] [-separator string]", TRUE) {
	login = NULL;
	password = NULL;
	path = NULL;
	object_id = 0;
	field_name = NULL;
	filter = NULL;
	fields = NULL;
	separator = NULL;
	verbose = FALSE;
	query_list = FALSE;
	query_count = FALSE;
	query_object = FALSE;
	query_raw_dates = FALSE;
	explorer_client = NULL;
	last_seconds = 0;
	scope = NEW T_ecma_scope(this, NULL);
	scope->add_linked_function("duration", NEW T_duration_function);
	scope->add_linked_function("second_duration", NEW T_second_duration_function);
	scope->add_linked_function("minute_duration", NEW T_minute_duration_function);
	object_format = NULL;
	create_classes();
	init_arguments();
}

T_report_system::~T_report_system() {
	if (login != NULL) delete login;

	if (password != NULL) delete password;

	if (path != NULL) delete path;

	if (field_name != NULL) delete field_name;

	if (filter != NULL) delete filter;

	if (fields != NULL) delete fields;

	if (separator != NULL) delete separator;

	if (explorer_client != NULL) delete explorer_client;

	if (object_format != NULL) delete object_format;

	scope->sub_link(TO_BE_DELETED_ARGUMENTS);
}

void T_report_system::init_arguments(void) {
	T_consistent_system::init_arguments();
	add_argument("-login", &login, wow_argument_string, "user login.");
	add_argument("-password", &password, wow_argument_string, "user password.");
	add_argument("-server", &explorer_address, wow_argument_server_address, "server to report.");
	add_argument("-verbose", &verbose, wow_argument_boolean, "Add logs.");
	add_argument("-list", &query_list, wow_argument_boolean, "Request for list content.");
	add_argument("-count", &query_count, wow_argument_boolean, "Request for list count.");
	add_argument("-content", &query_object, wow_argument_boolean, "Request for object content.");
	add_argument("-raw_dates", &query_raw_dates, wow_argument_boolean, "Request date in raw format (float).");
	add_argument("-path", &path, wow_argument_string, "path in the database.");
	add_argument("-object", &object_id, wow_argument_uint_32, "Object identifier.");
	add_argument("-field", &field_name, wow_argument_string, "Field requested.");
	add_argument("-filter", &filter, wow_argument_string, "Request filter.");
	add_argument("-fields", &fields, wow_argument_string, "Fields to be returned.");
	add_argument("-separator", &separator, wow_argument_string, "Separator string used in results.");
}

int T_report_system::verify_arguments(void) {
	int result = T_consistent_system::verify_arguments();

	if (login == NULL) {
		wow_log("-login not specified.\n");
		result = FALSE;
	}

	if (explorer_address.address == NULL) {
		wow_log("-server not specified.\n");
		result = FALSE;
	}

	int count = 0;

	if (query_list) count++;

	if (query_count) count++;

	if (query_object) count++;

	if (count == 0) {
		wow_log("one of -list, -count and -content must be specified.\n");
		result = FALSE;
	}
	else if (count > 1) {
		wow_log("just one of -list, -count and -content must be specified.\n");
		result = FALSE;
	}

	if (path == NULL) {
		wow_log("-path must be specified.\n");
		result = FALSE;
	}

	if (query_list && (field_name == NULL)) {
		wow_log("-field must be specified with -list.\n");
		result = FALSE;
	}

	if (query_count && (field_name == NULL)) {
		wow_log("-field must be specified with -count.\n");
		result = FALSE;
	}

	if (query_object && (fields == NULL)) {
		wow_log("-fields must be specified with -content.\n");
		result = FALSE;
	}

	if (separator == NULL) separator = wow_duplicate("|");

	if (verbose) wow_debug_level = 2;

	return result;
}

void T_report_system::init(void) {
	T_consistent_system::init();

	if (explorer_address.address != NULL) {
		explorer_client = NEW T_explorer_client(this, explorer_address.address, explorer_address.port);
		explorer_client->connect();
	}
}

void T_report_system::run(void) {
	if (!is_all_clients_connected() && !connect_to_servers()) return;

	if (fields != NULL) {
		T_ecma_scope * request_scope = NEW T_ecma_scope(this, get_scope());
		T_ecma_request_object * request_object = NEW T_ecma_request_object;
		request_scope->create_variable("row")->get_variable_value_address()->set_object(request_object AND_TO_BE_DELETED_ARGUMENTS);
		const char * start = fields;

		while (*start != 0) {
			const char * end = strchr(start, ';');

			if (end == NULL) {
				columns_insert(NEW T_report_column(request_scope, start, strlen(start)));
				break;
			}

			columns_insert(NEW T_report_column(request_scope, start, end - start));
			start = end + 1;
		}

		T_report_column * column = get_first_column();

		while (column != NULL) {
			T_ecma_value value;

			if (column->get_expression() != NULL) column->get_expression()->execute_for_value(&value, request_scope, TRUE, FALSE);

			column = column->get_next();
		}

		object_format = allocate_protocol_object(NULL, consistent_protocol_object_format, NULL);
		object_format->set_format_id(1);
		object_format->generate(request_object, NULL);
		request_object->sub_link(TO_BE_DELETED_ARGUMENTS);
		request_scope->sub_link(TO_BE_DELETED_ARGUMENTS);
	}

	T_consistent_system::run();
}

void T_report_system::stop_system(void) {
	if (is_system_ended()) return;

	wow_log("stop system\n");
	set_system_ended();
	disconnect_from_servers();
}

wow_uint_32 T_report_system::idle(double seconds) {
	if (seconds > last_seconds + 1) {
		last_seconds = seconds;

		if (!is_all_clients_connected() && !is_system_ended()) connect_to_servers();
	}

	return is_all_clients_connected() ? 0 : 1000;
}

int T_report_system::connect_to_servers(void) {
	if (wow_debug_level >= 2) wow_log("connect to servers\n");

	set_all_clients_connected();

	if ((get_explorer_client() != NULL) && (get_explorer_client()->get_connection() == NULL) && !get_explorer_client()->connect()) return FALSE;

	return TRUE;
}

void T_report_system::disconnect_from_servers(void) {
	if ((get_explorer_client() != NULL) && (get_explorer_client()->get_connection() != NULL)) get_explorer_client()->get_connection()->set_to_be_deleted(TO_BE_DELETED_ARGUMENTS);
}

// }{ -------------------------------------------------------------------------
