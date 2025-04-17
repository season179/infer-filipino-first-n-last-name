import os
import pandas as pd
from tqdm import tqdm

import src.config as config
from src.data_loader import load_names_from_file, load_input_csv
from src.name_parser import parse_name_batch
from src.models import BatchParseResponse, FailedBatch


def main():
    # Load common name lists
    common_first_names = load_names_from_file(config.COMMON_FIRST_NAMES_FILE)
    common_last_names = load_names_from_file(config.COMMON_LAST_NAMES_FILE)

    # Load input CSV
    df = load_input_csv(config.INPUT_CSV_FILE, config.INPUT_NAME_COLUMN)

    # Ensure output directory exists
    output_dir = os.path.dirname(config.OUTPUT_CSV_FILE)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    results_list = []

    # Create batches
    all_names = df[config.INPUT_NAME_COLUMN].tolist()
    name_batches = [all_names[i:i + config.BATCH_SIZE] for i in range(0, len(all_names), config.BATCH_SIZE)]

    # Process each batch
    for batch in tqdm(name_batches, desc="Processing Batches"):
        response = parse_name_batch(batch, common_first_names, common_last_names)
        if isinstance(response, BatchParseResponse):
            for result in response.results:
                results_list.append(result.to_dict())
        elif isinstance(response, FailedBatch):
            results_list.extend(response.generate_failed_results())
        else:
            # Unexpected response type
            for name in batch:
                results_list.append({
                    config.OUTPUT_ORIGINAL_NAME_COLUMN: name,
                    config.OUTPUT_FIRST_NAME_COLUMN: None,
                    config.OUTPUT_LAST_NAME_COLUMN: None,
                    config.OUTPUT_METHOD_COLUMN: None,
                    config.OUTPUT_ERROR_COLUMN: "Unknown response type"
                })

    # Consolidate results into DataFrame
    results_df = pd.DataFrame(results_list)

    # Merge with original data
    df_renamed = df.rename(columns={config.INPUT_NAME_COLUMN: config.OUTPUT_ORIGINAL_NAME_COLUMN})
    final_df = pd.merge(df_renamed, results_df, on=config.OUTPUT_ORIGINAL_NAME_COLUMN, how="left")

    # Select and order columns
    cols = list(df_renamed.columns) + [
        config.OUTPUT_FIRST_NAME_COLUMN,
        config.OUTPUT_LAST_NAME_COLUMN,
        config.OUTPUT_METHOD_COLUMN,
        config.OUTPUT_ERROR_COLUMN,
    ]
    final_df = final_df[cols]

    # Write to CSV
    final_df.to_csv(config.OUTPUT_CSV_FILE, index=False)
    print(f"Parsed names written to {config.OUTPUT_CSV_FILE}")


if __name__ == "__main__":
    main()