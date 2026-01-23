#if !defined(_Windows) && !defined(MacOS)
//ident "@(#)ccenter/report/main.C (c) Copyright Consistent Software 2002-2005"
#endif

#include "report_minimal.h"
#include "explorer_client_minimal.h"
#include "forward_declarations.hpp"
#include <stdio.h>

// }{ -------------------------------------------------------------------------

const char* product_name = "ccenter_report";
const char* product_version = "1.0";

// }{ -------------------------------------------------------------------------

int main(int argc, char* argv[])
{
    printf("=== CCC Report System ===\n");
    printf("Product: %s\n", product_name);
    printf("Version: %s\n", product_version);
    printf("Mode: REPORT\n");
    
    // Créer une instance du système de reporting
    T_report_system* report_system = new T_report_system();
    
    if (report_system->initialize()) {
        printf("✅ Report system initialized successfully\n");
        
        // Créer une instance du client explorer
        T_explorer_client* explorer = new T_explorer_client();
        
        if (argc > 1) {
            printf("🔗 Connecting to: %s\n", argv[1]);
            explorer->connect(argv[1], 20103);
        } else {
            printf("📝 Usage: %s <host>\n", argv[0]);
            printf("   Example: %s 10.199.30.67\n", argv[0]);
        }
        
        delete explorer;
    } else {
        printf("❌ Failed to initialize report system\n");
    }
    
    delete report_system;
    
    printf("\n=== System Shutdown ===\n");
    return 0;
}