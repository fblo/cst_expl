#ifndef CCENTER_COMMON_IDL_H__
#define CCENTER_COMMON_IDL_H__

#if !defined(_Windows) && !defined(MacOS)
//ident "@(#)ccenter/common/idl.h (c) Copyright Consistent Software 2002-2009"
#endif

#include <system/common/idl.h>
#include "ccenter_public.h"
#ifdef WOW_SYSTEM
#include "ccenter_system.h"
#endif
#include <ccenter/idl/ccenter.idl.h>
#ifdef CCENTER_CCXML_CLASSES
#include "ccxml_classes.h"
#endif
#ifdef CCENTER_DISPATCH_CLASSES
#include "dispatch_classes.h"
#endif
#ifdef CCENTER_DISPATCH_DB_CLASSES
#include "dispatch_db_classes.h"
#endif
#ifdef CCENTER_STATS_MYSQL_CLASSES
#include "stats_mysql_classes.h"
#endif
#ifdef CCENTER_DB_LOGGER_CLASSES
#include "db_logger_classes.h"
#endif
#ifdef CCENTER_DB_LOGGER_DB_CLASSES
#include "db_logger_db_classes.h"
#endif
#ifdef CCENTER_SCHEDULER_CLASSES
#include "scheduler_classes.h"
#endif
#ifdef CCENTER_ALERT_CLASSES
#include "alert_classes.h"
#endif
#ifdef CCENTER_SYNTHESIS_CLASSES
#include "synthesis_classes.h"
#endif
#ifdef CCENTER_TTS_CLASSES
#include "tts_classes.h"
#endif
#ifdef CCENTER_OOCC_CLASSES
#include "oocc_classes.h"
#endif
#ifdef CCENTER_OOID_CLASSES
#include "ooid_classes.h"
#endif
#ifdef CCENTER_VOIP_CLASSES
#include "voip_classes.h"
#endif
#ifdef CCENTER_PROXY_CLASSES
#include "proxy_classes.h"
#endif
#ifdef CCENTER_QUEUES_CLASSES
#include "queues_classes.h"
#endif
#ifdef CCENTER_LOAD_CLASSES
#include "load_classes.h"
#endif
#ifdef CCENTER_CALL_CONTROL_CLASSES
#include "call_control_classes.h"
#endif
#ifdef W3C_XFORMS_CLASSES
#include "w3c_xforms_classes.h"
#endif
#ifdef W3C_NLSM_CLASSES
#include "w3c_nlsm_classes.h"
#endif
#ifdef W3C_GRAMMAR_CLASSES
#include "w3c_grammar_classes.h"
#endif
#ifdef W3C_SSML_CLASSES
#include "w3c_ssml_classes.h"
#endif
#ifdef W3C_VXML_CLASSES
#include "w3c_vxml_classes.h"
#endif
#ifdef W3C_CCXML_CLASSES
#include "w3c_ccxml_classes.h"
#endif
#ifdef CCENTER_SCE_CLASSES
#include "sce_classes.h"
#endif
#ifdef CCENTER_SCE_PARSER
#include "sce_parser.h"
#endif
#ifdef CCENTER_OOV_CLASSES
#include "oov_classes.h"
#endif
#ifdef CCENTER_SCRIPTING_CLASSES
#include "scripting_classes.h"
#endif
#ifdef CCENTER_ENGINE_CLASSES
#include "engine_classes.h"
#endif
#ifdef CCENTER_UPDATE_SERVER_CLASSES
#include "update_server_classes.h"
#endif
#ifdef CCENTER_RSC_PARSER
#include "rsc_parser.h"
#endif
#ifdef CCENTER_UPDATE
#include "explorer_client.h"
#include "update.h"
#endif
#ifdef CCENTER_XSD_GEN
#include "xsd_gen.h"
#endif
#ifdef CCENTER_REPORT
#include "ecma_lib.h"
#include "explorer_client.h"
#include "report.h"
#endif
#ifdef CCENTER_VOIP
#include "server_head_client.h"
#include "server_head_watcher_client.h"
#include "server_explorer_client.h"
#include "call_control_client.h"
#include "tts_control_client.h"
#include "inter_call_control_server.h"
#include "call_control_logger_sender.h"
#include "dtmf.h"
#include "g711.h"
#include "voip_transaction.h"
#include "rtsp_client.h"
#include "media_client.h"
#include "voip_call.h"
#include "sip_server.h"
#include "mrcp_server.h"
#include "call_control.h"
#include "voip.h"
#endif
#ifdef CCENTER_LOAD
#include "server_head_client.h"
#include "server_head_watcher_client.h"
#include "server_explorer_client.h"
#include "call.h"
#include "call_control_server.h"
#include "load.h"
#include "explorer_server.h"
#endif
#ifdef CCENTER_CCXML
#include "server_head_client.h"
#include "server_head_watcher_client.h"
#include "server_explorer_client.h"
#include "queues_client.h"
#include "ccxml_logger_sender.h"
#include "call_control_server.h"
#include "user_control_server.h"
#include "explorer_server.h"
#include "ccxml_ws_client.h"
#include "ccxml.h"
#include "ccxml_session.h"
#include "vxml_session.h"
#include "wav_session.h"
#endif
#ifdef CCENTER_QUEUES
#include "server_head_client.h"
#include "server_head_watcher_client.h"
#include "server_explorer_client.h"
#include "queues_logger_sender.h"
#include "queues_server.h"
#include "queues.h"
#endif
#ifdef CCENTER_PROXY
#include "explorer_query.h"
#include "ecma_lib.h"
#include "server_head_client.h"
#include "server_head_watcher_client.h"
#include "server_explorer_client.h"
#include "proxy_explorer_server.h"
#include "user_control_client.h"
#include "proxy_logger_sender.h"
#include "voip_transaction.h"
#include "g711.h"
#include "rtsp_client.h"
#include "media_client.h"
#include "voip_call.h"
#include "sip_server.h"
#include "call_control_client.h"
#include "inter_call_control_client.h"
#include "engine_session.h"
#include "proxy.h"
#include "proxy_socket.h"
#endif
#ifdef CCENTER_DISPATCH
#include "explorer_server.h"
#include "server_head_client.h"
#include "server_head_watcher_client.h"
#include "logger_control_client.h"
#include "dispatch_logger_sender.h"
#include "proxy_logger_decoder.h"
#include "scheduler_logger_decoder.h"
#include "call_control_logger_decoder.h"
#include "ccxml_logger_decoder.h"
#include "queues_logger_decoder.h"
#include "logger_logger.h"
#include "dispatch.h"
#endif
#ifdef CCENTER_DB_LOGGER
#include "explorer_server.h"
#include "explorer_client.h"
#include "server_head_client.h"
#include "server_head_watcher_client.h"
#include "logger_control_client.h"
#include "db_logger_logger_sender.h"
#include "ccxml_logger_decoder.h"
#include "queues_logger_decoder.h"
#include "db_logger.h"
#endif
#ifdef CCENTER_STATS_MYSQL
#include <mysql/mysql.h>
#include "explorer_server.h"
#include "explorer_client.h"
#include "server_head_client.h"
#include "server_head_watcher_client.h"
#include "logger_control_client.h"
#include "call_consolidation.h"
#include "task_consolidation.h"
#include "agent_consolidation.h"
#include "stats_mysql_logger_sender.h"
#include "ccxml_logger_decoder.h"
#include "queues_logger_decoder.h"
#include "stats_mysql.h"
#endif
#ifdef CCENTER_SCHEDULER
#include "explorer_server.h"
#include "server_head_client.h"
#include "server_head_watcher_client.h"
#include "server_explorer_client.h"
#include "scheduler_logger_sender.h"
#include "scheduler.h"
#include "calendar.h"
#endif
#ifdef CCENTER_ALERT
#include "explorer_query.h"
#include "ecma_lib.h"
#include "explorer_server.h"
#include "server_head_client.h"
#include "server_head_watcher_client.h"
#include "server_explorer_client.h"
#include "alert_logger_sender.h"
#include "alert.h"
#endif
#ifdef CCENTER_TTS_ACAPELA
#include <nscube.h>
#include "tts_control_server.h"
#include "server_head_client.h"
#include "server_head_watcher_client.h"
#include "tts_logger_sender.h"
#include "tts_acapela.h"
#endif
#ifdef CCENTER_UPDATE_SERVER
#include "server_head_client.h"
#include "server_head_watcher_client.h"
#include "explorer_client.h"
#include "user_control_client.h"
#include "update_server_logger_sender.h"
//#include "sce_server.h"
#include "update_server.h"
#endif

#endif
