#!/bin/bash
# Script de génération des stubs pour le build cccenter_report

set -e

echo "🔧 Génération des stubs pour cccenter_report..."

# Créer la structure des dépendances
DEPS_DIR="dependencies"
mkdir -p "$DEPS_DIR"/{ccenter/{public,common},wo/wow,system/{public,idl}}

# Générer wow_object.h (fichier de base)
cat > "$DEPS_DIR/wo/wow/wow_object.h" << 'EOF'
#ifndef WOW_OBJECT_H__
#define WOW_OBJECT_H__

#include <stdint.h>

typedef uint32_t wow_uint_32;
typedef uint16_t wow_uint_16;
typedef uint8_t wow_uint_8;

class T_wow_object {
public:
    virtual ~T_wow_object() {}
    
    static void * operator new(size_t size) {
        return ::operator new(size);
    }
    
    static void operator delete(void * ptr) {
        ::operator delete(ptr);
    }
};

#define overload_link(class_name) \
    public: static const char * get_class_name() { return #class_name; }

#define read_only_field(type, name) \
    private: type _##name; \
    public: type get_##name() const { return _##name; }

#define read_only_string_field(name) \
    read_only_field(const char *, name)

#define read_only_list_field(type, name) \
    private: type * _##name; \
    public: type * get_##name() const { return _##name; }

#define read_only_boolean_field(name) \
    read_only_field(bool, name)

#define read_only_class_field(type, name) \
    read_only_field(type, name)

#define private_field(type, name) \
    private: type _##name;

#endif
EOF

# Générer wow_system.h
cat > "$DEPS_DIR/wo/wow/wow_system.h" << 'EOF'
#ifndef WOW_SYSTEM_H__
#define WOW_SYSTEM_H__

#include "wow_object.h"

class T_wow_system : public T_wow_object {
public:
    T_wow_system() {}
    virtual ~T_wow_system() {}
    
    overload_link(T_wow_system)
};

#endif
EOF

# Générer wow_socket.h
cat > "$DEPS_DIR/wo/wow/wow_socket.h" << 'EOF'
#ifndef WOW_SOCKET_H__
#define WOW_SOCKET_H__

#include "wow_object.h"

class T_wow_server_address : public T_wow_object {
    read_only_field(const char*, host)
    read_only_field(wow_uint_16, port)
    
public:
    T_wow_server_address(const char* h, wow_uint_16 p) {
        _host = strdup(h);
        _port = p;
    }
    
    virtual ~T_wow_server_address() {
        if (_host) free((void*)_host);
    }
    
    overload_link(T_wow_server_address)
    
private:
    char* _host;
    wow_uint_16 _port;
};

#endif
EOF

# Générer wow_xml.h
cat > "$DEPS_DIR/wo/wow/wow_xml.h" << 'EOF'
#ifndef WOW_XML_H__
#define WOW_XML_H__

#include "wow_object.h"

class T_wow_xml_object : public T_wow_object {
public:
    T_wow_xml_object() {}
    virtual ~T_wow_xml_object() {}
    
    overload_link(T_wow_xml_object)
};

#endif
EOF

# Générer wow_file.h
cat > "$DEPS_DIR/wo/wow/wow_file.h" << 'EOF'
#ifndef WOW_FILE_H__
#define WOW_FILE_H__

#include "wow_object.h"

class T_wow_file : public T_wow_object {
public:
    T_wow_file() {}
    virtual ~T_wow_file() {}
    
    overload_link(T_wow_file)
};

#endif
EOF

# Générer wow_outgoing_message.h
cat > "$DEPS_DIR/wo/wow/wow_outgoing_message.h" << 'EOF'
#ifndef WOW_OUTGOING_MESSAGE_H__
#define WOW_OUTGOING_MESSAGE_H__

#include "wow_object.h"

class T_wow_outgoing_message : public T_wow_object {
public:
    T_wow_outgoing_message() {}
    virtual ~T_wow_outgoing_message() {}
    
    overload_link(T_wow_outgoing_message)
};

#endif
EOF

# Générer wow_incoming_message.h
cat > "$DEPS_DIR/wo/wow/wow_incoming_message.h" << 'EOF'
#ifndef WOW_INCOMING_MESSAGE_H__
#define WOW_INCOMING_MESSAGE_H__

#include "wow_object.h"

class T_wow_incoming_message : public T_wow_object {
public:
    T_wow_incoming_message() {}
    virtual ~T_wow_incoming_message() {}
    
    overload_link(T_wow_incoming_message)
};

#endif
EOF

# Générer wow.h
cat > "$DEPS_DIR/wo/wow/wow.h" << 'EOF'
#ifndef WOW_H__
#define WOW_H__

#include "wow_object.h"
#include "wow_system.h"
#include "wow_socket.h"
#include "wow_xml.h"
#include "wow_file.h"
#include "wow_outgoing_message.h"
#include "wow_incoming_message.h"

#endif
EOF

# Générer les classes IDL de base
cat > "$DEPS_DIR/system/idl/system_idl.h" << 'EOF'
#ifndef SYSTEM_IDL_H__
#define SYSTEM_IDL_H__

#include "../wo/wow.h"

class T_system_idl : public T_wow_object {
public:
    T_system_idl() {}
    virtual ~T_system_idl() {}
    
    overload_link(T_system_idl)
};

#endif
EOF

# Générer consistent_system.h
cat > "$DEPS_DIR/system/idl/consistent_system.h" << 'EOF'
#ifndef CONSISTENT_SYSTEM_H__
#define CONSISTENT_SYSTEM_H__

#include "../wo/wow.h"

class T_consistent_system : public T_wow_object {
public:
    T_consistent_system() {}
    virtual ~T_consistent_system() {}
    
    overload_link(T_consistent_system)
};

#endif
EOF

# Générer consistent_client.h
cat > "$DEPS_DIR/system/idl/consistent_client.h" << 'EOF'
#ifndef CONSISTENT_CLIENT_H__
#define CONSISTENT_CLIENT_H__

#include "../wo/wow.h"

class T_consistent_client : public T_wow_object {
public:
    T_consistent_client() {}
    virtual ~T_consistent_client() {}
    
    overload_link(T_consistent_client)
};

#endif
EOF

# Générer explorer_classes.h
cat > "$DEPS_DIR/system/idl/explorer_classes.h" << 'EOF'
#ifndef EXPLORER_CLASSES_H__
#define EXPLORER_CLASSES_H__

#include "../wo/wow.h"

class T_explorer_classes : public T_wow_object {
public:
    T_explorer_classes() {}
    virtual ~T_explorer_classes() {}
    
    overload_link(T_explorer_classes)
};

#endif
EOF

# Générer protocol_classes.h
cat > "$DEPS_DIR/system/idl/protocol_classes.h" << 'EOF'
#ifndef PROTOCOL_CLASSES_H__
#define PROTOCOL_CLASSES_H__

#include "../wo/wow.h"

class T_protocol_classes : public T_wow_object {
public:
    T_protocol_classes() {}
    virtual ~T_protocol_classes() {}
    
    overload_link(T_protocol_classes)
};

#endif
EOF

# Générer ecma_lib.h
cat > "$DEPS_DIR/system/idl/ecma_lib.h" << 'EOF'
#ifndef ECMA_LIB_H__
#define ECMA_LIB_H__

#include "../wo/wow.h"

class T_ecma_lib : public T_wow_object {
public:
    T_ecma_lib() {}
    virtual ~T_ecma_lib() {}
    
    overload_link(T_ecma_lib)
};

#endif
EOF

# Générer ecma_script.h
cat > "$DEPS_DIR/system/idl/ecma_script.h" << 'EOF'
#ifndef ECMA_SCRIPT_H__
#define ECMA_SCRIPT_H__

#include "../wo/wow.h"

class T_ecma_script : public T_wow_object {
public:
    T_ecma_script() {}
    virtual ~T_ecma_script() {}
    
    overload_link(T_ecma_script)
};

#endif
EOF

# Générer ecma_regexp.h
cat > "$DEPS_DIR/system/idl/ecma_regexp.h" << 'EOF'
#ifndef ECMA_REGEXP_H__
#define ECMA_REGEXP_H__

#include "../wo/wow.h"

class T_ecma_regexp : public T_wow_object {
public:
    T_ecma_regexp() {}
    virtual ~T_ecma_regexp() {}
    
    overload_link(T_ecma_regexp)
};

#endif
EOF

# Générer consistent_variable.h
cat > "$DEPS_DIR/system/idl/consistent_variable.h" << 'EOF'
#ifndef CONSISTENT_VARIABLE_H__
#define CONSISTENT_VARIABLE_H__

#include "../wo/wow.h"

class T_consistent_variable : public T_wow_object {
public:
    T_consistent_variable() {}
    virtual ~T_consistent_variable() {}
    
    overload_link(T_consistent_variable)
};

#endif
EOF

# Générer ccenter_idl.h
cat > "$DEPS_DIR/system/idl/ccenter_idl.h" << 'EOF'
#ifndef CCENTER_IDL_H__
#define CCENTER_IDL_H__

#include "../wo/wow.h"

class T_ccenter_idl : public T_wow_object {
public:
    T_ccenter_idl() {}
    virtual ~T_ccenter_idl() {}
    
    overload_link(T_ccenter_idl)
};

#endif
EOF

echo "✅ Stubs générés avec succès dans $DEPS_DIR/"
echo "📁 Structure créée :"
find $DEPS_DIR -name "*.h" | sort