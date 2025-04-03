import os
from agents import (
    Agent, 
    WebSearchTool, 
    function_tool,
)
from pyairtable import Api
from .instructions import nutrition_agent_instructions

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
nutrition_agent = Agent(
    name="Nutrition Agent", 
    instructions=nutrition_agent_instructions,
    model="gpt-4o",
    tools = [
        WebSearchTool(user_location={
                "type": "approximate",
                "country": "US",
                "region": "TN",
                "city": "Franklin" 
            }),
        write_nutrition_log
    ],
    handoff_description="""Determines nutritional information and logs it for the user.  
                        Any prompt mentioning food the user has eaten should be passed here."""
)
