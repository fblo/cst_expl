#if !defined(_Windows) && !defined(MacOS)
//ident "@(#)cccenter/report/explorer_client.h (c) Copyright Consistent Software 2002-2005"
#endif

// }{ -------------------------------------------------------------------------

#ifndef CCENTER_REPORT_EXPLORER_CLIENT_H__
#define CCENTER_REPORT_EXPLORER_CLIENT_H__

class T_explorer_client {
public:
    T_explorer_client();
    virtual ~T_explorer_client();
    
    // Méthodes de connexion réseau basique
    virtual bool connect(const char* host, int port);
    virtual void disconnect();
};

#endif