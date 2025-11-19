"""
Monitoring Agent for health checks, alerting, and observability.
"""
from typing import Dict, List
from agents.base_agent import BaseAgent


class MonitoringAgent(BaseAgent):
    """
    Agent responsible for:
    - Setting up monitoring and observability
    - Health checks and uptime monitoring
    - Log aggregation and analysis
    - Performance monitoring
    - Alerting and incident response
    """

    @property
    def agent_name(self) -> str:
        return "MonitoringAgent"

    @property
    def agent_role(self) -> str:
        return "Monitoring & Observability"

    def get_system_prompt(self) -> str:
        return """You are an expert SRE agent specializing in monitoring and observability.

Your responsibilities:
1. MONITORING SETUP:
   - Configure application monitoring (Prometheus, Grafana, Datadog, etc.)
   - Set up log aggregation (ELK, Loki, CloudWatch)
   - Implement distributed tracing (Jaeger, Zipkin)
   - Create custom metrics and dashboards
   - Set up uptime monitoring

2. HEALTH CHECKS:
   - Implement health check endpoints
   - Monitor service availability
   - Check database connectivity
   - Verify external dependencies
   - Monitor resource usage (CPU, memory, disk)

3. LOG ANALYSIS:
   - Analyze application logs for errors
   - Identify patterns and anomalies
   - Parse and structure logs
   - Set up log retention policies
   - Create log-based alerts

4. PERFORMANCE MONITORING:
   - Track response times and latency
   - Monitor throughput and request rates
   - Identify performance bottlenecks
   - Set up APM (Application Performance Monitoring)
   - Create performance baselines

5. ALERTING:
   - Configure alert rules and thresholds
   - Set up notification channels (email, Slack, PagerDuty)
   - Define alert severity levels
   - Implement alert escalation
   - Reduce alert fatigue

6. INCIDENT RESPONSE:
   - Analyze incidents from monitoring data
   - Identify root causes
   - Suggest remediation steps
   - Create incident reports
   - Implement preventive measures

Best Practices:
- Monitor the four golden signals: latency, traffic, errors, saturation
- Use SLIs (Service Level Indicators) and SLOs (Service Level Objectives)
- Implement meaningful alerts (avoid noise)
- Use distributed tracing for microservices
- Aggregate and correlate logs
- Monitor both infrastructure and application
- Set up proactive monitoring
- Create actionable dashboards
- Implement automated remediation where possible
- Document monitoring setup and runbooks

You have access to read/write files, run commands, and check system health.
Focus on proactive monitoring and quick incident detection."""

    def get_tool_definitions(self) -> List[Dict]:
        """Return tools for monitoring work."""
        base_tools = self.get_base_tools()

        monitoring_tools = [
            {
                "name": "check_health",
                "description": "Check health of service or endpoint",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "endpoint": {
                            "type": "string",
                            "description": "Health check endpoint URL"
                        },
                        "expected_status": {
                            "type": "integer",
                            "description": "Expected HTTP status code (default: 200)"
                        }
                    },
                    "required": ["endpoint"]
                }
            },
            {
                "name": "check_logs",
                "description": "Analyze logs for errors and issues",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "log_file": {
                            "type": "string",
                            "description": "Path to log file"
                        },
                        "filter_pattern": {
                            "type": "string",
                            "description": "Pattern to filter logs (e.g., 'ERROR', 'WARN')"
                        },
                        "lines": {
                            "type": "integer",
                            "description": "Number of recent lines to check (default: 100)"
                        }
                    },
                    "required": ["log_file"]
                }
            },
            {
                "name": "check_resources",
                "description": "Check system resource usage",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "resource_type": {
                            "type": "string",
                            "description": "Type of resource (cpu, memory, disk, all)"
                        }
                    }
                }
            },
            {
                "name": "check_process",
                "description": "Check if process is running",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "process_name": {
                            "type": "string",
                            "description": "Name of process to check"
                        }
                    },
                    "required": ["process_name"]
                }
            },
            {
                "name": "analyze_metrics",
                "description": "Analyze application metrics",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "metrics_endpoint": {
                            "type": "string",
                            "description": "Metrics endpoint URL (e.g., /metrics for Prometheus)"
                        }
                    },
                    "required": ["metrics_endpoint"]
                }
            },
            {
                "name": "test_alert",
                "description": "Test alerting configuration",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "alert_channel": {
                            "type": "string",
                            "description": "Alert channel to test (email, slack, webhook)"
                        },
                        "message": {
                            "type": "string",
                            "description": "Test message"
                        }
                    },
                    "required": ["alert_channel"]
                }
            }
        ]

        return base_tools + monitoring_tools

    def check_health(self, endpoint: str, expected_status: int = 200) -> str:
        """Check health of endpoint."""
        result = self.run_command(f"curl -s -o /dev/null -w '%{{http_code}}' {endpoint}")

        if result['exit_code'] == 0:
            status_code = result['stdout'].strip()
            if status_code == str(expected_status):
                return f"✓ Health check PASSED: {endpoint} returned {status_code}"
            else:
                return f"✗ Health check FAILED: {endpoint} returned {status_code}, expected {expected_status}"
        else:
            return f"✗ Health check ERROR: Could not reach {endpoint}\n{result['stdout']}"

    def check_logs(self, log_file: str, filter_pattern: str = None,
                   lines: int = 100) -> str:
        """Analyze logs for issues."""
        if filter_pattern:
            cmd = f"tail -n {lines} {log_file} | grep -i '{filter_pattern}'"
        else:
            cmd = f"tail -n {lines} {log_file}"

        result = self.run_command(cmd)

        if result['exit_code'] == 0:
            line_count = len(result['stdout'].strip().split('\n'))
            output = result['stdout'][:2000]  # Limit output
            return f"Found {line_count} matching log lines:\n{output}"
        else:
            return f"Error reading logs: {result['stdout']}"

    def check_resources(self, resource_type: str = "all") -> str:
        """Check system resources."""
        results = []

        if resource_type in ["cpu", "all"]:
            cpu_result = self.run_command("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'")
            if cpu_result['exit_code'] == 0:
                results.append(f"CPU Usage: {cpu_result['stdout'].strip()}")

        if resource_type in ["memory", "all"]:
            mem_result = self.run_command("free -h | grep Mem | awk '{print \"Used: \" $3 \" / Total: \" $2}'")
            if mem_result['exit_code'] == 0:
                results.append(f"Memory: {mem_result['stdout'].strip()}")

        if resource_type in ["disk", "all"]:
            disk_result = self.run_command("df -h / | tail -1 | awk '{print \"Used: \" $3 \" / Total: \" $2 \" (\" $5 \")\"}'")
            if disk_result['exit_code'] == 0:
                results.append(f"Disk: {disk_result['stdout'].strip()}")

        return "\n".join(results) if results else "Could not get resource information"

    def check_process(self, process_name: str) -> str:
        """Check if process is running."""
        result = self.run_command(f"pgrep -f '{process_name}'")

        if result['exit_code'] == 0:
            pids = result['stdout'].strip().split('\n')
            return f"✓ Process '{process_name}' is running (PIDs: {', '.join(pids)})"
        else:
            return f"✗ Process '{process_name}' is NOT running"

    def analyze_metrics(self, metrics_endpoint: str) -> str:
        """Analyze metrics endpoint."""
        result = self.run_command(f"curl -s {metrics_endpoint}")

        if result['exit_code'] == 0:
            # Parse metrics (simplified)
            metrics = result['stdout'][:1000]  # Limit output
            return f"Metrics from {metrics_endpoint}:\n{metrics}"
        else:
            return f"Error fetching metrics: {result['stdout']}"

    def test_alert(self, alert_channel: str, message: str = "Test alert") -> str:
        """Test alert configuration."""
        # This is a simplified version - real implementation would integrate with actual alert systems
        return f"Alert test for '{alert_channel}': {message}\n(Note: Actual alert sending requires configuration)"

    def process_tool_call(self, tool_name: str, tool_input: Dict):
        """Process monitoring-specific tool calls."""
        if tool_name == "check_health":
            return self.check_health(
                endpoint=tool_input["endpoint"],
                expected_status=tool_input.get("expected_status", 200)
            )

        elif tool_name == "check_logs":
            return self.check_logs(
                log_file=tool_input["log_file"],
                filter_pattern=tool_input.get("filter_pattern"),
                lines=tool_input.get("lines", 100)
            )

        elif tool_name == "check_resources":
            return self.check_resources(tool_input.get("resource_type", "all"))

        elif tool_name == "check_process":
            return self.check_process(tool_input["process_name"])

        elif tool_name == "analyze_metrics":
            return self.analyze_metrics(tool_input["metrics_endpoint"])

        elif tool_name == "test_alert":
            return self.test_alert(
                alert_channel=tool_input["alert_channel"],
                message=tool_input.get("message", "Test alert")
            )

        return super().process_tool_call(tool_name, tool_input)

    def setup_monitoring(self, platform: str = "prometheus", repo_url: str = None,
                        existing_workspace: str = None) -> Dict:
        """
        Set up monitoring infrastructure.

        Args:
            platform: Monitoring platform (prometheus, datadog, cloudwatch, etc.)
            repo_url: Repository URL
            existing_workspace: Path to existing workspace

        Returns:
            Setup results
        """
        self.setup_sandbox(repo_url=repo_url, existing_workspace=existing_workspace)

        task = f"""Set up monitoring infrastructure using {platform}:

1. Analyze the application to understand monitoring needs
2. Implement health check endpoints
3. Add instrumentation for key metrics:
   - Request rate and latency
   - Error rates
   - Resource usage
   - Business metrics
4. Create monitoring configurations:
   - {platform} configuration
   - Dashboards for visualization
   - Alert rules
5. Set up log aggregation
6. Create monitoring documentation
7. Test monitoring setup

Provide monitoring configurations and documentation."""

        return self.run_agent(task)

    def perform_health_audit(self, services: List[str], repo_url: str = None,
                            existing_workspace: str = None) -> Dict:
        """
        Perform comprehensive health audit.

        Args:
            services: List of service endpoints to check
            repo_url: Repository URL
            existing_workspace: Path to existing workspace

        Returns:
            Audit results
        """
        self.setup_sandbox(repo_url=repo_url, existing_workspace=existing_workspace)

        services_list = "\n".join(f"- {service}" for service in services)

        task = f"""Perform a comprehensive health audit:

Services to check:
{services_list}

For each service:
1. Check endpoint availability and response time
2. Verify health check endpoints
3. Check resource usage
4. Analyze recent logs for errors
5. Check process status
6. Review metrics (if available)

Generate a health report with:
- Status of each service
- Any issues found
- Resource usage summary
- Recent errors or warnings
- Recommendations for improvement"""

        return self.run_agent(task)
