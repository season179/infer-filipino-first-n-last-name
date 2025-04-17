# Project Goal: Create a Python program that reads Filipino full names from a CSV file, parses them in batches into first name(s) and last name using the Anthropic Claude LLM via PydanticAI with predefined lists/rules, and outputs the results to a new CSV file.

# Tech Stack: Python 3.11, Poetry, PydanticAI, LiteLLM, Pandas, python-dotenv, Anthropic API.

# Phase 1: Project Setup and Configuration

- [X] Task 1.1: Initialize Project Environment

- [X] Subtask 1.1.1: Ensure Python 3.11 is installed and selected.

- [X] Subtask 1.1.3: Navigate to the project directory.


- [X] Task 1.2: Add Dependencies

- [X] Subtask 1.2.1: Add necessary libraries:

```bash
pip install pydantic-ai litellm pydantic python-dotenv anthropic pandas tqdm
```

(Added tqdm for progress bars, helpful for batch processing)

- [X] Task 1.3: Configure Environment Variables

- [X] Subtask 1.3.1: Create .env file.

- [X] Subtask 1.3.2: Add ANTHROPIC_API_KEY and optionally ANTHROPIC_MODEL to .env.

- [X] Subtask 1.3.3: Create .gitignore and add relevant entries.

- [X] Task 1.4: Set Up Project Structure

- [X] Subtask 1.4.1: Create directories: mkdir src data output.

- [X] Subtask 1.4.2: Create initial Python files: touch src/main.py src/config.py src/models.py src/data_loader.py src/name_parser.py.

- [X] Task 1.5: Define Configuration

- [X] Subtask 1.5.1: In src/config.py, define constants, including BATCH_SIZE:

# src/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# --- Data File Paths ---
COMMON_FIRST_NAMES_FILE = "data/common_first_names.txt"
COMMON_LAST_NAMES_FILE = "data/common_last_names.txt"
INPUT_CSV_FILE = "data/input_names.csv"
OUTPUT_CSV_FILE = "output/parsed_names.csv"

# --- CSV Column Names ---
INPUT_NAME_COLUMN = "FullName" # **Action Required**: Update if needed
OUTPUT_FIRST_NAME_COLUMN = "ParsedFirstName"
OUTPUT_LAST_NAME_COLUMN = "ParsedLastName"
OUTPUT_METHOD_COLUMN = "ParsingMethod"
OUTPUT_ORIGINAL_NAME_COLUMN = "OriginalName" # Keep original name in output
OUTPUT_ERROR_COLUMN = "ErrorMessage" # Column for errors

# --- Name Parsing Constants ---
SUFFIXES = {"Jr.", "Sr.", "III", "IV", "V", "II"}
PARTICLES = {"de", "dela", "del", "de los"}

# --- LLM Configuration ---
BATCH_SIZE = 100 # Number of names to process per API call
DEFAULT_ANTHROPIC_MODEL = "claude-3-5-sonnet-20240620"
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", DEFAULT_ANTHROPIC_MODEL)
# Logic to ensure only allowed model or default is used (as before)
if ANTHROPIC_MODEL != DEFAULT_ANTHROPIC_MODEL and not os.getenv("ANTHROPIC_MODEL"):
     pass
elif ANTHROPIC_MODEL != DEFAULT_ANTHROPIC_MODEL and os.getenv("ANTHROPIC_MODEL") != ANTHROPIC_MODEL:
     print(f"Warning: Environment variable ANTHROPIC_MODEL set to unsupported value. Falling back to default: {DEFAULT_ANTHROPIC_MODEL}")
     ANTHROPIC_MODEL = DEFAULT_ANTHROPIC_MODEL

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found.")

LLM_TEMPERATURE = 0.1

- [x] Subtask 1.5.2: Action Required: Update INPUT_NAME_COLUMN if needed.

Phase 2: Data Preparation

- [x] Task 2.1: Gather and Prepare Data Lists

- [x] Subtask 2.1.1: Action Required: Populate data/common_first_names.txt and data/common_last_names.txt.

- [X] Subtask 2.1.2: Ensure data/input_names.csv exists with the correct column name.

- [x] Task 2.2: Implement Data Loading

- [x] Subtask 2.2.1: In src/data_loader.py:

Implement load_names_from_file(filepath: str) -> set[str].

Implement load_input_csv(filepath: str, name_column: str) -> pd.DataFrame.

Phase 3: Define Output Structure (for Batching)

- [X] Task 3.1: Create Pydantic Models for Batch Response

- [X] Subtask 3.1.1: In src/models.py, define models to handle a list of results per API call:

# src/models.py
from pydantic import BaseModel, Field
from typing import List, Any, Union # Import List and Union

# Model for a single parsed name (can include errors)
class ParsedNameResult(BaseModel):
    first_name: str | None = Field(default=None, description="Identified first name(s).")
    last_name: str | None = Field(default=None, description="Identified last name(s).")
    parsing_method: str = Field(default="Unknown", description="Primary logic used by LLM.")
    original_name: str = Field(..., description="Original input name string.")
    error_message: str | None = Field(default=None, description="Error message if parsing failed for this specific name.")

    # Helper to convert to dict for DataFrame
    def to_dict(self) -> dict[str, Any]:
        return {
            "ParsedFirstName": self.first_name,
            "ParsedLastName": self.last_name,
            "ParsingMethod": self.parsing_method,
            "OriginalName": self.original_name, # Keep original name
            "ErrorMessage": self.error_message
        }

# Model representing the entire response for a batch
class BatchParseResponse(BaseModel):
    results: List[ParsedNameResult] = Field(..., description="A list containing a parse result for each name in the input batch.")

# Model for representing a failure of the entire batch call
class FailedBatch(BaseModel):
     batch_input_names: List[str]
     error_message: str = "Processing failed for the entire batch."
     results: List[ParsedNameResult] = [] # Empty results list for consistency

     # Helper method to generate failed results for all inputs in the batch
     def generate_failed_results(self) -> List[dict[str, Any]]:
          failed_list = []
          for name in self.batch_input_names:
               failed_item = ParsedNameResult(
                    original_name=name,
                    error_message=self.error_message,
                    parsing_method="Batch Failed"
               )
               failed_list.append(failed_item.to_dict())
          return failed_list


- [X] Subtask 3.1.2: Ensure ParsedNameResult includes original_name and error_message. The BatchParseResponse expects a list of these results. Added FailedBatch model for catastrophic batch failures.

Phase 4: Implement Core Parsing Logic (Batching)

- [ ] Task 4.1: Configure LLM and PydanticAI

- [ ] Subtask 4.1.1: In src/name_parser.py, import necessary modules (PydanticAI, BatchParseResponse, ParsedNameResult, FailedBatch, config, List, traceback).

- [ ] Subtask 4.1.2: Instantiate the PydanticAI client as before, using config.ANTHROPIC_MODEL and config.LLM_TEMPERATURE.

- [ ] Task 4.2: Develop the Batch LLM Prompt

- [ ] Subtask 4.2.1: Major Change: Craft a new prompt template string designed for batch processing.

- [ ] Subtask 4.2.2: The prompt must:

Clearly state the goal: Parse each name in the provided list [LIST_OF_NAMES] into first_name and last_name.

Provide the context ("Filipino names") and the prioritized rules (Suffixes, Last Names, First Names, Particles) as before, applying them to each name.

Include the data lists ([SUFFIX_LIST], [LAST_NAME_LIST], etc.).

Crucially: Instruct the LLM to return a JSON object matching the BatchParseResponse model, containing a results list. This list must have one entry (a ParsedNameResult object) for each name in the input [LIST_OF_NAMES], in the same order. If parsing fails for a specific name, it should still return an entry for it, populating the error_message field within its ParsedNameResult object.

Use placeholders for [LIST_OF_NAMES] and the data lists/constants.

- [ ] Task 4.3: Create Batch Parsing Function

- [ ] Subtask 4.3.1: Major Change: Define parse_name_batch(name_batch: List[str], common_first_names: set, common_last_names: set) -> Union[BatchParseResponse, FailedBatch]: in src/name_parser.py.

- [ ] Subtask 4.3.2: Inside the function:

Handle empty name_batch input.

Format the batch prompt string, inserting the name_batch (e.g., as a numbered list or JSON list string) and other data.

Wrap the llm_client call in a try...except block.

Call PydanticAI expecting the BatchParseResponse model: response: BatchParseResponse = llm_client(output_model=BatchParseResponse, text=formatted_batch_prompt).

Error Handling:

If the entire API call fails (exception), log the error and return an instance of FailedBatch(batch_input_names=name_batch, error_message=str(e)).

If the call succeeds but the returned response.results list doesn't match the length of the input name_batch, log this inconsistency and potentially return a FailedBatch or attempt to salvage partial results (more complex).

Return the successful BatchParseResponse object.

Phase 5: Main Execution Flow (Batching)

- [ ] Task 5.1: Implement Main Script Logic (Batching)

- [ ] Subtask 5.1.1: In src/main.py:

Import necessary functions/classes/config (load_names_from_file, load_input_csv, parse_name_batch, config, pd, BatchParseResponse, FailedBatch, tqdm).

Load common name sets and the input DataFrame.

Initialize results_list = [].

Major Change: Create batches from the input DataFrame's name column:

Get the list of names: all_names = df[config.INPUT_NAME_COLUMN].tolist().

Generate batches: name_batches = [all_names[i:i + config.BATCH_SIZE] for i in range(0, len(all_names), config.BATCH_SIZE)].

Iterate through name_batches (use tqdm for progress bar: for batch in tqdm(name_batches, desc="Processing Batches")).

Inside the loop, call response = parse_name_batch(batch, common_first_names, common_last_names).

Check the type of response:

If isinstance(response, BatchParseResponse): Iterate through response.results, convert each ParsedNameResult to a dictionary using to_dict(), and append to results_list.

If isinstance(response, FailedBatch): Use response.generate_failed_results() to get a list of dictionaries representing failures for that batch, and extend results_list with these.

Include logging for batch success/failure.

- [ ] Task 5.2: Combine Results and Output CSV

- [ ] Subtask 5.2.1: After processing all batches, create results_df = pd.DataFrame(results_list).

- [ ] Subtask 5.2.2: Important: Merge results_df with the original input DataFrame (df). Since results might be out of order or include failures, merge reliably using the OriginalName column (assuming original names are unique enough identifiers within the dataset) or by preserving and using the original DataFrame index if possible.

# Example using original name as merge key:
# Ensure OriginalName column exists in both df (as INPUT_NAME_COLUMN) and results_df
# Rename input column in original df for clarity if needed before merge
df_renamed = df.rename(columns={config.INPUT_NAME_COLUMN: "OriginalName"})
final_df = pd.merge(df_renamed, results_df, on="OriginalName", how="left")

Adjust merge strategy if original names aren't unique or if using index is preferred.

- [ ] Subtask 5.2.3: Select and order columns for the final output CSV (original columns + new columns like config.OUTPUT_FIRST_NAME_COLUMN, config.OUTPUT_LAST_NAME_COLUMN, config.OUTPUT_METHOD_COLUMN, config.OUTPUT_ERROR_COLUMN).

- [ ] Subtask 5.2.4: Save final_df to CSV using final_df.to_csv(config.OUTPUT_CSV_FILE, index=False). Ensure the output/ directory exists.