import sys
from agents import (
    Agent, 
    handoff,
    Runner, 
    ToolCallItem,
    MessageOutputItem,
    ToolCallOutputItem,
    HandoffCallItem,
    HandoffOutputItem
)
from .nutrition_agent import nutrition_agent

# setup agent
with open("instructions/orchestration-agent.txt", "r") as file:
    instructions = file.read()

health_assistant = Agent(
    name="Health Assistant",
    instructions=instructions,
    model="gpt-4o-mini",
    handoffs=[nutrition_agent],
)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a prompt as a command line argument")
        sys.exit(1)
    prompt = " ".join(sys.argv[1:])
    result = Runner.run_sync(health_assistant, prompt)
    for item in result.new_items:
        print("\n" + "-"*50 + "\n")
        if isinstance(item, HandoffCallItem):
            print(f"Handoff call: {item.raw_item.name}")
        elif isinstance(item, HandoffOutputItem):
            print(f"Handoff output: {item.source_agent.name} -> {item.target_agent.name}")
        elif isinstance(item, ToolCallItem):
            print(f"Tool call: {item.raw_item.type}")
        elif isinstance(item, MessageOutputItem):
            output_text = item.raw_item.content
            for ot in output_text:
                print(f"\nMessage: {ot.text}")
        elif isinstance(item, ToolCallOutputItem):
            print(f"Tool call output: {item.output}")