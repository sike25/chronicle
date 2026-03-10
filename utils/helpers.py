import json
import re
from modules.shape import Date
from utils.log import setup_logging

logger = setup_logging()

def convertToDate(date_string):
   date_split = date_string.split("/")
   return Date(
       day   = int(date_split[2]),
       month = int(date_split[1]),
       year  = int(date_split[0]),
   )

def extractJson(response_text):
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
    
    if match:
        json_str = match.group(1)
    else:
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        json_str = match.group(0) if match else response_text
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"CHRONICLE_ERROR: Failed to parse JSON from LLM response: {e}")
        return None