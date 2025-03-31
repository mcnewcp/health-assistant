import os
from agents import Agent, function_tool
from pyairtable import Api

# setup heart health log tool
@function_tool
def write_heart_log(
    systolic: int,
    diastolic: int,
    rate: int,
) -> str:
    """
    Write heart health information to the user's external log.
    
    This tool allows recording of heart health metrics for the user into a persistent
    storage system. It captures basic metrics, including blood pressure and heart rate.
    
    Args:
        systolic (int): Systolic blood pressure in mmHg
        diastolic (int): Diastolic blood pressure in mmHg
        rate (int): Heart rate in bpm
    
    Returns:
        str: The record ID of the created entry if successful
    
    Example:
        record_id = write_heart_log(124, 79, 65)
    """
    api = Api(os.getenv("AIRTABLE_PAT"))
    table = api.table(os.getenv("AIRTABLE_BASE_ID"), "heart_log")
    
    record = table.create({
        "systolic_mmhg": systolic,
        "diastolic_mmhg": diastolic,
        "rate_bpm": rate,
    })
    
    return record["id"]

# setup agent
with open("instructions/heart-health-agent.txt", "r") as file:
    instructions = file.read()
heart_health_agent = Agent(
    name="Heart Health Agent", 
    instructions=instructions,
    model="gpt-4o-mini",
    tools = [
        write_heart_log
    ],
    handoff_description="""Parses hearth health information and logs it for the user.  
                        Any prompt mentioning heart health metrics should be passed here."""
)
