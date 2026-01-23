#ifndef CCENTER_PUBLIC_CCENTER_SYSTEM_H__
#define CCENTER_PUBLIC_CCENTER_SYSTEM_H__

#if !defined(_Windows) && !defined(MacOS)
//ident "@(#)ccenter/public/ccenter_system.h (c) Copyright Consistent Software 2002-2005"
#endif

class T_ccenter_system : public T_consistent_system {
public:
	T_ccenter_system(const char * new_arguments_list, int do_set_loaded);
};

// A1001 : ccxml : vxml not found
// A1002 : ccxml : vxml application with application
// A1003 : ccxml : vxml without dialog
// A1004 : voip : sound not found
// A1005 : voip : asr disconnected
// A1006 : voip : asr failed
// A1007 : queues : configuration not found
// A1008 : queues : user variable not defined
// A1009 : queues : can't create user variable
// A1010 : queues : bad session_ranking
// A1011 : tts_acapela : can't init server
// A1012 : tts_acapela : can't create dispatcher
// A1013 : tts_acapela : can't get info about server
// A1014 : tts_acapela : can't get info about voices
// A1015 : tts_acapela : bad voice initialization
// A1016 : tts_acapela : bad voice list
// A1017 : tts_acapela : too many voices
// A1018 : tts_acapela : no matching voice
// A1019 : voip : register failed
// A1020 : ccxml : configuration not found
// A1021 : db_logger : configuration not found
// A1022 : voip : bad sound format
// A1023 : voip : bad wav header
// A1024 : ccxml : entry not found
// A1025 : ccxml : entry not ready
// A1026 : voip/proxy : voip configuration not found
// A1027 : ccxml : session not found (for call)
// A1028 : ccxml : No profile found for virtual agent session (dynamic callroom)
// A1029 : ccxml : No ccenter scenario found for a given profile
// E1001 : queues : user queue type not found
// E1002 : queues : user queue not found
// E1003 : queues : user queue task not found
// E1004 : ccxml : register expires
// W1001 : voip : rtp receive timeout
// W1002 : ccxml : disconnected call session timeout
// W1003 : ccxml : unplug mode
// W1004 : ccxml : end unplug mode

#endif
