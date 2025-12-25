"""
Unit Tests for ADK Agents
Tests individual agent behavior and responses
"""

import sys
from pathlib import Path

import pytest

# Add agents to path
sys.path.insert(0, str(Path(__file__).parent.parent / "adk_agents"))


class TestAgentCreation:
    """Test that all agents can be created successfully"""

    def test_shakti_agent_creation(self):
        """Test Shakti moderator agent creation"""
        from shakti_moderator.agent import root_agent

        assert root_agent is not None
        assert root_agent.name == "Shakti"
        assert root_agent.model == "gemini-2.0-flash-exp"
        assert "CROSSFIRE" in root_agent.instruction

    def test_sovereignist_agent_creation(self):
        """Test Sovereignist debater creation"""
        from sovereignist.agent import root_agent

        assert root_agent is not None
        assert root_agent.name == "Sovereignist"
        assert "tradition" in root_agent.instruction.lower()

    def test_reformist_agent_creation(self):
        """Test Reformist debater creation"""
        from reformist.agent import root_agent

        assert root_agent is not None
        assert root_agent.name == "Reformist"
        assert "revolution" in root_agent.instruction.lower()

    def test_technocrat_agent_creation(self):
        """Test Technocrat debater creation"""
        from technocrat.agent import root_agent

        assert root_agent is not None
        assert root_agent.name == "Technocrat"
        assert "data" in root_agent.instruction.lower()

    def test_humanist_agent_creation(self):
        """Test Humanist debater creation"""
        from humanist.agent import root_agent

        assert root_agent is not None
        assert root_agent.name == "Humanist"
        assert "emotional" in root_agent.instruction.lower()


class TestAgentInstructions:
    """Test agent instruction quality and completeness"""

    def test_all_agents_have_instructions(self):
        """Verify all agents have non-empty instructions"""
        agents = [
            "shakti_moderator",
            "sovereignist",
            "reformist",
            "technocrat",
            "humanist",
        ]

        for agent_name in agents:
            module = __import__(f"{agent_name}.agent", fromlist=["root_agent"])
            agent = module.root_agent

            assert agent.instruction is not None
            assert len(agent.instruction) > 50, f"{agent_name} instruction too short"

    def test_debater_instructions_contain_workflow(self):
        """Verify debater agents have structured workflows"""
        debaters = ["sovereignist", "reformist", "technocrat", "humanist"]

        for agent_name in debaters:
            module = __import__(f"{agent_name}.agent", fromlist=["root_agent"])
            agent = module.root_agent

            instruction = agent.instruction.lower()
            # Check for workflow elements
            assert any(
                word in instruction
                for word in ["analyze", "workflow", "step", "respond"]
            )


class TestAgentTools:
    """Test agent tools and capabilities"""

    def test_shakti_has_tools(self):
        """Verify Shakti moderator has required tools"""
        from shakti_moderator.agent import root_agent

        assert hasattr(root_agent, "tools")
        assert root_agent.tools is not None
        assert len(root_agent.tools) > 0

        # Check for specific tools
        tool_names = [
            t.__name__ if hasattr(t, "__name__") else str(t) for t in root_agent.tools
        ]
        assert any("search" in str(name).lower() for name in tool_names)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
