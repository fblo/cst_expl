# Ultra-optimized Fedora Containerfile for minimal size
FROM fedora:39 AS runtime

LABEL maintainer="ccc_report_dashboard"
LABEL description="CCCP Dashboard Web Server"
LABEL version="1.0"

# Install minimal dependencies with aggressive cleanup
RUN dnf -y install --setopt=install_weak_deps=False --nodocs \
        python3 \
        python3-pip \
        libxcrypt \
        mariadb-connector-c \
        libstdc++ \
        libgcc \
        glibc \
        cryptopp \
        sshpass \
        openssh-clients \
        && \
    dnf -y clean all && \
    rm -rf /var/cache/yum/* \
              /var/lib/dnf/history* \
              /var/log/dnf.* \
              /var/log/yum.* \
              /usr/share/doc/* \
              /usr/share/man/* \
              /usr/share/info/* \
              /var/cache/man/* \
              /tmp/* \
              /var/tmp/* && \
    find /var/log -type f -delete 2>/dev/null || true

# Create compatibility symlink
RUN ln -sf /lib64/libcrypt.so.1 /lib64/libcrypt.so.2 && \
    ldconfig -N

# Install Python requirements with minimal cache
RUN pip3 install --no-cache-dir --root-user-action=ignore \
        "flask>=2.0.0" \
        "flask-cors>=3.0.0" \
        "mysql-connector-python>=8.0.0" && \
    find /usr/local -name "*.pyc" -delete && \
    find /usr/local -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Create app user and directory structure
RUN mkdir -p /app && \
    mkdir /app/import_logs && \
    mkdir -p /opt/debug/NFS 

# Declare volume for NFS mount
VOLUME ["/opt/debug/NFS"]
    

# Set working directory
WORKDIR /app

# Copy application files
RUN mkdir ccc_bin
COPY web_server.py get_users_and_calls.py config.py debug_interface.xml dispatch.py snapshots.py paths.py mysql_queries.py jobs.py ./
COPY ccc_bin/ccenter_dispatch ccc_bin/ccenter_ccxml ccc_bin/ccenter_update ccc_bin/ccenter_report ./ccc_bin

COPY templates/ ./templates/
COPY routes/ ./routes/

# Set permissions
RUN chmod +x /app/ccc_bin/ccenter_report && \
    chmod +x /app/ccc_bin/ccenter_dispatch && \
    chmod +x /app/ccc_bin/ccenter_ccxml && \
    chmod +x /app/ccc_bin/ccenter_update


# Environment variables for optimization
ENV FLASK_HOST=0.0.0.0 \
    FLASK_PORT=5000 \
    FLASK_DEBUG=false \
    LOG_LEVEL=INFO \
    MYSQL_HOST=vs-ics-prd-web-fr-505 \
    MYSQL_USER=interactiv \
    MYSQL_PASSWORD=ics427! \
    DEFAULT_SERVER_PORT=20103 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONOPTIMIZE=1

EXPOSE 5000
EXPOSE 35000-35020

CMD ["python3", "web_server.py"]
