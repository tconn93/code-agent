# Security Hardening & Deployment Guide

This guide provides step-by-step instructions for deploying the AI Agent Platform securely in production.

---

## 🔴 **CRITICAL: Complete Before Production**

These steps are **mandatory** before deploying to production. Skipping them creates serious security vulnerabilities.

### 1. Generate and Set SECRET_KEY

The SECRET_KEY is used for JWT token signing and MUST be secure.

**❌ NEVER use the default value in production**

```bash
# Generate a secure secret key
python3 -c 'import secrets; print(secrets.token_urlsafe(32))'

# Output example (yours will be different):
# r5K9fJ2pL8mN4vQ7wX3yZ1aB6cD0eF-gH8iJ

# Add to your .env file
echo "SECRET_KEY=YOUR_GENERATED_KEY_HERE" >> .env
```

**Location**: Add `SECRET_KEY` to `.env` file in project root

**Verification**:
```bash
# The API will fail to start if SECRET_KEY is not set or is insecure
python services/api/main.py
# Should start successfully with: "✓ SECRET_KEY loaded from environment"
```

---

### 2. Set Up CORS Origins

Configure allowed origins for cross-origin requests.

```bash
# Add to .env
CORS_ORIGINS=https://your-frontend-domain.com,https://app.yourcompany.com

# Development (localhost)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Security Note**: Never use `*` (wildcard) in production!

---

### 3. Install Required Dependencies

```bash
# Install security-related packages
pip install passlib[bcrypt] python-jose[cryptography] python-multipart

# Or from requirements.txt
pip install -r requirements.txt
```

---

### 4. Run Database Migrations

Apply all database schema changes including authentication and cost tracking.

```bash
# Initialize Alembic (if not already done)
alembic init migrations

# Run migrations
alembic upgrade head

# Verify tables were created
psql -d agent_platform -c "\dt"
# Should show: users, api_keys, jobs (with new columns), etc.
```

---

### 5. Create Admin User

**IMPORTANT**: Create the first admin user manually.

```bash
# Option 1: Using Python
python3 << EOF
from services.api.auth import get_password_hash
from services.api.database import SessionLocal
from services.api.models import User

db = SessionLocal()
admin = User(
    email="admin@yourcompany.com",
    name="Admin User",
    password_hash=get_password_hash("CHANGE_THIS_SECURE_PASSWORD"),
    role="admin",
    is_active=True
)
db.add(admin)
db.commit()
print("Admin user created!")
db.close()
EOF

# Option 2: Using curl after API is running
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yourcompany.com",
    "name": "Admin User",
    "password": "SecureAdminPass123!"
  }'

# Then manually upgrade to admin in database
psql -d agent_platform -c "UPDATE users SET role='admin' WHERE email='admin@yourcompany.com';"
```

---

## 🔒 **Security Hardening Checklist**

### Environment Variables

Add these to your `.env` file:

```bash
# Required
SECRET_KEY=<your-64-char-secret-key>
DATABASE_URL=postgresql://user:password@localhost:5432/agent_platform
REDIS_URL=redis://localhost:6379/0

# AI Provider Keys (at least one required)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
GROQ_API_KEY=gsk_...
XAI_API_KEY=...

# CORS Configuration
CORS_ORIGINS=https://your-frontend.com

# Optional Security Features
ENABLE_HSTS=true  # Only if using HTTPS
```

---

### Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP (redirect to HTTPS)
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable

# Block direct access to internal services
sudo ufw deny 5432/tcp  # PostgreSQL (should only be localhost)
sudo ufw deny 6379/tcp  # Redis (should only be localhost)
sudo ufw deny 8000/tcp  # API (use reverse proxy)
```

---

### SSL/TLS Certificate (HTTPS)

**Production MUST use HTTPS**. Use Let's Encrypt for free certificates.

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d api.yourcompany.com

# Auto-renewal (certbot sets this up automatically)
sudo certbot renew --dry-run
```

Update `.env`:
```bash
ENABLE_HSTS=true
```

---

### Reverse Proxy (Nginx)

Never expose the FastAPI server directly. Use Nginx as a reverse proxy.

**File**: `/etc/nginx/sites-available/agent-platform`

```nginx
server {
    listen 80;
    server_name api.yourcompany.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourcompany.com;

    # SSL Configuration (certbot fills this in)
    ssl_certificate /etc/letsencrypt/live/api.yourcompany.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourcompany.com/privkey.pem;

    # Security headers (additional to application headers)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;

    # Proxy to FastAPI
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (for future real-time updates)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Increase upload size for large files
    client_max_body_size 100M;
}
```

Enable and test:
```bash
sudo ln -s /etc/nginx/sites-available/agent-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

### Database Security

#### PostgreSQL Hardening

**File**: `/etc/postgresql/15/main/pg_hba.conf`

```conf
# Only allow localhost connections
local   all             all                                     peer
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             ::1/128                 scram-sha-256

# Deny all other connections
host    all             all             0.0.0.0/0               reject
```

#### Create Database User with Limited Permissions

```bash
# Connect as postgres superuser
sudo -u postgres psql

# Create dedicated user
CREATE USER agent_user WITH PASSWORD 'STRONG_PASSWORD_HERE';

# Create database
CREATE DATABASE agent_platform OWNER agent_user;

# Grant only necessary permissions
GRANT CONNECT ON DATABASE agent_platform TO agent_user;
\c agent_platform
GRANT USAGE ON SCHEMA public TO agent_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO agent_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO agent_user;

# Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO agent_user;
```

Update `DATABASE_URL` in `.env`:
```bash
DATABASE_URL=postgresql://agent_user:STRONG_PASSWORD_HERE@localhost:5432/agent_platform
```

#### Enable Database Backups

```bash
# Create backup script
cat > /usr/local/bin/backup-agent-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/agent-platform"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

pg_dump agent_platform | gzip > $BACKUP_DIR/agent_platform_$DATE.sql.gz

# Keep only last 30 days of backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
EOF

chmod +x /usr/local/bin/backup-agent-db.sh

# Schedule daily backups (cron)
sudo crontab -e
# Add this line:
0 2 * * * /usr/local/bin/backup-agent-db.sh
```

---

### Redis Security

**File**: `/etc/redis/redis.conf`

```conf
# Bind only to localhost
bind 127.0.0.1 ::1

# Require password
requirepass YOUR_STRONG_REDIS_PASSWORD

# Disable dangerous commands
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""

# Enable AOF persistence (durability)
appendonly yes
appendfilename "appendonly.aof"
```

Update `.env`:
```bash
REDIS_URL=redis://:YOUR_STRONG_REDIS_PASSWORD@localhost:6379/0
```

Restart Redis:
```bash
sudo systemctl restart redis
```

---

### Docker Container Security

The code already includes security hardening, but verify these settings:

**File**: `agents/base_agent.py` (already implemented)

```python
# ✓ Memory limit: 2GB
mem_limit='2g'

# ✓ CPU limit: 100% of one core
cpu_quota=100000

# ✓ Drop all capabilities
cap_drop=['ALL']
cap_add=['CHOWN', 'DAC_OVERRIDE', 'FOWNER', 'SETGID', 'SETUID']

# ✓ No new privileges
security_opt=['no-new-privileges:true']
```

**Additional Docker Daemon Security** (`/etc/docker/daemon.json`):

```json
{
  "userns-remap": "default",
  "no-new-privileges": true,
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

Restart Docker:
```bash
sudo systemctl restart docker
```

---

## 📊 **Monitoring & Logging**

### Application Logging

Logs are automatically written to stdout. Capture them with systemd:

```bash
# View API logs
sudo journalctl -u agent-platform-api -f

# View worker logs
sudo journalctl -u agent-platform-worker -f
```

### Log Rotation

**File**: `/etc/logrotate.d/agent-platform`

```conf
/var/log/agent-platform/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
}
```

---

## 🚀 **Production Deployment**

### Systemd Service Files

#### API Service

**File**: `/etc/systemd/system/agent-platform-api.service`

```ini
[Unit]
Description=AI Agent Platform API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/agent-platform
Environment="PATH=/opt/agent-platform/venv/bin"
EnvironmentFile=/opt/agent-platform/.env
ExecStart=/opt/agent-platform/venv/bin/uvicorn services.api.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Worker Service

**File**: `/etc/systemd/system/agent-platform-worker@.service`

```ini
[Unit]
Description=AI Agent Platform Worker %i
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/agent-platform
Environment="PATH=/opt/agent-platform/venv/bin"
EnvironmentFile=/opt/agent-platform/.env
Environment="AGENT_ID=%i"
ExecStart=/opt/agent-platform/venv/bin/python services/worker/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Enable and Start Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable agent-platform-api
sudo systemctl enable agent-platform-worker@{1..4}  # Start 4 workers

# Start services
sudo systemctl start agent-platform-api
sudo systemctl start agent-platform-worker@{1..4}

# Check status
sudo systemctl status agent-platform-api
sudo systemctl status agent-platform-worker@*
```

---

## ✅ **Post-Deployment Checklist**

### Security Verification

```bash
# 1. Verify SECRET_KEY is set
curl https://api.yourcompany.com/
# Should NOT expose any error about SECRET_KEY

# 2. Verify authentication is required
curl https://api.yourcompany.com/projects/
# Should return 401 Unauthorized

# 3. Verify HTTPS is working
curl -I https://api.yourcompany.com/
# Should return 200 OK with security headers

# 4. Verify rate limiting
for i in {1..10}; do curl https://api.yourcompany.com/auth/login; done
# Should return 429 Too Many Requests after 5 requests

# 5. Test authentication flow
curl -X POST https://api.yourcompany.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@yourcompany.com","password":"YOUR_PASSWORD"}'
# Should return token

# 6. Verify Docker security
docker inspect <container_id> | grep -A 10 "CapDrop"
# Should show capability restrictions

# 7. Check database permissions
sudo -u postgres psql -d agent_platform -c "\dp"
# agent_user should have limited permissions

# 8. Verify CORS
curl -H "Origin: https://unauthorized.com" https://api.yourcompany.com/
# Should be blocked or not set CORS headers
```

---

## 🔄 **Maintenance**

### Regular Tasks

```bash
# Weekly: Update dependencies
pip install --upgrade -r requirements.txt

# Monthly: Review audit logs
psql -d agent_platform -c "SELECT * FROM audit_logs WHERE created_at > NOW() - INTERVAL '30 days';"

# Monthly: Review cost reports
curl -H "Authorization: Bearer YOUR_ADMIN_TOKEN" https://api.yourcompany.com/costs/report

# Quarterly: Security audit
# - Review user permissions
# - Check for unused API keys
# - Verify firewall rules
# - Update SSL certificates (auto-renewed by certbot)
```

---

## 🆘 **Troubleshooting**

### Issue: "SECRET_KEY environment variable is not set"

**Solution**:
```bash
# Verify .env file exists and has SECRET_KEY
cat .env | grep SECRET_KEY

# If missing, generate and add it
python3 -c 'import secrets; print("SECRET_KEY=" + secrets.token_urlsafe(32))' >> .env
```

### Issue: "Could not validate credentials" (401 error)

**Causes**:
- Token expired (24 hours)
- SECRET_KEY changed (invalidates all tokens)
- User account deactivated

**Solution**:
- Login again to get new token
- Check user is active: `SELECT * FROM users WHERE email='user@example.com';`

### Issue: Rate limit errors (429)

**Solution**:
- Normal behavior for security
- Wait 60 seconds and try again
- For legitimate high traffic, adjust rate limits in `services/api/security.py`

### Issue: Budget exceeded - jobs blocked

**Solution**:
- Check budget status: `curl -H "Authorization: Bearer TOKEN" https://api.yourcompany.com/costs/projects/{id}/budget`
- Increase budget in database: `UPDATE projects SET budget_allocated = 500.00 WHERE id = 1;`
- Or disable budget check by setting `budget_allocated = NULL`

---

## 📚 **Additional Resources**

- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

---

## 🎯 **Quick Start for Development**

If you just want to test locally (NOT for production):

```bash
# 1. Generate SECRET_KEY
export SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')

# 2. Start services
docker-compose up -d

# 3. Run migrations
alembic upgrade head

# 4. Start API
uvicorn services.api.main:app --reload

# 5. Create test user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test User","password":"TestPass123"}'
```

---

**Remember**: This guide covers security basics. For enterprise deployments, consider:
- Penetration testing
- Security audits
- DDoS protection (Cloudflare, AWS Shield)
- Secrets management (HashiCorp Vault, AWS Secrets Manager)
- Container orchestration (Kubernetes)
- Multi-region deployment
