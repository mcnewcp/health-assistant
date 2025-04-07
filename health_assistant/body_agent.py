import os
from agents import Agent, function_tool
from pyairtable import Api
from .instructions import body_agent_instructions

# setup body data log tool
@function_tool
def write_body_log(
    weight_lb: float,
    smm_lb: float,
    pbf: float,
    ecw_tbw: float
) -> str:
    """
    Write body composition information to the user's external log.
    
    This tool allows recording of body composition metrics for the user into a persistent
    storage system. It captures 4 metrics - weight, skeletal muscle mass, body fat percentage, and ECW/TBW ratio.
    
    Args:
        weight_lb (float): Body weight in lbs
        smm_lb (float): Skeletal muscle mass in lbs
        pbf (float): Body fat percentage in decimal format, e.g. 0.25 for 25%
        ecw_tbw (float): Extracellular water to total body water ratio in decimal format, e.g. 0.4 for 40%
    
    Returns:
        str: The record ID of the created entry if successful
    
    Example:
        record_id = write_body_log(169.7, 82.5, 0.150, 0.365)
    """
    api = Api(os.getenv("AIRTABLE_PAT"))
    table = api.table(os.getenv("AIRTABLE_BASE_ID"), "body_log")
    
    record = table.create({
        "weight_lb": weight_lb,
        "smm_lb": smm_lb,
        "pbf": pbf,
        "ecw_tbw": ecw_tbw
    })
    
    return record["id"]

# setup agent
body_agent = Agent(
    name="Body Composition Agent", 
    instructions=body_agent_instructions,
    model="gpt-4o-mini",
    tools = [
        write_body_log
    ],
    handoff_description="""Parses body composition information and logs it for the user.  
                        Any prompt mentioning body composition metrics should be passed here."""
)
