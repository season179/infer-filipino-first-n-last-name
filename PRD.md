Product Requirements Document: Filipino Name Parser (Batch Processing)
Version: 1.0
Date: April 16, 2025
Status: Proposed

1. Overview
This document outlines the requirements for the Filipino Name Parser, a Python application designed to automatically parse full Filipino names from a CSV file into their constituent First Name(s) and Last Name components. The parsing logic will leverage the Anthropic Claude Large Language Model (LLM) accessed via the PydanticAI framework, incorporating predefined lists of common names, suffixes, and particles to guide the LLM. Processing will occur in batches to enhance efficiency compared to single-name processing. The output will be a new CSV file containing the original data augmented with the parsed name components.

2. Goals
To accurately parse a list of Filipino full names from a CSV file into First Name(s) and Last Name components.

To utilize the specified Anthropic Claude LLM (claude-3-5-sonnet-20240620 or environment override) for the core parsing intelligence.

To improve processing efficiency by sending names to the LLM in configurable batches.

To provide structured output in CSV format, including original data and parsed components.

To implement the solution using the specified technical stack (Python 3.11, Poetry, Pandas, PydanticAI, etc.).

To ensure configuration (file paths, column names, batch size, API keys) is manageable.

3. Non-Goals
Providing a graphical user interface (GUI). This is a command-line/script-based tool.

Implementing automated testing frameworks. Testing will be performed manually.

Supporting input formats other than CSV.

Supporting output formats other than CSV.

Implementing name parsing logic without relying on the specified LLM.

Supporting LLM providers other than Anthropic or models other than the configured Claude model.

Achieving 100% parsing accuracy (LLM output may have limitations).

Real-time processing. This is designed for batch processing of existing files.

4. User Stories
As a Data Analyst, I want to process a CSV file containing Filipino names to automatically split them into first and last name columns, so that I can standardize the dataset for reporting and analysis.

As a Developer, I want a script that efficiently handles potentially large lists of names by using batch API calls, so that processing time and cost are optimized.

5. Functional Requirements
5.1. Input Processing
* FR1.1: The application MUST read data from an input CSV file specified in the configuration (`config.INPUT_CSV_FILE`).
* FR1.2: The application MUST identify the column containing the full names based on a configurable column name (`config.INPUT_NAME_COLUMN`).
* FR1.3: The application MUST load lists of common Filipino first names from a text file (`config.COMMON_FIRST_NAMES_FILE`).
* FR1.4: The application MUST load lists of common Filipino last names from a text file (`config.COMMON_LAST_NAMES_FILE`).
* FR1.5: The application MUST handle potential errors during file loading (e.g., File Not Found, incorrect CSV format, missing specified column).

5.2. Name Parsing (Batch Processing)
* FR2.1: The application MUST group the input names into batches of a configurable size (`config.BATCH_SIZE`).
* FR2.2: For each batch, the application MUST construct a prompt for the configured Anthropic Claude LLM (`config.ANTHROPIC_MODEL`).
* FR2.3: The prompt MUST include:
    * The list of names in the current batch.
    * Instructions to parse each name into First Name(s) and Last Name.
    * Contextual information (e.g., "These are Filipino names").
    * Prioritized parsing rules/heuristics (leveraging suffixes, particles, common first/last name lists).
    * The loaded lists of common first names, last names, suffixes (`config.SUFFIXES`), and particles (`config.PARTICLES`).
    * Instructions to return a structured response (JSON) containing a result for *each* name in the input batch, in the original order.
* FR2.4: The application MUST call the Anthropic API via the PydanticAI client, requesting output structured according to the `BatchParseResponse` Pydantic model.
* FR2.5: The application MUST handle the LLM's response:
    * Parse the structured list of results (`ParsedNameResult`).
    * For each result, extract the `first_name`, `last_name`, `original_name`, `parsing_method`, and any `error_message`.
* FR2.6: The application MUST handle errors during API calls:
    * Detect and log failures affecting an entire batch call.
    * Record failures indicated by the LLM for individual names within a batch (via the `error_message` field).
    * Ensure that a result (even if indicating failure) is recorded for every name sent in a batch.

5.3. Output Generation
* FR3.1: The application MUST consolidate the parsing results for all batches.
* FR3.2: The application MUST merge the parsing results with the original input data, aligning based on the original full name or input row index.
* FR3.3: The application MUST write the final results to an output CSV file specified in the configuration (`config.OUTPUT_CSV_FILE`).
* FR3.4: The output CSV MUST contain all original columns from the input CSV plus the following new columns (names defined in config):
    * Parsed First Name (`config.OUTPUT_FIRST_NAME_COLUMN`)
    * Parsed Last Name (`config.OUTPUT_LAST_NAME_COLUMN`)
    * Original Name (`config.OUTPUT_ORIGINAL_NAME_COLUMN`) - For reference/joining
    * Parsing Method (`config.OUTPUT_METHOD_COLUMN`) - Heuristic indicating how parsing was likely done.
    * Error Message (`config.OUTPUT_ERROR_COLUMN`) - Populated if parsing failed for that name.

5.4. Configuration
* FR4.1: The application MUST load the Anthropic API key securely from an environment variable (`ANTHROPIC_API_KEY`) defined in a `.env` file.
* FR4.2: The application MUST use the Anthropic model specified in the `ANTHROPIC_MODEL` environment variable, falling back to `config.DEFAULT_ANTHROPIC_MODEL` if the variable is not set. No other models should be used.
* FR4.3: File paths, column names, batch size, and LLM temperature MUST be configurable via `src/config.py`.

6. Non-Functional Requirements
NFR1 (Efficiency): The application should process names significantly faster than a one-by-one API call approach by using batching. Progress indication (e.g., via tqdm) should be provided during batch processing.

NFR2 (Reliability): The application should gracefully handle common errors (file I/O, API errors, data format issues) and log them appropriately. It should aim to process as many names as possible even if some fail.

NFR3 (Maintainability): The code should follow standard Python conventions, be well-commented, and organized into logical modules (data_loader, name_parser, models, config, main).

NFR4 (Security): API keys must not be hardcoded and should be loaded securely from the environment.

7. Data Requirements
Input Data:

Primary Input: CSV file (config.INPUT_CSV_FILE) with at least one column containing full Filipino names (config.INPUT_NAME_COLUMN). Encoding assumed to be UTF-8 unless specified otherwise.

Supporting Input: Text files (config.COMMON_FIRST_NAMES_FILE, config.COMMON_LAST_NAMES_FILE) containing one common name per line (UTF-8).

Output Data:

CSV file (config.OUTPUT_CSV_FILE, UTF-8) containing all original columns plus the new parsed name columns as specified in FR3.4.

Configuration Data:

Constants defined in src/config.py.

Environment variables defined in .env (ANTHROPIC_API_KEY, optionally ANTHROPIC_MODEL).

8. Technical Stack
Programming Language: Python 3.11

Package Management: Poetry

Core Libraries: Pandas (CSV I/O, DataFrames), PydanticAI (LLM interaction, data validation), LiteLLM (LLM provider interface), python-dotenv (environment variables), Anthropic Python SDK (dependency for LiteLLM).

LLM: Anthropic Claude (claude-3-5-sonnet-20240620 or as specified by ANTHROPIC_MODEL env var).

Optional: tqdm (for progress bars).

9. Future Considerations / Open Questions
How to handle extremely large common name lists efficiently within prompts?

Strategy for retrying failed batches or individual items within batches.

Potential for using asynchronous processing (asyncio) to make concurrent batch API calls for further speedup.

How will the quality/coverage of the common name lists be maintained?

Could statistical analysis of the input dataset supplement the LLM's parsing?

10. Success Metrics
SM1 (Completion): The application successfully processes the entire input CSV and generates the output CSV file without crashing.

SM2 (Accuracy - Manual Eval): A manually reviewed sample of the output shows a high percentage (e.g., >85-90%, target TBD) of names correctly parsed into First Name(s) and Last Name components.

SM3 (Error Handling): Errors encountered during processing (API issues, file issues, parsing failures) are appropriately logged or indicated in the output file's ErrorMessage column.

SM4 (Efficiency): Processing time for a benchmark dataset is significantly less than an estimated one-by-one processing time.