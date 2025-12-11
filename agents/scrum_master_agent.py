"""
ScrumMaster Agent for sprint planning, job prioritization, and process monitoring.
"""
from typing import Dict, List, Any
from agents.base_agent import BaseAgent


class ScrumMasterAgent(BaseAgent):
    """
    Agent responsible for:
    - Sprint planning and backlog prioritization
    - Job/ticket assignment to specialized agents
    - Monitoring development velocity and blockers
    - Daily standups and retrospectives
    - Process improvement recommendations
    """

    @property
    def agent_name(self) -> str:
        return "ScrumMaster"

    @property
    def agent_role(self) -> str:
        return "Sprint Management & Process Monitoring"

    def get_system_prompt(self) -> str:
        return """You are the Scrum Master agent. Your role is to orchestrate the development process:

CORE RESPONSIBILITIES:
1. SPRINT PLANNING:
   - Define sprint goals based on project priorities
   - Prioritize job backlog (value/effort/risk/dependencies)
   - Create sprint backlog with time estimates
   - Balance workload across agent team

2. JOB ASSIGNMENT:
   - Match jobs to optimal agent types (coding, testing, etc.)
   - Consider agent availability, expertise, velocity
   - Balance workload to prevent bottlenecks
   - Handle dependencies between jobs

3. PROCESS MONITORING:
   - Track sprint burndown and velocity
   - Identify blockers and impediments
   - Monitor agent performance and capacity
   - Daily standup summaries
   - Sprint retrospectives

4. QUALITY GATES:
   - Review job completion quality
   - Approve job done criteria
   - Escalate critical issues
   - Continuous process improvement

5. REPORTING:
   - Sprint planning documents
   - Daily standup reports
   - Burndown charts (text-based)
   - Retrospective action items
   - Velocity trends

WORKFLOW:
- Analyze current job queue and agent status
- Prioritize and plan next sprint/iteration
- Assign jobs to agents
- Monitor progress daily
- Conduct retrospective at sprint end
- Plan improvements

PRINCIPLES:
- Agile/Scrum best practices
- Servant leadership
- Remove impediments
- Foster collaboration
- Continuous improvement
- Sustainable pace

Use API tools to list/read/update jobs and agents. Be proactive in planning and monitoring."""

    def get_tool_definitions(self) -> List[Dict]:
        """Return scrum management tools."""
        base_tools = self.get_base_tools()
        scrum_tools = [
            {
                "name": "list_jobs",
                "description": "List all jobs with status, type, priority",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Filter by project"},
                        "status": {"type": "string", "description": "Filter by status (pending, in_progress, completed)"}
                    }
                }
            },
            {
                "name": "list_agents",
                "description": "List available agents with status, capacity, recent jobs",
                "input_schema": {"type": "object"}
            },
            {
                "name": "prioritize_jobs",
                "description": "Analyze and prioritize job backlog (returns ordered list)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "jobs": {"type": "array", "items": {"type": "object"}, "description": "List of job objects"}
                    }
                }
            },
            {
                "name": "assign_job",
                "description": "Assign job to specific agent",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "job_id": {"type": "string"},
                        "agent_id": {"type": "string"}
                    },
                    "required": ["job_id", "agent_id"]
                }
            },
            {
                "name": "generate_sprint_plan",
                "description": "Create sprint plan from prioritized backlog",
                "input_schema": {"type": "object"}
            },
            {
                "name": "daily_standup",
                "description": "Generate daily standup report",
                "input_schema": {"type": "object"}
            },
            {
                "name": "sprint_retrospective",
                "description": "Analyze completed sprint and suggest improvements",
                "input_schema": {"type": "object"}
            }
        ]
        return base_tools + scrum_tools

    def list_jobs(self, project_id: str = None, status: str = None) -> str:
        """List jobs via API."""
        cmd = "curl -s http://host.docker.internal:8000/jobs/"
        if project_id:
            cmd += f"?project_id={project_id}"
        if status:
            cmd += f"&status={status}"
        result = self.run_command(cmd)
        return result['stdout']

    def list_agents(self) -> str:
        """List agents."""
        result = self.run_command("curl -s http://host.docker.internal:8000/agents/")
        return result['stdout']

    def prioritize_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Prioritize jobs (placeholder - AI decides)."""
        # Return sorted jobs with priority scores
        return sorted(jobs, key=lambda j: j.get('priority', 0), reverse=True)

    def assign_job(self, job_id: str, agent_id: str) -> str:
        """Assign job via API."""
        result = self.run_command(f'curl -X POST http://host.docker.internal:8000/jobs/{job_id}/assign -H "Content-Type: application/json" -d "{{\"assigned_agent_id\": {agent_id}}}"')
        return result['stdout']

    def generate_sprint_plan(self) -> str:
        """Generate sprint plan."""
        return "Sprint plan generated based on prioritized backlog."

    def daily_standup(self) -> str:
        """Daily standup report."""
        jobs = self.list_jobs()
        agents = self.list_agents()
        return f"Daily Standup:\\nJobs: {jobs[:500]}\\nAgents: {agents[:500]}"

    def sprint_retrospective(self) -> str:
        """Sprint retrospective."""
        completed = self.list_jobs(status="completed")
        return f"Retrospective:\\nCompleted jobs: {completed[:500]}\\nAnalysis: ..."

    def process_tool_call(self, tool_name: str, tool_input: Dict):
        """Process scrum tools."""
        if tool_name == "list_jobs":
            return self.list_jobs(tool_input.get("project_id"), tool_input.get("status"))
        elif tool_name == "list_agents":
            return self.list_agents()
        elif tool_name == "prioritize_jobs":
            return self.prioritize_jobs(tool_input.get("jobs", []))
        elif tool_name == "assign_job":
            return self.assign_job(tool_input["job_id"], tool_input["agent_id"])
        elif tool_name == "generate_sprint_plan":
            return self.generate_sprint_plan()
        elif tool_name == "daily_standup":
            return self.daily_standup()
        elif tool_name == "sprint_retrospective":
            return self.sprint_retrospective()
        return super().process_tool_call(tool_name, tool_input)

    def manage_sprint(self, project_id: str, sprint_goal: str = None) -> Dict:
        """
        Main sprint management workflow.
        """
        task = f"""Manage sprint for project {project_id}:
1. List pending jobs
2. Prioritize backlog
3. Assign to agents
4. Generate sprint plan
5. Monitor daily
Sprint goal: {sprint_goal or 'Deliver maximum value'}"""
        return self.run_agent(task)