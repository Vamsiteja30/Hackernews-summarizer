from praval import start_agents, get_reef
from praval_agent import hn_summary_agent

# Start the agent with initial data
start_agents(
    hn_summary_agent,
    initial_data={"type": "summary_request", "text": "Test HackerNews post"}
)

# Wait for completion
get_reef().wait_for_completion()
get_reef().shutdown()
print("Test completed!")

