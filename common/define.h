#ifndef CCENTER_COMMON_DEFINE_H__
#define CCENTER_COMMON_DEFINE_H__

#if !defined(_Windows) && !defined(MacOS)
//ident "@(#)ccenter/common/define.h (c) Copyright Consistent Software 2002-2009"
#endif

// }{ -------------------------------------------------------------------------

#ifdef CCENTER_UPDATE
#define PROGRAM_NAME "ccenter_update"
#define PRODUCT_NAME "update"
#define T_system T_update_system
#define with_explorer_client
#define with_cryptopp_library
#define CONSISTENT_PROTOCOL_CLASSES
#define CONSISTENT_EXPLORER_CLASSES
#define CONSISTENT_HEAD_CLASSES
#define CONSISTENT_TREE_CLASSES
#define CONSISTENT_MYSQL_WS_CLASSES
#define CONSISTENT_STORE_CLASSES
#define CONSISTENT_LICENCES_CLASSES
#define CONSISTENT_MAIL_CLASSES
#define CONSISTENT_SOAP_CLASSES
#define CONSISTENT_DB_QUERY_CLASSES
#define CONSISTENT_NS_CLASSES
#define CONSISTENT_REDIRECT_PROXY_CLASSES
#define W3C_GRAMMAR_CLASSES
#define W3C_SSML_CLASSES
#define W3C_VXML_CLASSES
#define W3C_CCXML_CLASSES
#define CCENTER_VOIP_CLASSES
#define CCENTER_LOAD_CLASSES
#define CCENTER_CCXML_CLASSES
#define CCENTER_QUEUES_CLASSES
#define CCENTER_PROXY_CLASSES
#define CCENTER_DISPATCH_CLASSES
#define CONSISTENT_DB_QUERY_CLASSES
#define CCENTER_DISPATCH_DB_CLASSES
#define CCENTER_STATS_MYSQL_CLASSES
#define CCENTER_DB_LOGGER_CLASSES
#define CCENTER_DB_LOGGER_DB_CLASSES
#define CCENTER_SCHEDULER_CLASSES
#define CCENTER_ALERT_CLASSES
#define CCENTER_SYNTHESIS_CLASSES
#define CCENTER_TTS_CLASSES
#define CCENTER_OOCC_CLASSES
#define CCENTER_OOID_CLASSES
#define CCENTER_SCE_CLASSES
#define CCENTER_SCE_PARSER
#define CCENTER_OOV_CLASSES
#define CCENTER_SCRIPTING_CLASSES
#define CCENTER_ENGINE_CLASSES
#define CCENTER_RSC_PARSER
#define CCENTER_UPDATE_SERVER_CLASSES
#define W3C_XFORMS_CLASSES
#define W3C_NLSM_CLASSES
#define CONSISTENT_ECMA_SCRIPT
#define WOW_SYSTEM
#define WOW_SOCKET_CLIENT
#define WOW_XML
#define WOW_XML_PARSER
#define WOW_XML_PARSER_LOCATION
#define WOW_XML_LOADER
#define WOW_XML_DOCUMENTATION
#endif

#ifdef CCENTER_XSD_GEN
#define PROGRAM_NAME "ccenter_xsd_gen"
#define PRODUCT_NAME "xsd_gen"
#define T_system T_xsd_gen_system
#define CONSISTENT_PROTOCOL_CLASSES
#define CONSISTENT_EXPLORER_CLASSES
#define CONSISTENT_HEAD_CLASSES
#define CONSISTENT_TREE_CLASSES
#define CONSISTENT_MYSQL_WS_CLASSES
#define CONSISTENT_STORE_CLASSES
#define CONSISTENT_LICENCES_CLASSES
#define CONSISTENT_MAIL_CLASSES
#define CONSISTENT_SOAP_CLASSES
#define CONSISTENT_DB_QUERY_CLASSES
#define CONSISTENT_NS_CLASSES
#define CONSISTENT_REDIRECT_PROXY_CLASSES
#define W3C_GRAMMAR_CLASSES
#define W3C_SSML_CLASSES
#define W3C_VXML_CLASSES
#define W3C_CCXML_CLASSES
#define CCENTER_VOIP_CLASSES
#define CCENTER_LOAD_CLASSES
#define CCENTER_CCXML_CLASSES
#define CCENTER_QUEUES_CLASSES
#define CCENTER_PROXY_CLASSES
#define CCENTER_DISPATCH_CLASSES
#define CONSISTENT_DB_QUERY_CLASSES
#define CCENTER_DISPATCH_DB_CLASSES
#define CCENTER_STATS_MYSQL_CLASSES
#define CCENTER_DB_LOGGER_CLASSES
#define CCENTER_DB_LOGGER_DB_CLASSES
#define CCENTER_SCHEDULER_CLASSES
#define CCENTER_ALERT_CLASSES
#define CCENTER_SYNTHESIS_CLASSES
#define CCENTER_TTS_CLASSES
#define CCENTER_OOCC_CLASSES
#define CCENTER_OOID_CLASSES
#define CCENTER_SCE_CLASSES
#define CCENTER_OOV_CLASSES
#define CCENTER_SCRIPTING_CLASSES
#define CCENTER_ENGINE_CLASSES
#define W3C_XFORMS_CLASSES
#define W3C_NLSM_CLASSES
#define WOW_SYSTEM
#define WOW_XML
#define WOW_XML_DOCUMENTATION
#endif

#ifdef CCENTER_REPORT
#define PROGRAM_NAME "ccenter_report"
#define PRODUCT_NAME "report"
#define T_system T_report_system
#define with_explorer_client
#define CONSISTENT_PROTOCOL_CLASSES
#define CONSISTENT_EXPLORER_CLASSES
#define CONSISTENT_ECMA_SCRIPT
#define WOW_SYSTEM
#define WOW_SOCKET_CLIENT
#define WOW_XML
#endif

#ifdef CCENTER_VOIP
#define PROGRAM_NAME "ccenter_voip"
#define PRODUCT_NAME "voip"
#define LOGGER_NAME "ccenter_call_control"
#define T_system T_voip_system
#define MAX_SIMULTANEOUS_CALLS 20
#define CONSISTENT_PROGRAM
#define CONSISTENT_MODULE
#define with_head_client
#define with_head_watcher_client
#define with_explorer_client
#define with_server_explorer_client
#define with_multi_explorer_client
#define with_call_control_client
#define with_tts_control_client
#define with_inter_call_control_server
#define with_logger_client
#define with_call_control_logger_client
#define with_ns_client
#define SIP_INVITE
#define SIP_RTP
#define SIP_CALL_CONTROL
#define SIP_MRCP_ASR
#define SIP_MRCP_TTS
#define CONSISTENT_HEAD_CLASSES
#define CONSISTENT_TREE_CLASSES
#define CONSISTENT_PROTOCOL_CLASSES
#define CONSISTENT_DB_QUERY_CLASSES
#define W3C_XFORMS_CLASSES
#define W3C_NLSM_CLASSES
#define W3C_GRAMMAR_CLASSES
#define W3C_SSML_CLASSES
#define CCENTER_VOIP_CLASSES
#define CCENTER_CALL_CONTROL_CLASSES
#define WOW_SYSTEM
#define WOW_SOCKET_MULTI_SERVER
#define WOW_SOCKET_CLIENT
#define WOW_SOCKET_PARSER
#define WOW_SOCKET_HTTP_SERVER
#define WOW_XML
#define WOW_XML_PARSER
#define WOW_TIMER
#endif

#ifdef CCENTER_LOAD
#define PROGRAM_NAME "ccenter_load"
#define PRODUCT_NAME "load"
#define LOGGER_NAME "ccenter_load"
#define T_system T_load_system
#define MAX_SIMULTANEOUS_CALLS 20
#define CONSISTENT_PROGRAM
#define CONSISTENT_MODULE
#define with_head_client
#define with_head_watcher_client
#define with_explorer_client
#define with_server_explorer_client
#define with_multi_explorer_client
#define with_call_control_server
#define with_explorer_server
#define with_ns_client
#define XML_NAMING_SPACE_SERVERS
#define CONSISTENT_HEAD_CLASSES
#define CONSISTENT_TREE_CLASSES
#define CONSISTENT_PROTOCOL_CLASSES
#define CONSISTENT_DB_QUERY_CLASSES
#define CONSISTENT_EXPLORER_CLASSES
#define CONSISTENT_SOAP_CLASSES
#define W3C_XFORMS_CLASSES
#define W3C_NLSM_CLASSES
#define W3C_GRAMMAR_CLASSES
#define W3C_SSML_CLASSES
#define CCENTER_LOAD_CLASSES
#define CCENTER_CALL_CONTROL_CLASSES
#define CONSISTENT_ECMA_SCRIPT
#define WOW_SYSTEM
#define WOW_SOCKET_MULTI_SERVER
#define WOW_SOCKET_HTTP_SERVER T_proxy_socket_connection
#define WOW_SOCKET_CLIENT
#define WOW_SOCKET_PARSER
#define WOW_XML
#define WOW_XML_PARSER
#define WOW_XML_WEB_SERVICE_COMPLEX_TYPE
#define WOW_TIMER
#endif

#ifdef CCENTER_CCXML
#define PROGRAM_NAME "ccenter_ccxml"
#define PRODUCT_NAME "ccxml"
#define LOGGER_NAME "ccenter_ccxml"
#define T_system T_ccxml_system
#define MAX_SIMULTANEOUS_CALLS 20
#define CONSISTENT_PROGRAM
#define CONSISTENT_MODULE
#define with_head_client
#define with_head_watcher_client
#define with_explorer_client
#define with_server_explorer_client
#define with_multi_explorer_client
#define with_logger_client
#define with_ccxml_logger_client
#define with_queues_client
#define with_call_control_server
#define with_user_control_server
#define with_explorer_server
#define with_ns_client
#define with_cryptopp_library
#define CONSISTENT_HEAD_CLASSES
#define CONSISTENT_TREE_CLASSES
#define CONSISTENT_PROTOCOL_CLASSES
#define CONSISTENT_SOAP_CLASSES
#define CCENTER_CCXML_CLASSES
#define CCENTER_QUEUES_CLASSES
#define CCENTER_CALL_CONTROL_CLASSES
#define CCENTER_ENGINE_CLASSES
#define CONSISTENT_DB_QUERY_CLASSES
#define W3C_XFORMS_CLASSES
#define W3C_NLSM_CLASSES
#define W3C_GRAMMAR_CLASSES
#define W3C_SSML_CLASSES
#define W3C_VXML_CLASSES
#define W3C_CCXML_CLASSES
#define CONSISTENT_ECMA_SCRIPT
#define CONSISTENT_ECMA_WS_CLIENT
#define CONSISTENT_XQUERY
#define WOW_SYSTEM
#define WOW_SOCKET_SERVER
#define WOW_SOCKET_CLIENT
#define WOW_SOCKET_HTTP_SERVER
#define WOW_XML
#define WOW_XML_PARSER
#define WOW_XML_LOADER
#define WOW_XML_WATCHER
#define WOW_TIMER
#endif

#ifdef CCENTER_QUEUES
#define PROGRAM_NAME "ccenter_queues"
#define PRODUCT_NAME "queues"
#define LOGGER_NAME "ccenter_queues"
#define T_system T_queues_system
#define MAX_SIMULTANEOUS_CALLS 20
#define CONSISTENT_PROGRAM
#define CONSISTENT_MODULE
#define with_head_client
#define with_head_watcher_client
#define with_explorer_client
#define with_server_explorer_client
#define with_multi_explorer_client
#define with_logger_client
#define with_queues_logger_client
#define with_queues_server
#define with_ns_client
#define CONSISTENT_HEAD_CLASSES
#define CONSISTENT_TREE_CLASSES
#define CONSISTENT_PROTOCOL_CLASSES
#define CONSISTENT_DB_QUERY_CLASSES
#define CCENTER_QUEUES_CLASSES
#define CONSISTENT_ECMA_SCRIPT
#define WOW_SYSTEM
#define WOW_SOCKET_SERVER
#define WOW_SOCKET_CLIENT
#define WOW_XML
#define WOW_TIMER
#endif

#ifdef CCENTER_PROXY
#define PROGRAM_NAME "ccenter_proxy"
#define PRODUCT_NAME "proxy"
#define LOGGER_NAME "ccenter_proxy"
#define T_system T_proxy_system
#define MAX_SIMULTANEOUS_CALLS 20
#define CONSISTENT_PROGRAM
#define CONSISTENT_MODULE
#define with_proxy_explorer_server
#define with_proxy_explorer_server_with_user_control
#define with_explorer_server
#define with_explorer_server_ws "http://www.consistent.com/soap/explorer.wsdl"
#define with_server_explorer_client
#define with_explorer_client_session
#define with_proxy_web_service_server
#define with_head_client
#define with_head_watcher_client
#define with_user_control_client
#define with_call_control_client
#define with_inter_call_control_client
#define with_explorer_client
#define with_multi_explorer_client
#define with_logger_client
#define with_proxy_logger_client
#define with_ns_client
#define WOW_FTP_SERVER
#define SIP_REGISTER
#define SIP_INVITE
#define STUN_SERVER
#define XML_NAMING_SPACE_SERVERS
#define CONSISTENT_PROTOCOL_CLASSES
#define CONSISTENT_EXPLORER_CLASSES
#define CONSISTENT_HEAD_CLASSES
#define CONSISTENT_TREE_CLASSES
#define CONSISTENT_SOAP_CLASSES
#define CONSISTENT_MAIL_CLASSES
#define CONSISTENT_DB_QUERY_CLASSES
#define CONSISTENT_NS_CLASSES
#define W3C_XFORMS_CLASSES
#define W3C_NLSM_CLASSES
#define W3C_GRAMMAR_CLASSES
#define W3C_SSML_CLASSES
#define W3C_VXML_CLASSES
#define W3C_CCXML_CLASSES
#define CCENTER_VOIP_CLASSES
#define CCENTER_CALL_CONTROL_CLASSES
#define CCENTER_LOAD_CLASSES
#define CCENTER_CCXML_CLASSES
#define CCENTER_QUEUES_CLASSES
#define CCENTER_PROXY_CLASSES
#define CONSISTENT_DB_QUERY_CLASSES
#define CCENTER_DISPATCH_CLASSES
#define CCENTER_DISPATCH_DB_CLASSES
#define CCENTER_STATS_MYSQL_CLASSES
#define CCENTER_DB_LOGGER_CLASSES
#define CCENTER_DB_LOGGER_DB_CLASSES
#define CCENTER_SCHEDULER_CLASSES
#define CCENTER_ALERT_CLASSES
#define CCENTER_TTS_CLASSES
#define CCENTER_OOCC_CLASSES
#define CCENTER_OOID_CLASSES
#define CCENTER_ENGINE_CLASSES
#define CCENTER_SCRIPTING_CLASSES
#define CONSISTENT_ECMA_SCRIPT
#define CONSISTENT_EXPLORER_LIST_QUERY
#define WOW_SYSTEM
#define WOW_SOCKET_MULTI_SERVER
#define WOW_SOCKET_CLIENT
#define WOW_SOCKET_HTTP_SERVER T_proxy_socket_connection
#define WOW_SOCKET_PARSER
#define WOW_XML
#define WOW_XML_PARSER
#define WOW_XML_WEB_SERVICE_COMPLEX_TYPE
#define WOW_TIMER
#define WOW_XML_DOCUMENTATION
#endif

#ifdef CCENTER_DISPATCH
#define PROGRAM_NAME "ccenter_dispatch"
#define PRODUCT_NAME "dispatch"
#define LOGGER_NAME "ccenter_dispatch"
#define T_system T_dispatch_system
#define MAX_SIMULTANEOUS_CALLS 20
#define CONSISTENT_PROGRAM
#define CONSISTENT_MODULE
#define with_explorer_server
#define with_head_client
#define with_head_watcher_client
#define with_logger_client
#define with_logger_control_client
#define with_dispatch_logger_client
#define with_proxy_logger_decoder
#define with_scheduler_logger_decoder
#define with_call_control_logger_decoder
#define with_ccxml_logger_decoder
#define with_queues_logger_decoder
#define with_ns_client
#define XML_NAMING_SPACE_SERVERS
#define CONSISTENT_HEAD_CLASSES
#define CONSISTENT_TREE_CLASSES
#define CONSISTENT_PROTOCOL_CLASSES
#define CONSISTENT_EXPLORER_CLASSES
#define CONSISTENT_DB_QUERY_CLASSES
#define CONSISTENT_DB_QUERY
#define CCENTER_QUEUES_CLASSES
#define CCENTER_CCXML_CLASSES
#define CCENTER_DISPATCH_CLASSES
#define CCENTER_DISPATCH_DB_CLASSES
#define CONSISTENT_XQUERY
#define CONSISTENT_ECMA_SCRIPT
#define WOW_SYSTEM
#define WOW_SOCKET_SERVER
#define WOW_SOCKET_CLIENT
#define WOW_XML
#define WOW_XML_WATCHER
#define WOW_XML_LOADER
#define WOW_XML_PARSER
#define WOW_TIMER
#endif

#ifdef CCENTER_DB_LOGGER
#define PROGRAM_NAME "ccenter_db_logger"
#define PRODUCT_NAME "db_logger"
#define LOGGER_NAME "ccenter_db_logger"
#define T_system T_db_logger_system
#define MAX_SIMULTANEOUS_CALLS 20
#define CONSISTENT_PROGRAM
#define CONSISTENT_MODULE
#define with_explorer_server
#define with_explorer_client
#define with_head_client
#define with_head_watcher_client
#define with_logger_client
#define with_logger_control_client
#define with_db_logger_logger_client
#define with_ccxml_logger_decoder
#define with_queues_logger_decoder
#define with_ns_client
#define XML_NAMING_SPACE_SERVERS
#define CONSISTENT_HEAD_CLASSES
#define CONSISTENT_TREE_CLASSES
#define CONSISTENT_PROTOCOL_CLASSES
#define CONSISTENT_DB_QUERY_CLASSES
#define CCENTER_CCXML_CLASSES
#define CCENTER_QUEUES_CLASSES
#define CCENTER_DB_LOGGER_CLASSES
#define CCENTER_DB_LOGGER_DB_CLASSES
#define CONSISTENT_ECMA_SCRIPT
#define CONSISTENT_XQUERY
#define WOW_SYSTEM
#define WOW_SOCKET_SERVER
#define WOW_SOCKET_CLIENT
#define WOW_XML
#define WOW_TIMER
#endif

#ifdef CCENTER_STATS_MYSQL
#define PROGRAM_NAME "ccenter_stats_mysql"
#define PRODUCT_NAME "stats_mysql"
#define LOGGER_NAME "ccenter_stats_mysql"
#define T_system T_stats_mysql_system
#define MAX_SIMULTANEOUS_CALLS 20
#define CONSISTENT_PROGRAM
#define CONSISTENT_MODULE
#define with_explorer_server
#define with_explorer_client
#define with_head_client
#define with_head_watcher_client
#define with_logger_client
#define with_logger_control_client
#define with_db_logger_logger_client
#define with_ccxml_logger_decoder
#define with_queues_logger_decoder
#define with_ns_client
#define XML_NAMING_SPACE_SERVERS
#define CONSISTENT_HEAD_CLASSES
#define CONSISTENT_TREE_CLASSES
#define CONSISTENT_PROTOCOL_CLASSES
#define CONSISTENT_DB_QUERY_CLASSES
#define CCENTER_CCXML_CLASSES
#define CCENTER_QUEUES_CLASSES
#define CCENTER_STATS_MYSQL_CLASSES
#define CONSISTENT_ECMA_SCRIPT
#define CONSISTENT_XQUERY
#define WOW_SYSTEM
#define WOW_SOCKET_SERVER
#define WOW_SOCKET_CLIENT
#define WOW_XML
#define WOW_XML_PARSER
#define WOW_XML_LOADER
#define WOW_TIMER
#endif

#ifdef CCENTER_SCHEDULER
#define PROGRAM_NAME "ccenter_scheduler"
#define PRODUCT_NAME "scheduler"
#define LOGGER_NAME "ccenter_scheduler"
#define T_system T_scheduler_system
#define MAX_SIMULTANEOUS_CALLS 20
#define CONSISTENT_PROGRAM
#define CONSISTENT_MODULE
#define with_explorer_server
#define with_head_client
#define with_head_watcher_client
#define with_explorer_client
#define with_server_explorer_client
#define with_multi_explorer_client
#define with_logger_client
#define with_scheduler_logger_client
#define with_ns_client
#define XML_NAMING_SPACE_SERVERS
#define CONSISTENT_HEAD_CLASSES
#define CONSISTENT_TREE_CLASSES
#define CONSISTENT_PROTOCOL_CLASSES
#define CONSISTENT_DB_QUERY_CLASSES
#define CCENTER_SCHEDULER_CLASSES
#define CONSISTENT_XQUERY
#define WOW_SYSTEM
#define WOW_SOCKET_SERVER
#define WOW_SOCKET_CLIENT
#define WOW_XML
#define WOW_XML_WATCHER
#define WOW_TIMER
#endif

#ifdef CCENTER_ALERT
#define PROGRAM_NAME "ccenter_alert"
#define PRODUCT_NAME "alert"
#define LOGGER_NAME "ccenter_alert"
#define T_system T_alert_system
#define MAX_SIMULTANEOUS_CALLS 20
#define CONSISTENT_PROGRAM
#define CONSISTENT_MODULE
#define with_explorer_server
#define with_head_client
#define with_head_watcher_client
#define with_explorer_client
#define with_server_explorer_client
#define with_multi_explorer_client
#define with_logger_client
#define with_alert_logger_client
#define with_ns_client
#define XML_NAMING_SPACE_SERVERS
#define CONSISTENT_HEAD_CLASSES
#define CONSISTENT_TREE_CLASSES
#define CONSISTENT_PROTOCOL_CLASSES
#define CONSISTENT_DB_QUERY_CLASSES
#define CCENTER_ALERT_CLASSES
#define CONSISTENT_SOAP_CLASSES
#define CONSISTENT_ECMA_SCRIPT
#define CONSISTENT_ECMA_WS_CLIENT
#define CONSISTENT_EXPLORER_LIST_QUERY
#define CONSISTENT_REQUESTS
#define WOW_SYSTEM
#define WOW_SOCKET_SERVER
#define WOW_SOCKET_CLIENT
#define WOW_SOCKET_HTTP_SERVER
#define WOW_XML
#define WOW_XML_WATCHER
#define WOW_XML_PARSER
#define WOW_XML_LOADER
#define WOW_TIMER
#endif

#ifdef CCENTER_TTS_ACAPELA
#define PROGRAM_NAME "ccenter_tts_accapela"
#define PRODUCT_NAME "tts_acapela"
#define LOGGER_NAME "ccenter_tts"
#define T_system T_tts_acapela_system
#define MAX_SIMULTANEOUS_CALLS 20
#define CONSISTENT_PROGRAM
#define CONSISTENT_MODULE
#define with_tts_control_server
#define with_head_client
#define with_head_watcher_client
#define with_logger_client
#define with_tts_logger_client
#define with_ns_client
//#define XML_NAMING_SPACE_SERVERS
#define CONSISTENT_HEAD_CLASSES
#define CONSISTENT_TREE_CLASSES
#define CONSISTENT_PROTOCOL_CLASSES
#define CONSISTENT_DB_QUERY_CLASSES
#define CCENTER_TTS_CLASSES
#define W3C_SSML_CLASSES
#define WOW_SYSTEM
#define WOW_SOCKET_SERVER
#define WOW_SOCKET_CLIENT
#define WOW_XML
#define STD_MALLOC
#define WOW_TIMER
#endif

#ifdef CCENTER_UPDATE_SERVER
#define PROGRAM_NAME "ccenter_update_server"
#define PRODUCT_NAME "update_server"
#define LOGGER_NAME "ccenter_update_server"
#define T_system T_update_server_system
#define MAX_SIMULTANEOUS_CALLS 20
#define CONSISTENT_PROGRAM
#define CONSISTENT_MODULE
#define with_head_client
#define with_head_watcher_client
#define with_logger_client
#define with_update_server_logger_client
#define with_explorer_client
#define with_user_control_client
#define with_cryptopp_library
//#define XML_NAMING_SPACE_SERVERS
#define CONSISTENT_PROTOCOL_CLASSES
#define CONSISTENT_HEAD_CLASSES
#define CONSISTENT_TREE_CLASSES
#define CONSISTENT_EXPLORER_CLASSES
#define CONSISTENT_MYSQL_WS_CLASSES
#define W3C_GRAMMAR_CLASSES
#define W3C_SSML_CLASSES
#define W3C_VXML_CLASSES
#define W3C_CCXML_CLASSES
#define CCENTER_CCXML_CLASSES
#define CCENTER_UPDATE_SERVER_CLASSES
#define CCENTER_VOIP_CLASSES
#define CCENTER_LOAD_CLASSES
#define CCENTER_QUEUES_CLASSES
#define CCENTER_PROXY_CLASSES
#define CCENTER_DISPATCH_CLASSES
#define CCENTER_DISPATCH_DB_CLASSES
#define CCENTER_SCHEDULER_CLASSES
#define CCENTER_TTS_CLASSES
#define CONSISTENT_SOAP_CLASSES
#define CONSISTENT_ECMA_SCRIPT
#define CONSISTENT_STORE_CLASSES
#define CCENTER_DB_LOGGER_CLASSES
#define CCENTER_DB_LOGGER_DB_CLASSES
#define CONSISTENT_DB_QUERY_CLASSES
//#define CONSISTENT_DB_QUERY
#define WOW_SYSTEM
#define WOW_SOCKET_MULTI_SERVER
#define WOW_SOCKET_CLIENT
#define WOW_SOCKET_PARSER
#define WOW_XML
#define WOW_XML_PARSER
#define WOW_XML_WEB_SERVICE_COMPLEX_TYPE
#define WOW_TIMER
#endif

#ifdef CCENTER_LIBCCENTER
#define with_explorer_client
#define CCENTER_SCHEDULER_CLASSES
#define CONSISTENT_PROTOCOL_CLASSES
#define CONSISTENT_XQUERY
#define WOW_XML
#define WOW_DATE
#define WOW_XML_PARSER
#endif

#ifdef CONSISTENT_PROGRAM
#define WOW_SOCKET_HTTP_CLIENT
#endif

#ifdef WOW_XML
#define WOW_XML_DUMP
#define WOW_STREAM
#endif

#define WOW_DATE
#define MAX_NETWORK_BUFFER_SIZE 8000

// }{ -------------------------------------------------------------------------

#endif
