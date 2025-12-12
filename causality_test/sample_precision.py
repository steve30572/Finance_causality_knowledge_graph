import sys
from pathlib import Path
import pandas as pd
import numpy as np

#!/usr/bin/env python3
"""
sample_and_precision.py

- Loads 'stacked_cause_effect_evaluated_final.csv' (same directory).
- Keeps only columns that start with 'evaluation'.
- Repeats 10 times:
    - Samples 1000 rows (with replacement if file has <1000 rows).
    - Computes proportion of entries equal to 1 among sampled rows.
- Prints the 10 ratios and their mean and standard deviation.
"""


file_path = ""
CSV_PATH = Path(file_path)
SAMPLE_N = 1000
REPEATS = 10

def main():
    if not CSV_PATH.exists():
        print(f"Error: file not found: {CSV_PATH}", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(CSV_PATH)
    eval_cols = [c for c in df.columns if str(c).startswith("evaluation")]
    if not eval_cols:
        print("Error: no columns starting with 'evaluation' found.", file=sys.stderr)
        sys.exit(1)

    eval_df = df[eval_cols].apply(pd.to_numeric, errors="coerce")
    n_rows = len(eval_df)
    replace = n_rows < SAMPLE_N

    ratios = []
    for i in range(REPEATS):
        sample_df = eval_df.sample(n=SAMPLE_N, replace=replace)
        ones = (sample_df == 1).sum().sum()
        total = sample_df.size
        ratio = ones / total if total > 0 else float("nan")
        ratios.append(ratio)

    ratios = np.array(ratios, dtype=float)
    mean = np.nanmean(ratios)
    std = np.nanstd(ratios, ddof=0)

    print("ratios (each run):")
    for r in ratios:
        print(f"{r:.6f}")
    print(f"\nprecision: {mean:.6f}")
    # print(f"std:  {std:.6f}")

if __name__ == "__main__":
    main()
