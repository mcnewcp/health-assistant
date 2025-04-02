from agents import Agent
from .instructions import health_assistantant_instructions
from .nutrition_agent import nutrition_agent
from .heart_health_agent import heart_health_agent
from .body_agent import body_agent

# setup agent
health_assistant = Agent(
    name="Health Assistant",
    instructions=health_assistantant_instructions,
    model="gpt-4o-mini",
    handoffs=[nutrition_agent, heart_health_agent, body_agent],
)
