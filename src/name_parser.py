import json
import traceback
from typing import List, Union
from pydantic_ai import PydanticAI
from src.models import BatchParseResponse, ParsedNameResult, FailedBatch
from src.config import ANTHROPIC_MODEL, LLM_TEMPERATURE, SUFFIXES, PARTICLES

# Instantiate PydanticAI client
llm_client = PydanticAI(model=ANTHROPIC_MODEL, temperature=LLM_TEMPERATURE)

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
        response: BatchParseResponse = llm_client(
            output_model=BatchParseResponse,
            text=prompt
        )
        if len(response.results) != len(name_batch):
            msg = (
                f"Batch size mismatch: sent {len(name_batch)} names, "
                f"received {len(response.results)} results"
            )
            print(msg)
            return FailedBatch(batch_input_names=name_batch, error_message=msg)
        return response
    except Exception as e:
        traceback.print_exc()
        return FailedBatch(batch_input_names=name_batch, error_message=str(e))