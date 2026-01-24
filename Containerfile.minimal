# Ultra-optimized Fedora Containerfile for minimal size
FROM fedora:39 AS runtime

LABEL maintainer="ccc_report_dashboard"
LABEL description="Ultra-optimized CCCP Dashboard Web Server"
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
RUN useradd -m -s /bin/sh -u 1000 cccp && \
    mkdir -p /app && \
    chown cccp:cccp /app

# Set working directory
WORKDIR /app

# Copy application files
COPY --chown=cccp:cccp ccenter_report web_server.py get_users_and_calls.py ./
COPY --chown=cccp:cccp templates/ ./templates/

# Create minimal config
RUN cat > config.py << 'EOF'
import os
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "vs-ics-prd-web-fr-505"),
    "user": os.getenv("MYSQL_USER", "interactiv"),
    "password": os.getenv("MYSQL_PASSWORD", "ics427!"),
    "database": os.getenv("MYSQL_DATABASE"),
    "charset": "utf8",
    "collation": "utf8_general_ci",
}
DEFAULT_SERVER_IP = os.getenv("DEFAULT_SERVER_IP", "10.199.30.67")
DEFAULT_SERVER_PORT = int(os.getenv("DEFAULT_SERVER_PORT", "20103"))
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
EOF

# Set permissions
RUN chmod +x /app/ccenter_report && \
    chown -R cccp:cccp /app

# Switch to non-root user
USER cccp

# Environment variables for optimization
ENV FLASK_HOST=0.0.0.0 \
    FLASK_PORT=5000 \
    FLASK_DEBUG=false \
    LOG_LEVEL=INFO \
    MYSQL_HOST=vs-ics-prd-web-fr-505 \
    MYSQL_USER=interactiv \
    MYSQL_PASSWORD=ics427! \
    DEFAULT_SERVER_IP=10.199.30.67 \
    DEFAULT_SERVER_PORT=20103 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONOPTIMIZE=1

EXPOSE 5000

# Lightweight health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/status', timeout=3)" || exit 1

CMD ["python3", "web_server.py"]