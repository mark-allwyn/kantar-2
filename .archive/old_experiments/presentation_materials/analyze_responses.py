"""
Analyze LLM responses to understand systematic conservative bias.

This script examines the actual free-text responses from synthetic respondents
to diagnose whether the bias is in:
1. Response generation (genuinely conservative language)
2. SSR mapping (incorrect semantic similarity scoring)
3. Other factors
"""

import pandas as pd
import numpy as np
from pathlib import Path
from src.scales.registry import get_default_registry
from src.ssr.embeddings import EmbeddingService
from src.ssr.similarity import compute_similarities
import warnings
warnings.filterwarnings('ignore')

# Load the embedding service (same one used for SSR)
print("Loading embedding service...")
embedding_service = EmbeddingService()

# Load scale registry
print("Loading scale registry...")
registry = get_default_registry()

# Load synthetic data (most recent baseline run)
synthetic_path = "data/synthetic/synthetic_data_100resp_20251218_170726.xlsx"
print(f"\nLoading synthetic data: {synthetic_path}")
df = pd.read_excel(synthetic_path)

print(f"✓ Loaded {len(df)} respondents")
print(f"✓ Columns: {df.shape[1]}")

# Questions to analyze (the ones in validation)
QUESTIONS = {
    'B2': 'PRPURINT',  # Purchase Intent
    'B4': 'PRVALMNY',  # Value for Money
    'B7': 'LIKBILTY',  # Likeability
    'B8': 'RELVANCE',  # Relevance
    'B9': 'EXCITMENT', # Excitement
    'B11': 'BELVBLTY', # Believability
    'B13': 'UNIQNESS', # Uniqueness
}

print("\n" + "="*80)
print("RESPONSE ANALYSIS BY QUESTION")
print("="*80)

for q_code, q_name in QUESTIONS.items():
    print(f"\n{'='*80}")
    print(f"{q_name} ({q_code})")
    print(f"{'='*80}")

    # Get scale info
    scale = registry.get_scale(f"likert5_{q_name.lower()}_v1")
    if not scale:
        print(f"⚠ Scale not found in registry")
        continue

    anchors = scale.anchor_texts
    print(f"\nScale Anchors:")
    for i, anchor in enumerate(anchors, 1):
        print(f"  {i}: {anchor}")

    # Find response columns for this question across concepts
    response_cols = [col for col in df.columns if col.startswith(f'{q_code}_') and '_response' in col]
    score_cols = [col for col in df.columns if col.startswith(f'{q_code}_') and '_score' in col]

    if not response_cols:
        print(f"\n⚠ No response columns found for {q_code}")
        continue

    print(f"\n✓ Found {len(response_cols)} concepts")

    # Collect all responses and scores
    all_responses = []
    all_scores = []
    all_concepts = []

    for resp_col in response_cols:
        concept = resp_col.split('_')[1]  # Extract concept name
        score_col = f"{q_code}_{concept}_score"

        if score_col not in df.columns:
            continue

        responses = df[resp_col].dropna().tolist()
        scores = df[score_col].dropna().tolist()

        all_responses.extend(responses)
        all_scores.extend(scores)
        all_concepts.extend([concept] * len(responses))

    if not all_responses:
        print(f"\n⚠ No valid responses found")
        continue

    print(f"\n✓ Total responses: {len(all_responses)}")
    print(f"✓ Mean score: {np.mean(all_scores):.2f}")
    print(f"✓ Score distribution: {np.bincount([int(s) for s in all_scores if not np.isnan(s)])}")

    # Sample responses by score level
    print(f"\n{'─'*80}")
    print("SAMPLE RESPONSES BY SCORE")
    print(f"{'─'*80}")

    for score_level in [1, 2, 3, 4, 5]:
        score_responses = [r for r, s in zip(all_responses, all_scores) if int(s) == score_level]

        if score_responses:
            print(f"\nScore {score_level} (n={len(score_responses)}):")
            print(f"  Anchor: \"{anchors[score_level-1]}\"")
            # Show up to 3 examples
            for i, resp in enumerate(score_responses[:3], 1):
                print(f"  Example {i}: \"{resp}\"")

    # Check if responses match their assigned scores
    print(f"\n{'─'*80}")
    print("SSR MAPPING VALIDATION")
    print(f"{'─'*80}")

    # Sample 10 random responses and verify SSR mapping
    sample_size = min(10, len(all_responses))
    sample_indices = np.random.choice(len(all_responses), sample_size, replace=False)

    # Encode anchors
    anchor_embeddings = embedding_service.embed_texts(anchors)

    print(f"\nChecking {sample_size} random responses...")

    mismatches = 0
    for idx in sample_indices:
        response = all_responses[idx]
        assigned_score = int(all_scores[idx])

        # Compute SSR score manually
        response_embedding = embedding_service.embed_single(response)
        similarities = compute_similarities(response_embedding, anchor_embeddings)
        predicted_score = int(np.argmax(similarities) + 1)

        if predicted_score != assigned_score:
            mismatches += 1
            print(f"\n⚠ MISMATCH:")
            print(f"  Response: \"{response}\"")
            print(f"  Assigned: {assigned_score} (\"{anchors[assigned_score-1]}\")")
            print(f"  Predicted: {predicted_score} (\"{anchors[predicted_score-1]}\")")
            print(f"  Similarities: {[f'{s:.3f}' for s in similarities]}")

    if mismatches == 0:
        print(f"✓ All {sample_size} samples correctly mapped")
    else:
        print(f"\n⚠ {mismatches}/{sample_size} mismatches found ({mismatches/sample_size*100:.1f}%)")

    # Language pattern analysis
    print(f"\n{'─'*80}")
    print("LANGUAGE PATTERNS")
    print(f"{'─'*80}")

    # Check for hedging words
    hedging_words = ['maybe', 'might', 'could', 'possibly', 'perhaps', 'somewhat', 'fairly', 'rather']
    negative_words = ['not', "don't", "wouldn't", "won't", 'never', 'no', 'nothing']
    positive_words = ['love', 'great', 'excellent', 'amazing', 'perfect', 'definitely', 'absolutely']

    responses_text = ' '.join(all_responses).lower()

    hedging_count = sum(responses_text.count(word) for word in hedging_words)
    negative_count = sum(responses_text.count(word) for word in negative_words)
    positive_count = sum(responses_text.count(word) for word in positive_words)

    print(f"\nWord patterns across {len(all_responses)} responses:")
    print(f"  Hedging words: {hedging_count} occurrences")
    print(f"  Negative words: {negative_count} occurrences")
    print(f"  Positive words: {positive_count} occurrences")
    print(f"  Hedging ratio: {hedging_count/len(all_responses):.2f} per response")
    print(f"  Negative ratio: {negative_count/len(all_responses):.2f} per response")
    print(f"  Positive ratio: {positive_count/len(all_responses):.2f} per response")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
