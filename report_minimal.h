#if !defined(_Windows) && !defined(MacOS)
//ident "@(#)ccenter/report/report.h (c) Copyright Consistent Software 2002-2005"
#endif

// }{ -------------------------------------------------------------------------

#ifndef CCENTER_REPORT_REPORT_H__
#define CCENTER_REPORT_REPORT_H__

class T_report_system {
public:
    T_report_system();
    virtual ~T_report_system();
    
    // Méthodes de base pour le reporting
    virtual bool initialize();
    virtual void shutdown();
};

#endif