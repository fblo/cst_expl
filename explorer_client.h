#ifndef CCENTER_REPORT_EXPLORER_CLIENT_H__
#define CCENTER_REPORT_EXPLORER_CLIENT_H__

#if !defined(_Windows) && !defined(MacOS)
//ident "@(#)ccenter/report/explorer_client.h (c) Copyright Consistent Software 2002-2005"
#endif

class T_report_system;

class T_explorer_client : public T_consistent_client {
	read_only_boolean_field(connected_once)
	read_only_field(waiting_objects, wow_uint_32)
public:
	overload_link(explorer_client);
	T_explorer_client(T_report_system * new_system, const char * new_server_address, wow_uint_16 new_server_port);
	virtual ~T_explorer_client();
	T_report_system * get_system(void) const {
		return (T_report_system *)T_consistent_client::get_system();
	}
	virtual void load_naming_space(const char * path);
	virtual void connected(void);
	virtual void server_ask_to_disconnect(void);
	explorer_fields
};

#endif
