"""
Direct ADK Agent Test
Tests if ADK agents can generate real responses
"""

import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
    "/Users/sargupta/AIPodcast/service-account-key.json"
)

sys.path.insert(0, str(Path(__file__).parent.parent / "adk_agents"))  # noqa: E402

from google.adk.agents.llm_agent import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# Create a simple test agent
agent = Agent(
    model="gemini-2.0-flash-exp",
    name="TestBot",
    description="A test agent",
    instruction="You are a friendly AI. Give very short, enthusiastic responses under 10 words.",
)

print("Testing ADK Agent...")
print("=" * 60)

try:
    # Create session service
    session_service = InMemorySessionService()

    # Create runner
    runner = Runner(agent=agent, session_service=session_service)

    # Run the agent
    print("Calling agent with: 'Say hello!'")
    result = runner.run(user_message="Say hello!")

    print(f"\nResult type: {type(result)}")
    print(
        f"Result attributes: {[attr for attr in dir(result) if not attr.startswith('_')][:15]}"
    )

    # Try to extract text
    if hasattr(result, "response_message"):
        resp_msg = result.response_message
        print(f"\nResponse Message type: {type(resp_msg)}")
        print(
            f"Response Message attrs: {[attr for attr in dir(resp_msg) if not attr.startswith('_')][:15]}"
        )

        if hasattr(resp_msg, "content"):
            content = resp_msg.content
            print(f"\nContent type: {type(content)}")
            if isinstance(content, list) and len(content) > 0:
                print(f"First part type: {type(content[0])}")
                first_part = content[0]
                if hasattr(first_part, "text"):
                    print(f"\n✅ SUCCESS! Agent responded: '{first_part.text}'")
                else:
                    print(f"First part: {first_part}")

    print(f"\nFull result: {result}")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 60)
