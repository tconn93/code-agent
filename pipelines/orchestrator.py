"""
Pipeline Orchestrator for coordinating multi-agent workflows.
"""
import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

from agents.architect_agent import ArchitectAgent
from agents.coding_agent import CodingAgent
from agents.testing_agent import TestingAgent
from agents.deployment_agent import DeploymentAgent
from agents.monitoring_agent import MonitoringAgent


class PipelineOrchestrator:
    """
    Orchestrates the software development pipeline across multiple agents.

    Workflow:
    1. Architecture/Design -> 2. Implementation -> 3. Testing -> 4. Deployment -> 5. Monitoring
    """

    def __init__(self, api_key: str, workspace_path: str = "/tmp/agent-workspace"):
        self.api_key = api_key
        self.workspace_path = workspace_path
        self.pipeline_state = {
            "status": "initialized",
            "current_stage": None,
            "stages_completed": [],
            "results": {},
            "errors": [],
            "started_at": None,
            "completed_at": None
        }

    def _create_agent(self, agent_type: str):
        """Create an agent instance."""
        agents = {
            "architect": ArchitectAgent,
            "coding": CodingAgent,
            "testing": TestingAgent,
            "deployment": DeploymentAgent,
            "monitoring": MonitoringAgent
        }

        if agent_type not in agents:
            raise ValueError(f"Unknown agent type: {agent_type}")

        return agents[agent_type](self.api_key, self.workspace_path)

    def _save_state(self, output_dir: str = None):
        """Save pipeline state to file."""
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            state_file = Path(output_dir) / "pipeline_state.json"
            with open(state_file, 'w') as f:
                json.dump(self.pipeline_state, f, indent=2, default=str)

    def run_full_pipeline(self, requirements: str, repo_url: Optional[str] = None,
                         output_dir: str = "./pipeline_output") -> Dict:
        """
        Run the full development pipeline from requirements to deployment.

        Args:
            requirements: Project requirements and specifications
            repo_url: Git repository URL (optional, for existing projects)
            output_dir: Directory to save pipeline outputs

        Returns:
            Pipeline execution results
        """
        self.pipeline_state["started_at"] = datetime.now().isoformat()
        self.pipeline_state["status"] = "running"

        print("=" * 80)
        print("STARTING SOFTWARE DEVELOPMENT PIPELINE")
        print("=" * 80)

        try:
            # Stage 1: Architecture & Design
            print("\n" + "=" * 80)
            print("STAGE 1: ARCHITECTURE & DESIGN")
            print("=" * 80)
            self.pipeline_state["current_stage"] = "architecture"

            with self._create_agent("architect") as architect:
                if repo_url:
                    arch_result = architect.review_architecture(
                        repo_url=repo_url,
                        existing_workspace=self.workspace_path
                    )
                    print("\n[ARCHITECT] Architecture review completed")
                else:
                    arch_result = architect.design_system(
                        requirements=requirements,
                        existing_workspace=self.workspace_path
                    )
                    print("\n[ARCHITECT] System design completed")

                self.pipeline_state["results"]["architecture"] = arch_result
                self.pipeline_state["stages_completed"].append("architecture")

            self._save_state(output_dir)

            # Stage 2: Implementation
            print("\n" + "=" * 80)
            print("STAGE 2: IMPLEMENTATION")
            print("=" * 80)
            self.pipeline_state["current_stage"] = "coding"

            with self._create_agent("coding") as coder:
                # Extract implementation plan from architecture
                impl_spec = f"""Based on the architecture design, implement the following:

{requirements}

Architecture artifacts are available in docs/architecture/

Follow the architecture design and implement all required components."""

                coding_result = coder.implement_feature(
                    feature_spec=impl_spec,
                    existing_workspace=self.workspace_path
                )
                print("\n[CODING] Implementation completed")

                self.pipeline_state["results"]["coding"] = coding_result
                self.pipeline_state["stages_completed"].append("coding")

            self._save_state(output_dir)

            # Stage 3: Testing
            print("\n" + "=" * 80)
            print("STAGE 3: TESTING & QA")
            print("=" * 80)
            self.pipeline_state["current_stage"] = "testing"

            with self._create_agent("testing") as tester:
                test_spec = f"""Create comprehensive tests for the implemented features:

{requirements}

Ensure:
- Unit tests for all components
- Integration tests for component interactions
- End-to-end tests for key workflows
- Edge cases and error handling
- Achieve >80% code coverage"""

                testing_result = tester.create_tests(
                    spec=test_spec,
                    existing_workspace=self.workspace_path
                )
                print("\n[TESTING] Testing completed")

                # Run QA suite
                qa_result = tester.run_qa_suite(existing_workspace=self.workspace_path)
                print("\n[TESTING] QA suite completed")

                self.pipeline_state["results"]["testing"] = testing_result
                self.pipeline_state["results"]["qa"] = qa_result
                self.pipeline_state["stages_completed"].append("testing")

            self._save_state(output_dir)

            # Stage 4: Deployment
            print("\n" + "=" * 80)
            print("STAGE 4: DEPLOYMENT")
            print("=" * 80)
            self.pipeline_state["current_stage"] = "deployment"

            with self._create_agent("deployment") as deployer:
                # Setup deployment infrastructure
                setup_result = deployer.setup_deployment(
                    platform="docker",
                    existing_workspace=self.workspace_path
                )
                print("\n[DEPLOYMENT] Deployment setup completed")

                # Deploy to staging
                deploy_result = deployer.execute_deployment(
                    environment="staging",
                    existing_workspace=self.workspace_path
                )
                print("\n[DEPLOYMENT] Staging deployment completed")

                self.pipeline_state["results"]["deployment_setup"] = setup_result
                self.pipeline_state["results"]["deployment"] = deploy_result
                self.pipeline_state["stages_completed"].append("deployment")

            self._save_state(output_dir)

            # Stage 5: Monitoring
            print("\n" + "=" * 80)
            print("STAGE 5: MONITORING & OBSERVABILITY")
            print("=" * 80)
            self.pipeline_state["current_stage"] = "monitoring"

            with self._create_agent("monitoring") as monitor:
                # Setup monitoring
                monitoring_result = monitor.setup_monitoring(
                    platform="prometheus",
                    existing_workspace=self.workspace_path
                )
                print("\n[MONITORING] Monitoring setup completed")

                # Perform health audit
                health_result = monitor.perform_health_audit(
                    services=["http://localhost:3000", "http://localhost:8000"],
                    existing_workspace=self.workspace_path
                )
                print("\n[MONITORING] Health audit completed")

                self.pipeline_state["results"]["monitoring_setup"] = monitoring_result
                self.pipeline_state["results"]["health_audit"] = health_result
                self.pipeline_state["stages_completed"].append("monitoring")

            self._save_state(output_dir)

            # Pipeline completed successfully
            self.pipeline_state["status"] = "completed"
            self.pipeline_state["completed_at"] = datetime.now().isoformat()
            self.pipeline_state["current_stage"] = None

            print("\n" + "=" * 80)
            print("PIPELINE COMPLETED SUCCESSFULLY")
            print("=" * 80)
            print(f"\nStages completed: {', '.join(self.pipeline_state['stages_completed'])}")
            print(f"Results saved to: {output_dir}")

        except Exception as e:
            self.pipeline_state["status"] = "failed"
            self.pipeline_state["errors"].append(str(e))
            self.pipeline_state["completed_at"] = datetime.now().isoformat()

            print("\n" + "=" * 80)
            print("PIPELINE FAILED")
            print("=" * 80)
            print(f"Error: {e}")

            raise

        finally:
            self._save_state(output_dir)

        return self.pipeline_state

    def run_partial_pipeline(self, stages: List[str], task_descriptions: Dict[str, str],
                           repo_url: Optional[str] = None,
                           output_dir: str = "./pipeline_output") -> Dict:
        """
        Run specific stages of the pipeline.

        Args:
            stages: List of stages to run (e.g., ['coding', 'testing'])
            task_descriptions: Dictionary mapping stage names to task descriptions
            repo_url: Git repository URL
            output_dir: Directory to save outputs

        Returns:
            Pipeline execution results
        """
        self.pipeline_state["started_at"] = datetime.now().isoformat()
        self.pipeline_state["status"] = "running"

        print("=" * 80)
        print(f"RUNNING PIPELINE STAGES: {', '.join(stages)}")
        print("=" * 80)

        stage_agent_map = {
            "architecture": "architect",
            "coding": "coding",
            "testing": "testing",
            "deployment": "deployment",
            "monitoring": "monitoring"
        }

        try:
            for stage in stages:
                if stage not in stage_agent_map:
                    raise ValueError(f"Unknown stage: {stage}")

                print(f"\n{'=' * 80}")
                print(f"STAGE: {stage.upper()}")
                print("=" * 80)

                self.pipeline_state["current_stage"] = stage
                agent_type = stage_agent_map[stage]

                with self._create_agent(agent_type) as agent:
                    task = task_descriptions.get(stage, "")
                    result = agent.run_agent(task)

                    self.pipeline_state["results"][stage] = result
                    self.pipeline_state["stages_completed"].append(stage)

                    print(f"\n[{stage.upper()}] Stage completed")

                self._save_state(output_dir)

            self.pipeline_state["status"] = "completed"
            self.pipeline_state["completed_at"] = datetime.now().isoformat()
            self.pipeline_state["current_stage"] = None

            print("\n" + "=" * 80)
            print("PARTIAL PIPELINE COMPLETED")
            print("=" * 80)

        except Exception as e:
            self.pipeline_state["status"] = "failed"
            self.pipeline_state["errors"].append(str(e))
            self.pipeline_state["completed_at"] = datetime.now().isoformat()
            raise

        finally:
            self._save_state(output_dir)

        return self.pipeline_state

    def run_code_review_pipeline(self, repo_url: str, focus_areas: List[str] = None,
                                output_dir: str = "./review_output") -> Dict:
        """
        Run a code review pipeline (Architecture Review + Code Review + QA).

        Args:
            repo_url: Git repository URL
            focus_areas: Specific areas to focus on
            output_dir: Directory to save outputs

        Returns:
            Review results
        """
        print("=" * 80)
        print("STARTING CODE REVIEW PIPELINE")
        print("=" * 80)

        self.pipeline_state["started_at"] = datetime.now().isoformat()
        self.pipeline_state["status"] = "running"

        try:
            # Architecture Review
            print("\n" + "=" * 80)
            print("ARCHITECTURE REVIEW")
            print("=" * 80)

            with self._create_agent("architect") as architect:
                arch_review = architect.review_architecture(
                    repo_url=repo_url,
                    existing_workspace=self.workspace_path
                )
                self.pipeline_state["results"]["architecture_review"] = arch_review

            # Code Review
            print("\n" + "=" * 80)
            print("CODE REVIEW")
            print("=" * 80)

            with self._create_agent("coding") as coder:
                code_review = coder.review_code(
                    existing_workspace=self.workspace_path,
                    focus_areas=focus_areas
                )
                self.pipeline_state["results"]["code_review"] = code_review

            # QA Review
            print("\n" + "=" * 80)
            print("QA REVIEW")
            print("=" * 80)

            with self._create_agent("testing") as tester:
                qa_review = tester.run_qa_suite(existing_workspace=self.workspace_path)
                self.pipeline_state["results"]["qa_review"] = qa_review

            self.pipeline_state["status"] = "completed"
            self.pipeline_state["completed_at"] = datetime.now().isoformat()

            print("\n" + "=" * 80)
            print("CODE REVIEW PIPELINE COMPLETED")
            print("=" * 80)

        except Exception as e:
            self.pipeline_state["status"] = "failed"
            self.pipeline_state["errors"].append(str(e))
            raise

        finally:
            self._save_state(output_dir)

        return self.pipeline_state
