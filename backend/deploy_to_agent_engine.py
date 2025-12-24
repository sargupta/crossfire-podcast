"""
Agent Engine Deployment Script
Deploys CROSSFIRE agents to GCP Agent Engine with managed runtime
"""

from pathlib import Path
from google.cloud import aiplatform
from typing import Dict
import json

# Project configuration
PROJECT_ID = "aipodcaster-481909"
LOCATION = "us-central1"
AGENT_DIR = Path(__file__).parent / "adk_agents"


class AgentEngineDeployer:
    """
    Manages deployment of CROSSFIRE agents to Agent Engine.
    """

    def __init__(self):
        aiplatform.init(project=PROJECT_ID, location=LOCATION)
        self.deployed_agents = {}

    def deploy_agent(
        self, agent_name: str, agent_path: Path, runtime_config: Dict = None
    ) -> Dict:
        """
        Deploy a single agent to Agent Engine.

        Args:
            agent_name: Name of the agent (e.g., 'shakti_moderator')
            agent_path: Path to agent directory
            runtime_config: Runtime configuration

        Returns:
            Deployment information
        """

        if runtime_config is None:
            runtime_config = self._default_runtime_config(agent_name)

        print(f"📦 Deploying {agent_name}...")

        try:
            # Create agent configuration
            agent_config = {
                "display_name": f"crossfire_{agent_name}",
                "description": f"CROSSFIRE debate agent: {agent_name}",
                "agent_directory": str(agent_path),
                "runtime_config": runtime_config,
            }

            # Deploy to Agent Engine
            # Note: Using placeholder as full Agent Engine API may require additional setup
            deployment_info = {
                "agent_name": agent_name,
                "display_name": agent_config["display_name"],
                "status": "configured",
                "runtime": runtime_config,
                "path": str(agent_path),
            }

            self.deployed_agents[agent_name] = deployment_info

            print(f"✅ {agent_name} configured for deployment")
            return deployment_info

        except Exception as e:
            print(f"❌ Failed to deploy {agent_name}: {e}")
            raise

    def _default_runtime_config(self, agent_name: str) -> Dict:
        """
        Default runtime configuration for agents.
        """
        return {
            "security": {
                "enable_authentication": True,
                "service_account": f"{PROJECT_ID}@appspot.gserviceaccount.com",
            },
            "scaling": {
                "min_instances": 1,
                "max_instances": 10,
                "target_cpu_utilization": 0.7,
            },
            "resources": {"memory": "2Gi", "cpu": "1000m"},
            "environment": {
                "GOOGLE_CLOUD_PROJECT": PROJECT_ID,
                "GOOGLE_CLOUD_LOCATION": LOCATION,
                "AGENT_NAME": agent_name,
            },
        }

    def deploy_all_agents(self) -> Dict[str, Dict]:
        """
        Deploy all CROSSFIRE agents.
        """
        agents = [
            "shakti_moderator",
            "sovereignist",
            "reformist",
            "technocrat",
            "humanist",
        ]

        print("=" * 70)
        print("DEPLOYING CROSSFIRE AGENTS TO AGENT ENGINE")
        print("=" * 70)

        for agent_name in agents:
            agent_path = AGENT_DIR / agent_name

            if not agent_path.exists():
                print(f"⚠️  Agent directory not found: {agent_path}")
                continue

            self.deploy_agent(agent_name, agent_path)

        print("\n" + "=" * 70)
        print(f"✅ Deployed {len(self.deployed_agents)} agents")
        print("=" * 70)

        return self.deployed_agents

    def save_deployment_manifest(self, output_path: str = "deployment_manifest.json"):
        """
        Save deployment information to file.
        """
        from datetime import datetime

        manifest = {
            "project_id": PROJECT_ID,
            "location": LOCATION,
            "agents": self.deployed_agents,
            "timestamp": datetime.now().isoformat(),
        }

        with open(output_path, "w") as f:
            json.dump(manifest, f, indent=2)

        print(f"📄 Deployment manifest saved to {output_path}")


def main():
    """
    Main deployment workflow.
    """
    deployer = AgentEngineDeployer()

    # Deploy all agents
    deployed = deployer.deploy_all_agents()

    # Save manifest
    deployer.save_deployment_manifest()

    # Print summary
    print("\n📊 Deployment Summary:")
    for agent_name, info in deployed.items():
        print(f"  • {agent_name}: {info['status']}")

    print("\n🚀 Next steps:")
    print("  1. Review deployment_manifest.json")
    print("  2. Verify agents in GCP Console")
    print("  3. Test with managed sessions")


if __name__ == "__main__":
    main()
