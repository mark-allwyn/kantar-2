"""
Simple script to examine LLM responses from synthetic data
"""

import pandas as pd
import numpy as np

# Load synthetic data
synthetic_path = "data/synthetic/synthetic_data_100resp_20251218_170726.xlsx"
print(f"Loading: {synthetic_path}\n")
df = pd.read_excel(synthetic_path)

print(f"✓ Loaded {len(df)} respondents")
print(f"✓ Columns: {df.shape[1]}\n")

# Questions to analyze
QUESTIONS = {
    'B2': 'Purchase Intent',
    'B4': 'Value for Money',
    'B7': 'Likeability',
    'B8': 'Relevance',
    'B9': 'Excitement',
    'B11': 'Believability',
    'B13': 'Uniqueness',
}

print("="*80)
print("SAMPLE RESPONSES BY QUESTION")
print("="*80)

for q_code, q_name in QUESTIONS.items():
    print(f"\n{'='*80}")
    print(f"{q_name} ({q_code})")
    print(f"{'='*80}")

    # Find response and score columns
    response_cols = [col for col in df.columns if col.startswith(f'{q_code}_') and '_response' in col]
    score_cols = [col for col in df.columns if col.startswith(f'{q_code}_') and '_score' in col]

    if not response_cols:
        print(f"⚠ No response columns found")
        continue

    print(f"\n✓ Found {len(response_cols)} concepts")

    # Collect responses and scores for first concept
    first_concept_resp = response_cols[0]
    first_concept_score = score_cols[0]

    responses = df[first_concept_resp].dropna()
    scores = df[first_concept_score].dropna()

    print(f"\n✓ Analyzing concept: {first_concept_resp.split('_')[1]}")
    print(f"✓ Total responses: {len(responses)}")
    print(f"✓ Mean score: {scores.mean():.2f}")
    print(f"✓ Score distribution: {dict(scores.value_counts().sort_index())}")

    # Show sample responses by score
    print(f"\nSAMPLE RESPONSES:")
    print(f"{'─'*80}")

    for score_level in [1, 2, 3, 4, 5]:
        score_mask = scores == score_level
        score_responses = responses[score_mask]

        if len(score_responses) > 0:
            print(f"\n✓ Score {score_level} (n={len(score_responses)}):")
            # Show up to 3 examples
            for i, (idx, resp) in enumerate(list(score_responses.items())[:3], 1):
                print(f"  {i}. \"{resp}\"")

    # Language analysis
    print(f"\n{'─'*80}")
    print("LANGUAGE PATTERNS:")

    all_text = ' '.join(responses.dropna().astype(str)).lower()

    hedging = ['maybe', 'might', 'could', 'possibly', 'perhaps', 'somewhat', 'fairly', 'rather', 'probably']
    negative = ['not', "don't", "wouldn't", "won't", 'never', 'no', 'nothing', "isn't", "aren't"]
    positive = ['love', 'great', 'excellent', 'amazing', 'perfect', 'definitely', 'absolutely', 'wonderful']
    concern = ['but', 'however', 'although', 'though', 'concern', 'worried', 'hesitant', 'unsure']

    hedging_count = sum(all_text.count(word) for word in hedging)
    negative_count = sum(all_text.count(word) for word in negative)
    positive_count = sum(all_text.count(word) for word in positive)
    concern_count = sum(all_text.count(word) for word in concern)

    print(f"  Hedging words: {hedging_count} ({hedging_count/len(responses):.2f} per response)")
    print(f"  Negative words: {negative_count} ({negative_count/len(responses):.2f} per response)")
    print(f"  Positive words: {positive_count} ({positive_count/len(responses):.2f} per response)")
    print(f"  Concern words: {concern_count} ({concern_count/len(responses):.2f} per response)")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
