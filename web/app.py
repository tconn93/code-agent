"""
Web interface for AI Agent Pipeline.

Provides real-time monitoring, agent control, configuration management,
and feature request handling through a browser-based interface.
"""
import os
import sys
import json
import threading
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Settings, load_config
from pipelines import PipelineOrchestrator

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
pipeline_state = {
    "status": "idle",
    "current_stage": None,
    "agents": {
        "architect": {"status": "idle", "last_activity": None, "iterations": 0},
        "coding": {"status": "idle", "last_activity": None, "iterations": 0},
        "testing": {"status": "idle", "last_activity": None, "iterations": 0},
        "deployment": {"status": "idle", "last_activity": None, "iterations": 0},
        "monitoring": {"status": "idle", "last_activity": None, "iterations": 0}
    },
    "feature_requests": [],
    "logs": []
}

settings = None
orchestrator = None


def load_settings():
    """Load or reload settings."""
    global settings, orchestrator
    try:
        settings = load_config()
        orchestrator = PipelineOrchestrator(
            api_key=settings.anthropic_api_key or settings.gemini_api_key or settings.grok_api_key or settings.groq_api_key or settings.openai_api_key,
            workspace_path=settings.workspace_path,
            settings=settings
        )
        return True
    except Exception as e:
        log_message(f"Error loading settings: {e}", "error")
        return False


def log_message(message: str, level: str = "info"):
    """Add log message and broadcast to connected clients."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": message
    }
    pipeline_state["logs"].append(log_entry)

    # Keep only last 1000 logs
    if len(pipeline_state["logs"]) > 1000:
        pipeline_state["logs"] = pipeline_state["logs"][-1000:]

    socketio.emit('log', log_entry)


def update_agent_status(agent_name: str, status: str, iterations: int = None):
    """Update agent status and broadcast to clients."""
    pipeline_state["agents"][agent_name]["status"] = status
    pipeline_state["agents"][agent_name]["last_activity"] = datetime.now().isoformat()

    if iterations is not None:
        pipeline_state["agents"][agent_name]["iterations"] = iterations

    socketio.emit('agent_update', {
        "agent": agent_name,
        "status": status,
        "last_activity": pipeline_state["agents"][agent_name]["last_activity"],
        "iterations": pipeline_state["agents"][agent_name]["iterations"]
    })


# Routes

@app.route('/')
def index():
    """Main dashboard."""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """Get current pipeline status."""
    return jsonify(pipeline_state)


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration."""
    if not settings:
        return jsonify({"error": "Configuration not loaded"}), 500

    # Return config without sensitive API keys (mask them)
    config_dict = settings.to_dict()

    for key in config_dict:
        if 'api_key' in key and config_dict[key]:
            # Mask API key, show only last 4 characters
            config_dict[key] = f"***{config_dict[key][-4:]}"

    return jsonify(config_dict)


@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration."""
    try:
        new_config = request.json

        # Load current config
        config_path = Path("./config.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                current_config = json.load(f)
        else:
            current_config = {}

        # Update with new values (don't update masked API keys)
        for key, value in new_config.items():
            if 'api_key' in key and value and value.startswith('***'):
                # Keep existing API key if masked
                continue
            current_config[key] = value

        # Save updated config
        with open(config_path, 'w') as f:
            json.dump(current_config, f, indent=2)

        # Reload settings
        if load_settings():
            log_message("Configuration updated successfully", "info")
            return jsonify({"success": True, "message": "Configuration updated"})
        else:
            return jsonify({"error": "Failed to reload configuration"}), 500

    except Exception as e:
        log_message(f"Error updating configuration: {e}", "error")
        return jsonify({"error": str(e)}), 500


@app.route('/api/feature-requests', methods=['GET'])
def get_feature_requests():
    """Get all feature requests."""
    return jsonify(pipeline_state["feature_requests"])


@app.route('/api/feature-requests', methods=['POST'])
def add_feature_request():
    """Add a new feature request."""
    try:
        data = request.json
        feature_request = {
            "id": len(pipeline_state["feature_requests"]) + 1,
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "repo_url": data.get("repo_url", ""),
            "priority": data.get("priority", "medium"),
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "assigned_to": None
        }

        pipeline_state["feature_requests"].append(feature_request)
        log_message(f"New feature request added: {feature_request['title']}", "info")
        socketio.emit('feature_request_added', feature_request)

        return jsonify(feature_request)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/feature-requests/<int:request_id>', methods=['DELETE'])
def delete_feature_request(request_id):
    """Delete a feature request."""
    pipeline_state["feature_requests"] = [
        fr for fr in pipeline_state["feature_requests"] if fr["id"] != request_id
    ]
    socketio.emit('feature_request_deleted', {"id": request_id})
    return jsonify({"success": True})


@app.route('/api/pipeline/run', methods=['POST'])
def run_pipeline():
    """Run the full pipeline."""
    try:
        data = request.json
        requirements = data.get("requirements", "")
        repo_url = data.get("repo_url", None)

        if not requirements:
            return jsonify({"error": "Requirements are required"}), 400

        if not orchestrator:
            if not load_settings():
                return jsonify({"error": "Failed to load configuration"}), 500

        # Run pipeline in background thread
        def run_in_background():
            try:
                pipeline_state["status"] = "running"
                log_message(f"Starting pipeline: {requirements}", "info")
                socketio.emit('pipeline_status', {"status": "running"})

                result = orchestrator.run_full_pipeline(
                    requirements=requirements,
                    repo_url=repo_url,
                    output_dir=f"./pipeline_output/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )

                pipeline_state["status"] = result.get("status", "completed")
                log_message(f"Pipeline completed: {result.get('status')}", "info")
                socketio.emit('pipeline_status', {"status": pipeline_state["status"]})

            except Exception as e:
                pipeline_state["status"] = "error"
                log_message(f"Pipeline error: {e}", "error")
                socketio.emit('pipeline_status', {"status": "error", "error": str(e)})

        thread = threading.Thread(target=run_in_background)
        thread.daemon = True
        thread.start()

        return jsonify({"success": True, "message": "Pipeline started"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/agent/prompt', methods=['POST'])
def send_agent_prompt():
    """Send a prompt to a specific agent."""
    try:
        data = request.json
        agent_name = data.get("agent", "")
        prompt = data.get("prompt", "")

        if agent_name not in pipeline_state["agents"]:
            return jsonify({"error": "Invalid agent name"}), 400

        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        # Run agent in background thread
        def run_agent_in_background():
            try:
                update_agent_status(agent_name, "running")
                log_message(f"Sending prompt to {agent_name}: {prompt[:50]}...", "info")

                # Create agent and run
                agent = orchestrator._create_agent(agent_name)
                with agent:
                    agent.setup_sandbox()
                    result = agent.run_agent(prompt)

                update_agent_status(agent_name, "completed", result.get("iterations", 0))
                log_message(f"{agent_name} completed", "info")

            except Exception as e:
                update_agent_status(agent_name, "error")
                log_message(f"{agent_name} error: {e}", "error")

        thread = threading.Thread(target=run_agent_in_background)
        thread.daemon = True
        thread.start()

        return jsonify({"success": True, "message": f"Prompt sent to {agent_name}"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/logs')
def get_logs():
    """Get recent logs."""
    limit = request.args.get('limit', 100, type=int)
    return jsonify(pipeline_state["logs"][-limit:])


# WebSocket events

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    log_message("Client connected", "info")
    emit('status', pipeline_state)


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    log_message("Client disconnected", "info")


def main():
    """Run the web server."""
    # Load initial settings
    load_settings()

    # Get port from environment or default to 5000
    port = int(os.getenv('WEB_PORT', 5000))
    host = os.getenv('WEB_HOST', '0.0.0.0')

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║        AI Agent Pipeline - Web Interface                    ║
╠══════════════════════════════════════════════════════════════╣
║  Server: http://{host}:{port}                           ║
║  Status: Running                                            ║
╚══════════════════════════════════════════════════════════════╝
    """)

    socketio.run(app, host=host, port=port, debug=True, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    main()
