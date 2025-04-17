import os
from dotenv import load_dotenv

load_dotenv()

# --- Data File Paths ---
COMMON_FIRST_NAMES_FILE = "data/common_first_names.txt"
COMMON_LAST_NAMES_FILE = "data/common_last_names.txt"
INPUT_CSV_FILE = "data/filipino-names.csv"
OUTPUT_CSV_FILE = "output/parsed_names.csv"

# --- CSV Column Names ---
INPUT_NAME_COLUMN = "name"  # **Action Required**: Update if needed
OUTPUT_FIRST_NAME_COLUMN = "ParsedFirstName"
OUTPUT_LAST_NAME_COLUMN = "ParsedLastName"
OUTPUT_METHOD_COLUMN = "ParsingMethod"
OUTPUT_ORIGINAL_NAME_COLUMN = "OriginalName"  # Keep original name in output
OUTPUT_ERROR_COLUMN = "ErrorMessage"  # Column for errors

# --- Name Parsing Constants ---
SUFFIXES = {"Jr.", "Sr.", "III", "IV", "V", "II"}
PARTICLES = {"de", "dela", "del", "de los"}

# --- LLM Configuration ---
BATCH_SIZE = 100  # Number of names to process per API call
DEFAULT_ANTHROPIC_MODEL = "claude-3-7-sonnet-latest"
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", DEFAULT_ANTHROPIC_MODEL)
# Logic to ensure only allowed model or default is used (as before)
if ANTHROPIC_MODEL != DEFAULT_ANTHROPIC_MODEL and not os.getenv("ANTHROPIC_MODEL"):
    pass
elif (
    ANTHROPIC_MODEL != DEFAULT_ANTHROPIC_MODEL
    and os.getenv("ANTHROPIC_MODEL") != ANTHROPIC_MODEL
):
    print(
        f"Warning: Environment variable ANTHROPIC_MODEL set to unsupported value. Falling back to default: {DEFAULT_ANTHROPIC_MODEL}"
    )
    ANTHROPIC_MODEL = DEFAULT_ANTHROPIC_MODEL

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found.")

LLM_TEMPERATURE = 0.1
