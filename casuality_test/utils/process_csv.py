import sys
import pandas as pd

#!/usr/bin/env python3
"""
process_csv.py

Read 'stacked_cause_effect_evaluated_final.csv', replace 'X'->0 and 'O'->1 in the
'evaluation-2' column, and overwrite the CSV.
"""


DEFAULT_PATH = ""
COLUMN = "evaluation-3"

def main(path: str = DEFAULT_PATH) -> None:
    try:
        df = pd.read_csv(path)
    except Exception as e:
        print(f"Error reading '{path}': {e}", file=sys.stderr)
        sys.exit(1)

    if COLUMN not in df.columns:
        print(f"Column '{COLUMN}' not found in '{path}'", file=sys.stderr)
        sys.exit(1)

    # Replace values while leaving other values unchanged
    df[COLUMN] = df[COLUMN].replace({1: 0, 2: 1, 3: 1, 4: 1})

    try:
        df.to_csv(path, index=False)
    except Exception as e:
        print(f"Error writing '{path}': {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Updated '{path}' successfully.")

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH
    main(arg)
