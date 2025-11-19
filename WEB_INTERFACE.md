# Web Interface for AI Agent Pipeline

## Overview

The AI Agent Pipeline now includes a **comprehensive web interface** that allows you to:

- 🔍 **Monitor agents in real-time** - See what each agent is doing
- 🚀 **Submit feature requests** - Queue work for the pipeline
- 💬 **Send prompts to specific agents** - Direct agent interaction
- ⚙️ **Edit configuration** - Change models, API keys, and settings
- 📊 **View live logs** - Real-time activity feed
- 📁 **Manage projects** - Switch between repositories

## Quick Start

### 1. Install Web Dependencies

```bash
pip install flask flask-socketio python-socketio
```

### 2. Start the Web Server

```bash
python web/app.py
```

### 3. Open in Browser

Navigate to: `http://localhost:5000`

## Features

### Real-Time Agent Monitoring

- **Live status updates** for all 5 agents (Architect, Coding, Testing, Deployment, Monitoring)
- **Iteration counters** - See how many iterations each agent has completed
- **Last activity timestamps** - Know when agents were last active
- **Status indicators** - Idle, Running, Completed, Error states with color coding

### Feature Request Management

- **Create feature requests** with title, description, and repository URL
- **Priority levels** - High, Medium, Low
- **Status tracking** - Pending, In Progress, Completed
- **Queue visualization** - See all pending work
- **One-click execution** - Run feature requests directly from the dashboard

### Agent Interaction

Send custom prompts to individual agents:
- **Architect** - Design questions, architecture reviews
- **Coding** - Implementation requests, bug fixes
- **Testing** - Test creation, QA tasks
- **Deployment** - Deployment configurations
- **Monitoring** - Health checks, log analysis

### Configuration Editor

Edit pipeline configuration through the web UI:
- **API Keys** - Update provider credentials (masked for security)
- **Model Selection** - Choose which model each agent uses
- **Provider Selection** - Switch between Anthropic, Gemini, Grok, Groq, OpenAI
- **Workspace Path** - Change working directory
- **Iteration Limits** - Adjust max iterations per agent
- **Advanced Settings** - Coverage thresholds, timeouts, etc.

### Live Logging

- **Real-time log stream** using WebSockets
- **Log levels** - Info, Warning, Error
- **Timestamps** - Precise activity timing
- **Filterable** - Search and filter logs
- **Auto-scroll** - Automatically follow latest logs
- **Export** - Download logs for analysis

## Web Interface Architecture

### Backend (Flask + SocketIO)

- **Flask** - Web framework for HTTP endpoints
- **Flask-SocketIO** - WebSocket support for real-time updates
- **Threading** - Background pipeline execution
- **JSON API** - RESTful endpoints for all operations

### Frontend (HTML + JavaScript)

- **Vanilla JavaScript** - No framework dependencies
- **WebSocket Client** - Real-time bi-directional communication
- **Responsive Design** - Works on desktop, tablet, mobile
- **Dark Theme** - Easy on the eyes for long sessions

### API Endpoints

#### Status & Monitoring
- `GET /api/status` - Get pipeline and agent status
- `GET /api/logs?limit=100` - Get recent logs
- `WS /` - WebSocket connection for real-time updates

#### Configuration
- `GET /api/config` - Get current configuration (API keys masked)
- `POST /api/config` - Update configuration

#### Pipeline Control
- `POST /api/pipeline/run` - Run full pipeline with requirements
- `POST /api/agent/prompt` - Send prompt to specific agent

#### Feature Requests
- `GET /api/feature-requests` - List all feature requests
- `POST /api/feature-requests` - Create new feature request
- `DELETE /api/feature-requests/<id>` - Delete feature request

### WebSocket Events

**Client → Server:**
- `connect` - Establish connection
- `disconnect` - Close connection

**Server → Client:**
- `status` - Full pipeline status (on connect)
- `log` - New log entry
- `agent_update` - Agent status changed
- `pipeline_status` - Pipeline status changed
- `feature_request_added` - New feature request
- `feature_request_deleted` - Feature request removed

## Usage Examples

### Example 1: Monitor Running Pipeline

1. Start web server: `python web/app.py`
2. Open browser to `http://localhost:5000`
3. Click "Run Pipeline" button
4. Enter requirements: "Build a REST API for task management"
5. Watch agents activate in real-time
6. View logs as they stream in
7. See iteration counts increase
8. Get notified when complete

### Example 2: Send Prompt to Coding Agent

1. Navigate to "Agents" tab
2. Select "Coding Agent"
3. Enter prompt: "Review the authentication code for security issues"
4. Click "Send Prompt"
5. Watch agent status change to "Running"
6. View real-time logs of the review
7. Agent completes and returns to "Idle"

### Example 3: Update Configuration

1. Navigate to "Configuration" tab
2. Update "Coding Agent" model from Claude to GPT-4:
   ```
   Before: anthropic:claude-sonnet-4-20250514
   After: openai:gpt-4-turbo-preview
   ```
3. Click "Save Configuration"
4. Configuration reloads automatically
5. Next run uses new model

### Example 4: Create Feature Request

1. Navigate to "Feature Requests" tab
2. Click "New Feature Request"
3. Fill in details:
   - Title: "Add user authentication"
   - Description: "Implement JWT-based auth with refresh tokens"
   - Repository: `https://github.com/user/my-app`
   - Priority: High
4. Click "Create"
5. Request appears in queue
6. Click "Run" to execute immediately
7. Track progress in real-time

## Security Considerations

### Production Deployment

**⚠️ IMPORTANT**: The default setup is for development only!

For production, you MUST:

1. **Change SECRET_KEY**:
   ```bash
   export SECRET_KEY="your-secure-random-key-here"
   ```

2. **Add Authentication**:
   - Implement user login
   - Use session management
   - Add role-based access control

3. **Use HTTPS**:
   - Deploy behind reverse proxy (Nginx, Apache)
   - Use SSL/TLS certificates
   - Enable HSTS headers

4. **Restrict Access**:
   - Firewall rules to limit IP access
   - VPN or SSH tunnel for remote access
   - Rate limiting on API endpoints

5. **Protect API Keys**:
   - Never expose real API keys in UI
   - Use environment variables
   - Implement proper key rotation

### Recommended Production Stack

```
Browser → HTTPS → Nginx (Reverse Proxy) → Gunicorn → Flask App → Docker Containers
                      ↓
                  SSL/TLS
                      ↓
              Authentication Layer
                      ↓
              API Key Vault
```

## Configuration

### Environment Variables

```bash
# Web Server
export WEB_HOST="0.0.0.0"           # Listen address
export WEB_PORT="5000"              # Port number
export SECRET_KEY="your-secret"     # Flask secret key

# Pipeline Configuration (optional, can use config.json instead)
export ANTHROPIC_API_KEY="..."
export GEMINI_API_KEY="..."
export GROQ_API_KEY="..."
export OPENAI_API_KEY="..."
```

### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "web/app.py"]
```

Build and run:
```bash
docker build -t ai-agent-web .
docker run -p 5000:5000 -v /var/run/docker.sock:/var/run/docker.sock ai-agent-web
```

### Docker Compose

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./workspace:/workspace
      - ./config.json:/app/config.json
    environment:
      - SECRET_KEY=your-secret-key
      - WEB_HOST=0.0.0.0
      - WEB_PORT=5000
```

Run with:
```bash
docker-compose up -d
```

## Advanced Features

### Custom Themes

Edit `web/static/css/style.css` to customize:
- Color scheme
- Layout
- Fonts
- Animations

### Webhook Integration

Add webhooks to notify external services:

```python
# In web/app.py
import requests

def notify_webhook(event, data):
    webhook_url = os.getenv('WEBHOOK_URL')
    if webhook_url:
        requests.post(webhook_url, json={"event": event, "data": data})

# Call in log_message:
notify_webhook('log', log_entry)
```

### Metrics Export

Export metrics to Prometheus:

```python
from prometheus_client import Counter, Gauge, generate_latest

pipeline_runs = Counter('pipeline_runs_total', 'Total pipeline runs')
active_agents = Gauge('active_agents', 'Number of active agents')

@app.route('/metrics')
def metrics():
    return generate_latest()
```

## Troubleshooting

### Web Server Won't Start

**Issue**: Port 5000 already in use

**Solution**:
```bash
export WEB_PORT=8080
python web/app.py
```

### WebSocket Connection Failed

**Issue**: CORS error in browser console

**Solution**: Check firewall rules, ensure WebSocket ports are open

### Agents Not Updating

**Issue**: Real-time updates not appearing

**Solution**:
- Check WebSocket connection in browser DevTools
- Verify Flask-SocketIO is installed
- Restart web server

### Configuration Not Saving

**Issue**: Changes don't persist

**Solution**:
- Check file permissions on `config.json`
- Ensure web server has write access
- Verify JSON format is valid

## Future Enhancements

Planned features for future releases:

- 📊 **Analytics Dashboard** - Charts and graphs of pipeline performance
- 🔔 **Notifications** - Email/Slack alerts for pipeline events
- 👥 **Multi-User Support** - Team collaboration features
- 📝 **Task Scheduling** - Cron-like scheduled pipelines
- 🔄 **Workflow Builder** - Visual pipeline designer
- 🗄️ **Database Backend** - Persistent storage for history
- 🔍 **Search** - Full-text search across logs and results
- 📦 **Plugin System** - Extend functionality with plugins

## Support

For issues or questions about the web interface:

1. Check the logs: `tail -f web/app.log`
2. Review this documentation
3. Check GitHub issues
4. Consult main documentation: [README.md](../README.md)

---

**🎉 Enjoy your new web interface!** Open a browser and start monitoring your AI agents in real-time.
