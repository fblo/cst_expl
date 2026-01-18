# Deployment Guide - CCCP Explorer

## Overview

This guide covers deploying CCCP Explorer in various environments including local development, staging, and production.

## Deployment Options

### Option 1: Standalone Server

Best for: Development, testing, small deployments

```bash
# Run directly
python3 /home/fblo/Documents/repos/explo-cst/web_server.py

# Run in background
nohup python3 /home/fblo/Documents/repos/explo-cst/web_server.py > /var/log/cccp-explorer.log 2>&1 &
```

### Option 2: Systemd Service

Best for: Production Linux servers

Create `/etc/systemd/system/cccp-explorer.service`:

```ini
[Unit]
Description=CCCP Explorer Dashboard
After=network.target

[Service]
Type=simple
User=cccp
Group=cccp
WorkingDirectory=/home/fblo/Documents/repos/explo-cst
ExecStart=/usr/bin/python3 /home/fblo/Documents/repos/explo-cst/web_server.py
Restart=always
Environment=CCCP_HOST=10.199.30.67
Environment=FLASK_HOST=0.0.0.0
Environment=FLASK_PORT=5000

[Install]
WantedBy=multi-user.target
```

Install and start:

```bash
# Copy service file
sudo cp cccp-explorer.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable cccp-explorer

# Start service
sudo systemctl start cccp-explorer

# Check status
sudo systemctl status cccp-explorer
```

### Option 3: Docker Container

Best for: Isolated deployments, cloud environments

Create `Dockerfile`:

```dockerfile
FROM python:3.14-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Run application
CMD ["python3", "web_server.py"]
```

Build and run:

```bash
# Build image
docker build -t cccp-explorer:latest .

# Run container
docker run -d \
  --name cccp-explorer \
  -p 5000:5000 \
  -e CCCP_HOST=10.199.30.67 \
  cccp-explorer:latest

# View logs
docker logs -f cccp-explorer
```

### Option 4: Reverse Proxy (Nginx)

Best for: Production with SSL, load balancing

Create nginx config `/etc/nginx/conf.d/cccp-explorer.conf`:

```nginx
server {
    listen 80;
    server_name cccp.example.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable SSL with Let's Encrypt:

```bash
# Install certbot
sudo dnf install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d cccp.example.com
```

## Environment Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CCCP_HOST` | 10.199.30.67 | CCCP server hostname |
| `CCCP_PROXY_PORT` | 20101 | CCCP proxy port |
| `CCCP_DISPATCH_PORT` | 20103 | CCCP dispatch port |
| `FLASK_HOST` | 0.0.0.0 | Web server bind address |
| `FLASK_PORT` | 5000 | Web server port |
| `FLASK_DEBUG` | False | Enable debug mode |

### Example Environment File

Create `.env` in project root:

```
CCCP_HOST=10.199.30.67
CCCP_PROXY_PORT=20101
CCCP_DISPATCH_PORT=20103
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False
CCCP_USERNAME=supervisor_fdai
CCCP_PASSWORD=toto
```

## Security Hardening

### 1. Firewall Configuration

```bash
# Allow only web port
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload

# Deny other ports
sudo firewall-cmd --set-default-zone=drop
```

### 2. Non-Root User

```bash
# Create service user
sudo useradd -r -s /sbin/nologin cccp

# Set permissions
sudo chown -R cccp:cccp /home/fblo/Documents/repos/explo-cst
sudo chmod 750 /home/fblo/Documents/repos/explo-cst
```

### 3. SSL/TLS

Use reverse proxy with SSL (see Option 4 above).

### 4. Secrets Management

Never commit credentials. Use:

```bash
# Environment variables (recommended)
export CCCP_PASSWORD="your-secure-password"

# Or systemd drop-in
sudo mkdir -p /etc/systemd/system/cccp-explorer.service.d
sudo tee /etc/systemd/system/cccp-explorer.service.d/environment.conf <<EOF
[Service]
Environment="CCCP_PASSWORD=your-secure-password"
EOF
```

## Monitoring

### Health Check Endpoint

```bash
# Check if service is healthy
curl http://localhost:5000/api/status | jq '.connected'
```

### Log Monitoring

```bash
# View systemd logs
sudo journalctl -u cccp-explorer -f

# View application logs
tail -f /var/log/cccp-explorer.log
```

### Prometheus Metrics (Optional)

Add metrics endpoint to `web_server.py`:

```python
@app.route("/metrics")
def metrics():
    return jsonify({
        "connected_clients": len(state.clients),
        "events_count": len(state.all_events),
        "users_count": len(state.users),
    })
```

## Backup and Recovery

### Configuration Backup

```bash
# Backup configuration
tar -czf /backup/cccp-explorer-config-$(date +%Y%m%d).tar.gz \
  /home/fblo/Documents/repos/explo-cst/.env \
  /etc/systemd/system/cccp-explorer.service \
  /etc/nginx/conf.d/cccp-explorer.conf
```

### Recovery Procedure

```bash
# Restore from backup
tar -xzf /backup/cccp-explorer-config-20240118.tar.gz -C /

# Restart services
sudo systemctl restart cccp-explorer
sudo systemctl restart nginx
```

## Performance Tuning

### Gunicorn (Production)

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_server:app
```

### File Descriptors

```bash
# Increase limit
sudo tee /etc/security/limits.d/cccp.conf <<EOF
cccp soft nofile 65536
cccp hard nofile 65536
EOF
```

## Troubleshooting Deployment

### Service Won't Start

```bash
# Check logs
sudo journalctl -u cccp-explorer -xe

# Check port
sudo netstat -tlnp | grep 5000
```

### Connection Failures

```bash
# Test CCCP connectivity
nc -zv 10.199.30.67 20101
nc -zv 10.199.30.67 20103
```

### Memory Issues

```bash
# Check memory usage
ps aux | grep web_server
free -h
```

## Scaling Considerations

### Horizontal Scaling

CCCP Explorer is stateless at the application level. For horizontal scaling:

1. Use load balancer with sticky sessions
2. Each instance connects independently to CCCP
3. Shared storage for logs if needed

### High Availability

1. Multiple instances behind load balancer
2. CCCP server redundancy (outside scope)
3. Health checks on each instance
