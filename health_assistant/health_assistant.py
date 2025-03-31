from agents import Agent
from .nutrition_agent import nutrition_agent
from .heart_health_agent import heart_health_agent
from .body_agent import body_agent

# setup agent
with open("instructions/orchestration-agent.txt", "r") as file:
    instructions = file.read()

health_assistant = Agent(
    name="Health Assistant",
    instructions=instructions,
    model="gpt-4o-mini",
    handoffs=[nutrition_agent, heart_health_agent, body_agent],
)
