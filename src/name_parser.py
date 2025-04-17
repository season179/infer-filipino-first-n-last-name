import json
import traceback
from typing import List, Union
from pydantic_ai import Agent, exceptions as pydantic_ai_exceptions
from pydantic_ai.models.anthropic import AnthropicModel
from src.models import BatchParseResponse, ParsedNameResult, FailedBatch
from src.config import ANTHROPIC_MODEL, LLM_TEMPERATURE, SUFFIXES, PARTICLES

# Instantiate LLM client with strict JSON-only output and configured temperature
llm_client = Agent(
    AnthropicModel(ANTHROPIC_MODEL),
    system_prompt=(
        "You are a JSON generator. Output ONLY valid JSON matching the BatchParseResponse Pydantic model. "
        "Do not include any additional text or markdown. "
        "The JSON must have a top-level 'results' key mapping to a list of objects, each with keys: "
        "original_name, first_name, last_name, parsing_method, and error_message."
    ),
    result_type=BatchParseResponse
)

def parse_name_batch(
    name_batch: List[str],
    common_first_names: set,
    common_last_names: set
) -> Union[BatchParseResponse, FailedBatch]:
    if not name_batch:
        return BatchParseResponse(results=[])

    # Prepare JSON strings for prompt
    name_list_json = json.dumps(name_batch, ensure_ascii=False)
    suffix_list_json = json.dumps(list(SUFFIXES), ensure_ascii=False)
    particle_list_json = json.dumps(list(PARTICLES), ensure_ascii=False)
    common_first_names_json = json.dumps(list(common_first_names), ensure_ascii=False)
    common_last_names_json = json.dumps(list(common_last_names), ensure_ascii=False)

    prompt = (
        f"Goal: Parse each of the following Filipino names into first_name and last_name:\n"
        f"{name_list_json}\n\n"
        f"Context: These are Filipino names.\n"
        f"Rules (in priority order):\n"
        f"1. Suffixes: {suffix_list_json}\n"
        f"2. Common Last Names: {common_last_names_json}\n"
        f"3. Common First Names: {common_first_names_json}\n"
        f"4. Particles: {particle_list_json}\n\n"
        f"Important: For every name in the input list, include exactly one result in the 'results' array in the original order; if parsing fails for a name, populate its error_message field.\n\n"
        f"Return a JSON object matching the BatchParseResponse model:\n"
        f"{'{'}\"results\": [\n"
        f"  { '{'}\n"
        f"    \"original_name\": \"<original name>\",\n"
        f"    \"first_name\": \"<first name>\",\n"
        f"    \"last_name\": \"<last name>\",\n"
        f"    \"parsing_method\": \"<method>\",\n"
        f"    \"error_message\": null\n"
        f"  { '}' }\n"
        f"]}}\n"
    )

    try:
        # Call LLM agent
        result = llm_client.run_sync(prompt)
        response: BatchParseResponse = result.data
        if len(response.results) != len(name_batch):
            msg = (
                f"Batch size mismatch: sent {len(name_batch)} names, "
                f"received {len(response.results)} results"
            )
            print(msg)
            return FailedBatch(batch_input_names=name_batch, error_message=msg)
        return response
    except Exception as e:
        error_msg = f"LLM call failed: {e}"
        # Specifically handle the case where the model's output structure was invalid
        if isinstance(e, pydantic_ai_exceptions.UnexpectedModelBehavior):
            error_msg = f"LLM failed to generate valid JSON structure: {e}"
        return FailedBatch(batch_input_names=name_batch, error_message=error_msg)