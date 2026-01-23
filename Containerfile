# Containerfile pour binaires récents avec glibc 2.38+
FROM fedora:39

# Métadonnées
LABEL maintainer="ccc_report_build"
LABEL description="Container for modern ccc_report binaries with glibc 2.38+"
LABEL version="1.0"

# Variables d'environnement
ENV CC=gcc
ENV CXX=g++
ENV CFLAGS="-O2 -g -D_UNIX_ -DCCENTER_REPORT"
ENV CXXFLAGS="-O2 -g -std=c++03 -D_UNIX_ -DCCENTER_REPORT"
ENV LDFLAGS="-lcrypt"
ENV MAKEFLAGS="-j$(nproc)"

# Installation des paquets
RUN dnf update -y && \
    dnf groupinstall -y "Development Tools" && \
    dnf install -y \
        gcc \
        gcc-c++ \
        make \
        cmake \
        libxcrypt \
        libxcrypt-devel \
        libxml2-devel \
        libxslt-devel \
        zlib-devel \
        openssl-devel \
        which \
        wget \
        curl \
        git && \
    dnf clean all

# Créer le lien symbolique pour libcrypt.so.2
RUN ln -sf /lib64/libcrypt.so.1 /lib64/libcrypt.so.2 && \
    ldconfig

# Création des répertoires de travail
RUN mkdir -p /opt/ccenter_report && \
    mkdir -p /opt/ccenter_report/build && \
    mkdir -p /opt/ccenter_report/output

# Copier tous les fichiers sources
COPY . /opt/ccenter_report/

# Définir le répertoire de travail
WORKDIR /opt/ccenter_report

# Permissions (seulement si les scripts existent)
RUN chmod +x /opt/ccenter_report/build.sh 2>/dev/null || true && \
    chmod +x /opt/ccenter_report/create-stubs.sh 2>/dev/null || true && \
    chmod +x /opt/ccenter_report/full-build.sh 2>/dev/null || true

# Créer les stubs seulement si le script existe
RUN test -x /opt/ccenter_report/create-stubs.sh && /opt/ccenter_report/create-stubs.sh || true

# Permettre d'exécuter directement le binaire  
CMD ["./full-build.sh"]