#if !defined(_Windows) && !defined(MacOS)
//ident "@(#)ccenter/public/ccenter_system.C (c) Copyright Consistent Software 2002-2005"
#endif

#include "define.h"
#include "idl.h"

// }{ -------------------------------------------------------------------------

T_ccenter_system::T_ccenter_system(const char * new_arguments_list, int do_set_loaded)
	: T_consistent_system(new_arguments_list, do_set_loaded) {
#ifdef W3C_XFORMS_CLASSES
	get_naming_space_tree()->naming_spaces_insert(NEW T_w3c_xforms_naming_space);
#endif
#ifdef W3C_NLSM_CLASSES
	get_naming_space_tree()->naming_spaces_insert(NEW T_w3c_nlsm_naming_space);
#endif
#ifdef W3C_GRAMMAR_CLASSES
	get_naming_space_tree()->naming_spaces_insert(NEW T_w3c_grammar_naming_space);
#endif
#ifdef W3C_SSML_CLASSES
	get_naming_space_tree()->naming_spaces_insert(NEW T_w3c_ssml_naming_space);
#endif
#ifdef W3C_VXML_CLASSES
	get_naming_space_tree()->naming_spaces_insert(NEW T_w3c_vxml_naming_space);
#endif
#ifdef W3C_CCXML_CLASSES
	get_naming_space_tree()->naming_spaces_insert(NEW T_w3c_ccxml_naming_space);
#endif
#ifdef CCENTER_VOIP_CLASSES
	get_naming_space_tree()->naming_spaces_insert(NEW T_ccenter_voip_naming_space(head_naming_space));
#endif
#ifdef CCENTER_UPDATE_SERVER_CLASSES
	get_naming_space_tree()->naming_spaces_insert(NEW T_ccenter_update_server_naming_space(head_naming_space));
#endif
#ifdef CCENTER_LOAD_CLASSES
	get_naming_space_tree()->naming_spaces_insert(NEW T_ccenter_load_naming_space);
#endif
#ifdef CCENTER_CALL_CONTROL_CLASSES
	get_naming_space_tree()->naming_spaces_insert(NEW T_ccenter_call_control_naming_space(head_naming_space));
#endif
#ifdef CCENTER_CCXML_CLASSES
	get_naming_space_tree()->naming_spaces_insert(NEW T_ccenter_ccxml_naming_space(head_naming_space));
#endif
#ifdef CCENTER_QUEUES_CLASSES
	get_naming_space_tree()->naming_spaces_insert(NEW T_ccenter_queues_naming_space(head_naming_space));
#endif
#ifdef CCENTER_PROXY_CLASSES
	get_naming_space_tree()->naming_spaces_insert(NEW T_ccenter_proxy_naming_space(head_naming_space));
#endif
#ifdef CCENTER_DISPATCH_CLASSES
	get_naming_space_tree()->naming_spaces_insert(NEW T_ccenter_dispatch_naming_space(head_naming_space));
#endif
#ifdef CCENTER_DISPATCH_DB_CLASSES
	get_naming_space_tree()->naming_spaces_insert(NEW T_ccenter_dispatch_db_naming_space(head_naming_space));
#endif
#ifdef CCENTER_STATS_MYSQL_CLASSES
	get_naming_space_tree()->naming_spaces_insert(NEW T_ccenter_stats_mysql_naming_space(head_naming_space));
#endif
#ifdef CCENTER_DB_LOGGER_CLASSES
	get_naming_space_tree()->naming_spaces_insert(NEW T_ccenter_db_logger_naming_space(head_naming_space));
#endif
#ifdef CCENTER_DB_LOGGER_DB_CLASSES
	get_naming_space_tree()->naming_spaces_insert(NEW T_ccenter_db_logger_db_naming_space(head_naming_space));
#endif
#ifdef CCENTER_SCHEDULER_CLASSES
	get_naming_space_tree()->naming_spaces_insert(NEW T_ccenter_scheduler_naming_space());
#endif
#ifdef CCENTER_ALERT_CLASSES
	get_naming_space_tree()->naming_spaces_insert(NEW T_ccenter_alert_naming_space());
#endif
#ifdef CCENTER_SYNTHESIS_CLASSES
	get_naming_space_tree()->naming_spaces_insert(NEW T_ccenter_synthesis_naming_space());
#endif
#ifdef CCENTER_TTS_CLASSES
	get_naming_space_tree()->naming_spaces_insert(NEW T_ccenter_tts_naming_space);
#endif
#ifdef CCENTER_OOCC_CLASSES
	get_naming_space_tree()->naming_spaces_insert(NEW T_ccenter_oocc_naming_space);
#endif
#ifdef CCENTER_OOID_CLASSES
	get_naming_space_tree()->naming_spaces_insert(NEW T_ccenter_ooid_naming_space);
#endif
#ifdef CCENTER_SCRIPTING_CLASSES
	get_naming_space_tree()->naming_spaces_insert(NEW T_ccenter_scripting_naming_space);
#endif
#ifdef CCENTER_SCE_CLASSES
	get_naming_space_tree()->naming_spaces_insert(NEW T_ccenter_sce_naming_space);
#endif
#ifdef CCENTER_OOV_CLASSES
	get_naming_space_tree()->naming_spaces_insert(NEW T_ccenter_oov_naming_space);
#endif
#ifdef CCENTER_ENGINE_CLASSES
	get_naming_space_tree()->naming_spaces_insert(NEW T_ccenter_engine_naming_space);
#endif
#ifdef with_proxy_web_service_server
	get_naming_space_tree()->naming_spaces_insert(NEW T_proxy_web_service_naming_space("com.consistent.ccenter.proxy_web_service", "http://www.consistent.com/proxy_web_service.xsd"));
#endif
}

// }{ -------------------------------------------------------------------------
