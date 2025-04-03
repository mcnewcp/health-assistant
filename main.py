from health_assistant import health_assistant
from agents import (
    Runner,
    HandoffCallItem,
    HandoffOutputItem,
    ToolCallItem,
    MessageOutputItem,
    ToolCallOutputItem
)
import sys
from dotenv import load_dotenv

load_dotenv()

def main(prompt):
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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a prompt as a command line argument")
        sys.exit(1)
    prompt = " ".join(sys.argv[1:])
    main(prompt)