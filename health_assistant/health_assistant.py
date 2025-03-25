import sys
from agents import (
    Agent, 
    Runner, 
    ToolCallItem,
    MessageOutputItem,
    ToolCallOutputItem,
    HandoffCallItem,
    HandoffOutputItem
)
from .nutrition_agent import nutrition_agent
from .heart_health_agent import heart_health_agent

# setup agent
with open("instructions/orchestration-agent.txt", "r") as file:
    instructions = file.read()

health_assistant = Agent(
    name="Health Assistant",
    instructions=instructions,
    model="gpt-4o-mini",
    handoffs=[nutrition_agent, heart_health_agent],
)
