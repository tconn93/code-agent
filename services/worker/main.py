"""
Worker Service - Processes jobs from the Redis queue

This service:
1. Polls Redis for pending jobs
2. Fetches job details from PostgreSQL
3. Instantiates and executes the appropriate agent
4. Updates job status and results in the database
"""
import os
import sys
import time
import json
import redis
import logging
from datetime import datetime
from typing import Optional, Dict, Any

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker, Session
from services.api.models import Job, Agent, SystemConfig
from agents.architect_agent import ArchitectAgent
from agents.coding_agent import CodingAgent
from agents.testing_agent import TestingAgent
from agents.deployment_agent import DeploymentAgent
from agents.monitoring_agent import MonitoringAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://agent_user:agent_password@localhost:5432/agent_platform")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
AGENT_ID = os.getenv("AGENT_ID")  # Set when spawned as container
AGENT_NAME = os.getenv("AGENT_NAME", f"worker-{os.getpid()}")
AGENT_PROVIDER = os.getenv("AGENT_PROVIDER", "anthropic")
AGENT_MODEL = os.getenv("AGENT_MODEL", "")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "5"))  # seconds
HEARTBEAT_INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL", "30"))  # seconds

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redis setup
r = redis.from_url(REDIS_URL)

# Agent type mapping
AGENT_CLASSES = {
    "architect": ArchitectAgent,
    "coding": CodingAgent,
    "testing": TestingAgent,
    "deployment": DeploymentAgent,
    "monitoring": MonitoringAgent,
}


class Worker:
    """Worker that processes jobs from the queue"""

    def __init__(self, agent_id: Optional[int] = None):
        self.agent_id = agent_id
        self.running = True
        self.last_heartbeat = time.time()
        self.current_job_id = None

    def get_db(self) -> Session:
        """Get database session"""
        return SessionLocal()

    def send_heartbeat(self, db: Session):
        """Update agent heartbeat in database"""
        if not self.agent_id:
            return

        now = time.time()
        if now - self.last_heartbeat < HEARTBEAT_INTERVAL:
            return

        try:
            db.execute(
                update(Agent)
                .where(Agent.id == self.agent_id)
                .values(
                    last_heartbeat=datetime.utcnow(),
                    status="busy" if self.current_job_id else "idle",
                    current_job_id=self.current_job_id
                )
            )
            db.commit()
            self.last_heartbeat = now
            logger.debug(f"Heartbeat sent for agent {self.agent_id}")
        except Exception as e:
            logger.error(f"Failed to send heartbeat: {e}")
            db.rollback()

    def get_api_key_for_provider(self, provider: str) -> Optional[str]:
        """Get API key for the specified provider from database settings or env var"""
        env_key = f"{provider.upper()}_API_KEY"
        api_key = os.getenv(env_key)

        # Try database first
        db = self.get_db()
        try:
            db_key = db.query(SystemConfig).filter(SystemConfig.key == env_key).first()
            if db_key and db_key.value:
                api_key = db_key.value
                logger.info(f"Loaded API key for {provider} from database")
            elif not api_key:
                logger.warning(f"No API key found for provider '{provider}' (db/env: {env_key})")
        except Exception as e:
            logger.error(f"Failed to fetch API key from database: {e}")
            # Fallback to env var if already set
        finally:
            db.close()

        return api_key

    def create_agent(self, agent_type: str, provider: str = None, model: str = None):
        """Create an agent instance"""
        if agent_type not in AGENT_CLASSES:
            raise ValueError(f"Unknown agent type: {agent_type}")

        # Use provided provider/model or defaults
        provider = provider or AGENT_PROVIDER or "anthropic"
        model = model or AGENT_MODEL or None

        # Get API key
        api_key = self.get_api_key_for_provider(provider)
        if not api_key:
            raise ValueError(f"No API key available for provider '{provider}'")

        # Create agent
        agent_class = AGENT_CLASSES[agent_type]
        agent = agent_class(
            api_key=api_key,
            provider=provider,
            model=model
        )
        agent.docker_image = os.getenv("DOCKER_IMAGE", "coding-agent-sandbox")
        agent.max_iterations = int(os.getenv("MAX_ITERATIONS", "20"))
        agent.output_truncate_length = int(os.getenv("OUTPUT_TRUNCATE_LENGTH", "5000"))

        logger.info(f"Created {agent_type} agent with provider={provider}, model={model}")
        return agent

    def process_job(self, job_id: int):
        """Process a single job"""
        db = self.get_db()
        try:
            # Fetch job from database
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                logger.warning(f"Job {job_id} not found in database")
                return

            # Check if job is already completed or running
            if job.status in ["completed", "running"]:
                logger.info(f"Job {job_id} already {job.status}, skipping")
                return

            # Update job status to running
            job.status = "running"
            job.updated_at = datetime.utcnow()
            if self.agent_id:
                job.assigned_agent_id = self.agent_id
            db.commit()

            self.current_job_id = job_id
            logger.info(f"Starting job {job_id}: type={job.type}, project_id={job.project_id}")

            # Get agent configuration from assigned agent or use defaults
            agent_provider = AGENT_PROVIDER
            agent_model = AGENT_MODEL

            if job.assigned_agent_id:
                agent_record = db.query(Agent).filter(Agent.id == job.assigned_agent_id).first()
                if agent_record:
                    agent_provider = agent_record.provider or AGENT_PROVIDER
                    agent_model = agent_record.model or AGENT_MODEL or "grok-4-1-fast-reasoning" if agent_provider == "xai" else "claude-3-5-sonnet-20240620"

            # Determine agent type from job type
            agent_type = self.get_agent_type_from_job(job.type)

            # Create agent
            agent = self.create_agent(agent_type, agent_provider, agent_model)

            # Execute job based on type
            result = self.execute_job(agent, job, db)

            # Update job with results
            job.status = "completed"
            job.result = result
            job.updated_at = datetime.utcnow()
            db.commit()

            logger.info(f"Job {job_id} completed successfully")

        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}", exc_info=True)

            # Update job status to failed
            try:
                job = db.query(Job).filter(Job.id == job_id).first()
                if job:
                    job.status = "failed"
                    job.result = {"error": str(e)}
                    job.logs = f"Error: {str(e)}"
                    job.updated_at = datetime.utcnow()
                    db.commit()
            except Exception as update_error:
                logger.error(f"Failed to update job status: {update_error}")
                db.rollback()

        finally:
            self.current_job_id = None
            db.close()

    def get_agent_type_from_job(self, job_type: str) -> str:
        """Map job type to agent type"""
        job_to_agent_map = {
            "design_system": "architect",
            "review_architecture": "architect",
            "implement_feature": "coding",
            "review_code": "coding",
            "create_tests": "testing",
            "run_qa_suite": "testing",
            "setup_deployment": "deployment",
            "execute_deployment": "deployment",
            "setup_monitoring": "monitoring",
            "perform_health_audit": "monitoring",
        }

        agent_type = job_to_agent_map.get(job_type)
        if not agent_type:
            # Default: try to extract agent type from job_type
            # e.g., "coding_task" -> "coding"
            for atype in AGENT_CLASSES.keys():
                if atype in job_type.lower():
                    return atype

            # Fallback to coding agent
            logger.warning(f"Unknown job type '{job_type}', defaulting to 'coding' agent")
            return "coding"

        return agent_type

    def execute_job(self, agent, job: Job, db: Session) -> Dict[str, Any]:
        """Execute the job using the agent"""
        payload = job.payload or {}
        job_type = job.type

        # Get project if needed
        project = db.query(Job).filter(Job.id == job.id).first().project if job.project_id else None
        workspace_path = payload.get("workspace_path", f"/tmp/agent-workspace-{job.project_id}")

        # Execute based on job type
        if job_type == "design_system":
            requirements = payload.get("requirements", "")
            result = agent.design_system(
                requirements=requirements,
                existing_workspace=workspace_path
            )

        elif job_type == "review_architecture":
            repo_url = payload.get("repo_url") or (project.repo_url if project else None)
            result = agent.review_architecture(
                repo_url=repo_url,
                existing_workspace=workspace_path
            )

        elif job_type == "implement_feature":
            feature_spec = payload.get("task", payload.get("feature_spec", ""))
            result = agent.implement_feature(
                feature_spec=feature_spec,
                existing_workspace=workspace_path
            )

        elif job_type == "review_code":
            focus_areas = payload.get("focus_areas", [])
            result = agent.review_code(
                existing_workspace=workspace_path,
                focus_areas=focus_areas
            )

        elif job_type == "create_tests":
            spec = payload.get("spec", payload.get("task", ""))
            result = agent.create_tests(
                spec=spec,
                existing_workspace=workspace_path
            )

        elif job_type == "run_qa_suite":
            result = agent.run_qa_suite(existing_workspace=workspace_path)

        elif job_type == "setup_deployment":
            platform = payload.get("platform", "docker")
            repo_url = payload.get("repo_url") or (project.repo_url if project else None)
            result = agent.setup_deployment(
                platform=platform,
                repo_url=repo_url,
                existing_workspace=workspace_path
            )

        elif job_type == "execute_deployment":
            environment = payload.get("environment", "staging")
            repo_url = payload.get("repo_url") or (project.repo_url if project else None)
            result = agent.execute_deployment(
                environment=environment,
                repo_url=repo_url,
                existing_workspace=workspace_path
            )

        elif job_type == "setup_monitoring":
            platform = payload.get("platform", "prometheus")
            repo_url = payload.get("repo_url") or (project.repo_url if project else None)
            result = agent.setup_monitoring(
                platform=platform,
                repo_url=repo_url,
                existing_workspace=workspace_path
            )

        elif job_type == "perform_health_audit":
            services = payload.get("services", [])
            repo_url = payload.get("repo_url") or (project.repo_url if project else None)
            result = agent.perform_health_audit(
                services=services,
                repo_url=repo_url,
                existing_workspace=workspace_path
            )

        else:
            # Generic execution - use run_agent method
            task = payload.get("task", json.dumps(payload))
            result = agent.run_agent(task)

        return result

    def run(self):
        """Main agent worker loop - polls per-agent queue"""
        if not self.agent_id:
            logger.error("AGENT_ID env var required for agent worker")
            sys.exit(1)

        queue_name = f"job_queue_agent_{self.agent_id}"
        logger.info(f"Agent worker {AGENT_NAME} (ID: {self.agent_id}) polling queue: {queue_name}")
        logger.info(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")
        logger.info(f"Redis: {REDIS_URL}")

        while self.running:
            db = self.get_db()
            try:
                # Send heartbeat
                self.send_heartbeat(db)

                # Poll agent-specific queue
                result = r.brpop(queue_name, timeout=POLL_INTERVAL)

                if result:
                    _, job_id_bytes = result
                    job_id = int(job_id_bytes.decode('utf-8'))
                    logger.info(f"Agent {self.agent_id} received job {job_id} from {queue_name}")
                    # Process the job
                    self.process_job(job_id)
                else:
                    logger.debug(f"No jobs in {queue_name}, waiting...")

            except redis.ConnectionError as e:
                logger.error(f"Redis connection error: {e}")
                time.sleep(5)

            except KeyboardInterrupt:
                logger.info("Received interrupt signal, shutting down...")
                self.running = False
                break

            except Exception as e:
                logger.error(f"Agent worker error: {e}", exc_info=True)
                time.sleep(1)

            finally:
                db.close()

        logger.info(f"Agent worker {self.agent_id} stopped")


def main():
    """Main entry point for agent worker"""
    # AGENT_ID is required
    if not AGENT_ID:
        logger.error("AGENT_ID environment variable is required")
        sys.exit(1)

    try:
        agent_id = int(AGENT_ID)
    except ValueError:
        logger.error(f"Invalid AGENT_ID: {AGENT_ID}")
        sys.exit(1)

    # Create and run agent worker
    worker = Worker(agent_id=agent_id)
    worker.run()


if __name__ == "__main__":
    main()
