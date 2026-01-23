# Standard things

sp				:= $(sp).x
dirstack_$(sp)	:= $(d)
d				:= $(dir)

# Local rules and targets

CF_$(d)			:= -D_UNIX_ -DCCENTER_REPORT -I$(d) -Iccenter/public -Iccenter/common \
				   -Iwo/wow -Isystem/public
LF_$(d)			:= -lcrypt

TGTS_$(d)		:= $(d)/ccenter_report
OBJS_$(d)		:= $(d)/main.o $(d)/report.o $(d)/ccenter_system.o $(d)/explorer_client.o \
				   $(d)/system_idl.o $(d)/consistent_system.o $(d)/consistent_client.o \
				   $(d)/explorer_classes.o $(d)/protocol_classes.o \
				   $(d)/ecma_lib.o $(d)/ecma_script.o $(d)/ecma_regexp.o \
				   $(d)/consistent_variable.o $(d)/ccenter_idl.o \
				   $(d)/wow_system.o $(d)/wow_xml.o $(d)/wow_file.o $(d)/wow_socket.o \
				   $(d)/wow_outgoing_message.o $(d)/wow_incoming_message.o $(d)/wow.o
				   
DEPS_$(d)		:= $(OBJS_$(d):%=%.d)

TGT_BIN			:= $(TGT_BIN) $(TGTS_$(d))
CLEAN			:= $(CLEAN) $(TGTS_$(d)) $(OBJS_$(d)) $(DEPS_$(d)) $(TGTS_$(d)).debug

$(OBJS_$(d)):	system/idl/system.idl.h

$(TGTS_$(d)):	CF_TGT := $(CF_$(d))
$(TGTS_$(d)):	LF_TGT := $(LF_$(d))
$(TGTS_$(d)):	$(OBJS_$(d))
				$(LINK)

include ccenter/common/rules.mk

# Standard things

-include		$(DEPS_$(d))
CF_TGT 			:=
LF_TGT			:=
d				:= $(dirstack_$(sp))
sp				:= $(basename $(sp))
