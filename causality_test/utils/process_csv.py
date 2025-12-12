import sys
import pandas as pd

#!/usr/bin/env python3
"""
process_csv.py

Read 'stacked_cause_effect_evaluated_final.csv', replace 'X'->0 and 'O'->1 in the
'evaluation-2' column, and overwrite the CSV.
"""



def process_csv(path: str = "", column: str = "") -> None:
    
    try:
        df = pd.read_csv(path)
    except Exception as e:
        print(f"Error reading '{path}': {e}", file=sys.stderr)
        sys.exit(1)

    if column not in df.columns:
        print(f"Column '{column}' not found in '{path}'", file=sys.stderr)
        sys.exit(1)

    # Replace values while leaving other values unchanged
    df[column] = df[column].replace({1: 0, 2: 1, 3: 1, 4: 1})

    try:
        df.to_csv(path, index=False)
    except Exception as e:
        print(f"Error writing '{path}': {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Updated '{path}' successfully.")
