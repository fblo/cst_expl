#if !defined(_Windows) && !defined(MacOS)
//ident "@(#)ccenter/report/main.C (c) Copyright Consistent Software 2002-2005"
#endif

#include "define.h"
#include "idl.h"
#include "ccenter_version.h"

const wow_uint_32 product_version = CCENTER_VERSION;
const char * product_edition = CCENTER_EDITION;

// }{ -------------------------------------------------------------------------

int main(int argc, char * argv[]) {
//wow_alloc_assert = TRUE;
#ifdef WOW_TRACES
	wow_traces = stderr;
	wow_debug_level = 3;
#else
	wow_debug_level = 0;
#endif
#ifdef WOW_DEBUG
	wow_init_new();
#endif
	{
		T_report_system system;
		system.use_arguments(argc, argv);

		if (!system.verify_arguments()) {
			system.usage(stderr, argv[0]);
			return 2;
		}

		system.init();
#ifdef WOW_TRACES
		wow_log("%s Version %ld.%ld.%ld%s\n", argv[0], product_version >> 24, (product_version >> 16) & 0xff, (product_version >> 8) & 0xff, get_version_name(product_version & 0xff));
#endif

		if (system.get_explorer_client() != NULL) {
			if (!system.connect_to_servers()) return 4;

			system.run();

			if ((system.get_explorer_client() != NULL) && !system.get_explorer_client()->is_connected_once()) {
				wow_log("Can't connect to server ( %s:%d )\n", system.get_explorer_client()->get_server_address(), system.get_explorer_client()->get_server_port());
				return 5;
			}
		}
	}
#ifdef WOW_DEBUG
	wow_log("Exit OK\n");
	wow_display_stat_new();
#endif
	return 0;
}

// }{ -------------------------------------------------------------------------
