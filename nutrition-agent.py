import os
from dotenv import load_dotenv
from agents import (
    Agent, 
    Runner, 
    WebSearchTool, 
    function_tool,
    ToolCallItem,
    MessageOutputItem,
    ToolCallOutputItem
)
from pyairtable import Api
import sys

# load env vars
load_dotenv()

# setup nutrition log tool
@function_tool
def write_nutrition_log(
    short_description: str,
    protein_g: float,
    sodium_mg: float,
    potassium_mg: float,
    long_description: str
) -> str:
    """
    Write nutritional information to the user's external log.
    
    This tool allows recording of nutritional information for food items into a persistent
    storage system. It captures basic nutritional metrics and descriptions of the food item.
    
    Args:
        short_description (str): A brief one-line description of the food item
        protein_g (float): Amount of protein in grams
        sodium_mg (float): Amount of sodium in milligrams
        potassium_mg (float): Amount of potassium in milligrams
        long_description (str): A detailed description of the food item with context
    
    Returns:
        str: The record ID of the created entry if successful
    
    Example:
        record_id = write_nutrition_log(
            "Chicken Salad",
            25.0,
            400.0,
            500.0,
            "Grilled chicken breast on mixed greens with light dressing"
        )
    """
    api = Api(os.getenv("AIRTABLE_PAT"))
    table = api.table(os.getenv("AIRTABLE_BASE_ID"), "nutrition_log")
    
    record = table.create({
        "short_description": short_description,
        "protein_g": protein_g,
        "sodium_mg": sodium_mg,
        "potassium_mg": potassium_mg,
        "long_description": long_description
    })
    
    return record["id"]

# setup agent
with open("instructions/nutrition-agent.txt", "r") as file:
    instructions = file.read()
agent = Agent(
    name="Nutrition Assistant", 
    instructions=instructions,
    model="gpt-4o",
    tools = [
        WebSearchTool(user_location={
                "type": "approximate",
                "country": "US",
                "region": "TN",
                "city": "Franklin" 
            }),
        write_nutrition_log
    ]
)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a prompt as a command line argument")
        sys.exit(1)
    prompt = " ".join(sys.argv[1:])
    result = Runner.run_sync(agent, prompt)
    for item in result.new_items:
        if isinstance(item, ToolCallItem):
            print(f"Tool call: {item.raw_item.type}")
        elif isinstance(item, MessageOutputItem):
            output_text = item.raw_item.content
            for ot in output_text:
                print(f"\n\nMessage: {ot.text}")
        elif isinstance(item, ToolCallOutputItem):
            print(f"Tool call output: {item.output}")
