
$(d)/%.o:					ccenter/idl/ccenter.idl.h

$(d)/ccenter_idl.o:			ccenter/idl/ccenter.idl.cpp
							$(COMP)

$(d)/ccenter_system.o:		ccenter/public/ccenter_system.cpp
							$(COMP)

$(d)/voip_classes.o:		ccenter/public/voip_classes.cpp
							$(COMP)

$(d)/load_classes.o:		ccenter/public/load_classes.cpp
							$(COMP)

$(d)/call_control_classes.o:	ccenter/public/call_control_classes.cpp
								$(COMP)

$(d)/ccxml_classes.o:		ccenter/public/ccxml_classes.cpp
							$(COMP)

$(d)/queues_classes.o:		ccenter/public/queues_classes.cpp
							$(COMP)

$(d)/proxy_classes.o:		ccenter/public/proxy_classes.cpp
							$(COMP)

$(d)/dispatch_classes.o:	ccenter/public/dispatch_classes.cpp
							$(COMP)

$(d)/dispatch_db_classes.o:	ccenter/public/dispatch_db_classes.cpp
							$(COMP)

$(d)/stats_mysql_classes.o:	ccenter/public/stats_mysql_classes.cpp
							$(COMP)

$(d)/db_logger_classes.o:	ccenter/public/db_logger_classes.cpp
							$(COMP)

$(d)/db_logger_db_classes.o:	ccenter/public/db_logger_db_classes.cpp
								$(COMP)

$(d)/scheduler_classes.o:	ccenter/public/scheduler_classes.cpp
							$(COMP)

$(d)/alert_classes.o:		ccenter/public/alert_classes.cpp
							$(COMP)

$(d)/synthesis_classes.o:	ccenter/public/synthesis_classes.cpp
							$(COMP)

$(d)/tts_classes.o:			ccenter/public/tts_classes.cpp
							$(COMP)

$(d)/oocc_classes.o:		ccenter/public/oocc_classes.cpp
							$(COMP)

$(d)/ooid_classes.o:		ccenter/public/ooid_classes.cpp
							$(COMP)

$(d)/w3c_ccxml_classes.o:	ccenter/public/w3c_ccxml_classes.cpp
							$(COMP)

$(d)/w3c_vxml_classes.o:	ccenter/public/w3c_vxml_classes.cpp
							$(COMP)

$(d)/w3c_ssml_classes.o:	ccenter/public/w3c_ssml_classes.cpp
							$(COMP)

$(d)/w3c_grammar_classes.o:	ccenter/public/w3c_grammar_classes.cpp
							$(COMP)

$(d)/w3c_nlsm_classes.o:	ccenter/public/w3c_nlsm_classes.cpp
							$(COMP)

$(d)/w3c_xforms_classes.o:	ccenter/public/w3c_xforms_classes.cpp
							$(COMP)

$(d)/sce_classes.o:			ccenter/public/sce_classes.cpp
							$(COMP)

$(d)/sce_parser.o:			ccenter/public/sce_parser.cpp
							$(COMP)

$(d)/oov_classes.o:			ccenter/public/oov_classes.cpp
							$(COMP)

$(d)/engine_classes.o:		ccenter/public/engine_classes.cpp
							$(COMP)

$(d)/engine_session.o:		ccenter/public/engine_session.cpp
							$(COMP)

$(d)/rsc_parser.o:			ccenter/public/rsc_parser.cpp
							$(COMP)

$(d)/scripting_classes.o:	ccenter/public/scripting_classes.cpp
							$(COMP)

$(d)/sip_server.o:			ccenter/public/sip_server.cpp
							$(COMP)

$(d)/voip_transaction.o:	ccenter/public/voip_transaction.cpp
							$(COMP)

$(d)/voip_call.o:			ccenter/public/voip_call.cpp
							$(COMP)

$(d)/dtmf.o:				ccenter/public/dtmf.cpp
							$(COMP)

$(d)/mrcp_server.o:			ccenter/public/mrcp_server.cpp
							$(COMP)

$(d)/g711.o:				ccenter/public/g711.cpp
							$(COMP)

$(d)/rtsp_client.o:			ccenter/public/rtsp_client.cpp
							$(COMP)

$(d)/media_client.o:		ccenter/public/media_client.cpp
							$(COMP)

$(d)/update_server_classes.o:	ccenter/public/update_server_classes.cpp
								$(COMP)

include system/common/rules.mk
