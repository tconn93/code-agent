"""
Orchestrator Service - Routes jobs to specific agent queues

This service:
1. Polls the incoming_jobs queue for new jobs
2. Assigns unassigned jobs to idle agents
3. Routes jobs to per-agent queues (job_queue_agent_{id})
4. Updates job status and assigned_agent_id in database
"""

import os
import sys
import time
import json
import redis
import logging
from datetime import datetime
from typing import Optional

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker, Session
from services.api.models import Job, Agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://agent_user:agent_password@localhost:5432/agent_platform")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
POLL_INTERVAL = int(os.getenv("ORCHESTRATOR_POLL_INTERVAL", "1"))  # seconds, faster for routing

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redis setup
r = redis.from_url(REDIS_URL)

class Orchestrator:
    """Orchestrator that routes jobs to agents."""

    def __init__(self):
        self.running = True

    def get_db(self) -> Session:
        """Get database session."""
        return SessionLocal()

    def map_job_to_agent_type(self, job_type: str) -> str:
        """Map job type to agent type."""
        mapping = {
            "coding": "coding",
            "architect": "architect",
            "testing": "testing",
            "deployment": "deployment",
            "monitoring": "monitoring",
            # Add more as needed
        }
        return mapping.get(job_type, "coding")  # Default to coding

    def auto_assign(self, job: Job, db: Session) -> Optional[int]:
        """Auto-assign job to an idle agent matching type."""
        agent_type = self.map_job_to_agent_type(job.type)
        
        # Prefer xAI if available, then any idle
        # First try xAI
        xai_agent = db.query(Agent).filter(
            Agent.type == agent_type,
            Agent.provider == 'xai',
            Agent.status == 'idle',
            Agent.maintenance_mode == False
        ).order_by(Agent.priority.desc()).first()
        
        if xai_agent:
            logger.info(f"Auto-assigned {job.id} to xAI agent {xai_agent.id}")
            return xai_agent.id
        
        # Fallback to any idle
        available_agent = db.query(Agent).filter(
            Agent.type == agent_type,
            Agent.status == 'idle',
            Agent.maintenance_mode == False
        ).order_by(Agent.priority.desc()).first()
        
        if available_agent:
            logger.info(f"Auto-assigned {job.id} to agent {available_agent.id} ({available_agent.provider})")
            return available_agent.id
        else:
            logger.warning(f"No idle {agent_type} agent available for job {job.id}")
            return None

    def route_job(self, job_id: int):
        """Route a job to the appropriate agent queue."""
        db = self.get_db()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                logger.warning(f"Job {job_id} not found")
                return

            # If already assigned, just route
            if job.assigned_agent_id:
                agent_id = job.assigned_agent_id
                # Verify agent exists and is idle-ish
                agent = db.query(Agent).filter(Agent.id == agent_id).first()
                if not agent:
                    logger.error(f"Assigned agent {agent_id} not found for job {job_id}")
                    return
            else:
                # Auto-assign
                agent_id = self.auto_assign(job, db)
                if not agent_id:
                    # Hold job as 'queued' or fail
                    job.status = 'queued'  # Add to models if needed
                    db.commit()
                    logger.warning(f"Job {job_id} queued - no available agent")
                    return
                job.assigned_agent_id = agent_id
                db.commit()

            # Route to agent's queue
            queue_name = f"job_queue_agent_{agent_id}"
            r.lpush(queue_name, job_id)
            job.status = 'pending'  # Ensure status
            db.commit()

            logger.info(f"Routed job {job_id} to agent {agent_id} (queue: {queue_name})")

        except Exception as e:
            logger.error(f"Failed to route job {job_id}: {e}")
            db.rollback()
        finally:
            db.close()

    def run(self):
        """Main orchestrator loop."""
        logger.info("Orchestrator started - polling incoming_jobs")
        logger.info(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")
        logger.info(f"Redis: {REDIS_URL}")

        while self.running:
            try:
                # Poll incoming_jobs
                result = r.brpop("incoming_jobs", timeout=POLL_INTERVAL)

                if result:
                    _, job_id_bytes = result
                    job_id = int(job_id_bytes.decode('utf-8'))
                    logger.info(f"Received job {job_id} for routing")
                    self.route_job(job_id)
                else:
                    logger.info(f"Polled incoming_jobs - empty (length: {r.llen('incoming_jobs')})")

            except redis.ConnectionError as e:
                logger.error(f"Redis connection error: {e}")
                time.sleep(5)
            except KeyboardInterrupt:
                logger.info("Shutting down orchestrator...")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Orchestrator error: {e}", exc_info=True)
                time.sleep(1)

        logger.info("Orchestrator stopped")

def main():
    orchestrator = Orchestrator()
    orchestrator.run()

if __name__ == "__main__":
    main()
