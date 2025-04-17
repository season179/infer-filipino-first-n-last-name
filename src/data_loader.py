import pandas as pd

def load_names_from_file(filepath: str) -> set[str]:
    """Load names from a text file, one per line, ignoring empty lines."""
    names: set[str] = set()
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            name = line.strip()
            if name:
                names.add(name)
    return names

def load_input_csv(filepath: str, name_column: str) -> pd.DataFrame:
    """Load an input CSV into a DataFrame and verify the given column exists."""
    df = pd.read_csv(filepath)
    if name_column not in df.columns:
        raise ValueError(f"Column '{name_column}' not found in input CSV.")
    return df