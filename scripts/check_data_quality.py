#!/usr/bin/env python3
"""Check data quality of synthetic files."""

import pandas as pd
from pathlib import Path

studies = {
    "61405445-01": "data/synthetic/kantar/61405445-01/US/synthetic_US_50resp_20260114_201915.xlsx",
    "61407017": "data/synthetic/kantar/61407017/US/synthetic_US_50resp_20260114_201237.xlsx",
    "61407069": "data/synthetic/kantar/61407069/US/synthetic_US_50resp_20260114_194109.xlsx",
    "61407185": "data/synthetic/kantar/61407185/US/synthetic_US_50resp_20260114_200931.xlsx"
}

for study_id, file_path in studies.items():
    print(f"\n{'='*60}")
    print(f"Study: {study_id}")
    print(f"{'='*60}")

    try:
        df = pd.read_excel(file_path)

        print(f"Respondents: {len(df)}")
        print(f"Total columns: {len(df.columns)}")

        # Identify question columns
        question_cols = [c for c in df.columns if '(' in c and ')' in c]
        print(f"Question columns: {len(question_cols)}")

        # Check which have data
        questions_with_data = []
        for col in question_cols:
            if df[col].notna().sum() > 0:
                questions_with_data.append(col)

        print(f"Questions with data: {len(questions_with_data)}")
        print(f"Questions empty: {len(question_cols) - len(questions_with_data)}")

        if questions_with_data:
            print(f"\nSample questions with data:")
            for col in questions_with_data[:5]:
                non_null = df[col].notna().sum()
                unique_vals = df[col].dropna().nunique()
                print(f"  {col[:60]}... ({non_null} responses, {unique_vals} unique values)")

    except Exception as e:
        print(f"ERROR: {e}")
