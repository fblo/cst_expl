#ifndef CCENTER_REPORT_REPORT_H__
#define CCENTER_REPORT_REPORT_H__

#if !defined(_Windows) && !defined(MacOS)
//ident "@(#)ccenter/report/report.h (c) Copyright Consistent Software 2002-2005"
#endif

class T_w3c_ccxml;
class T_w3c_vxml;

class T_report_column : public T_wow_object {
	read_only_string_field(source)
	read_only_field(expression, T_ecma_expression *)
public:
	overload_link(report_column);
	T_report_column(T_ecma_scope * scope, const char * start, wow_uint_32 size) {
		source = wow_duplicate_sized(start, size);
		T_ecma_compiler compiler(scope, source);
		expression = compiler.parse_script_expression();

		if ((expression != NULL) && compiler.is_on_error()) {
			delete expression;
			expression = NULL;
		}
	}
	virtual ~T_report_column() {
		delete source;

		if (expression != NULL) delete expression;
	}
};

class T_report_system : public T_ccenter_system {
	read_only_string_field(login)
	read_only_string_field(password)
	read_only_string_field(path)
	read_only_field(object_id, wow_uint_32)
	read_only_string_field(field_name)
	read_only_string_field(filter)
	read_only_string_field(fields)
	read_only_string_field(separator)
	read_only_boolean_field(verbose)
	read_only_boolean_field(query_list)
	read_only_boolean_field(query_count)
	read_only_boolean_field(query_object)
	read_only_boolean_field(query_raw_dates)
	read_only_class_field(explorer_address, T_wow_server_address)
	read_only_field(explorer_client, T_explorer_client *)
	read_only_field(scope, T_ecma_scope *)
	read_only_list_field(column, report_column)
	read_only_field(object_format, T_consistent_protocol_object_format *)
	private_field(last_seconds, double)
public:
	T_report_system(void);
	virtual ~T_report_system();
	T_wow_communication * get_communication(void) const {
		return NULL;
	}
	void init_arguments(void);
	virtual int verify_arguments(void);
	virtual void init(void);
	virtual void run(void);
	virtual void stop_system(void);
	virtual wow_uint_32 idle(double seconds);
	int connect_to_servers(void);
	virtual void disconnect_from_servers(void);
};

#endif
