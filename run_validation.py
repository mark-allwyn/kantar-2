#!/usr/bin/env python3
"""
Run Validation Comparison

Compares synthetic data against ground truth with proper column alignment.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

from src.validation.metrics import ValidationMetrics
from src.visualization.comparison_plots import ComparisonVisualizer

# Configure plotting
sns.set_palette("husl")
plt.style.use('seaborn-v0_8-darkgrid')

def reshape_to_long_format(df, dataset_type="ground_truth"):
    """
    Reshape data to long format for comparison.

    Args:
        df: DataFrame (either ground truth or synthetic)
        dataset_type: "ground_truth" or "synthetic"

    Returns:
        DataFrame in long format with columns: respondent_id, concept, question, value
    """
    records = []

    for idx, row in df.iterrows():
        respondent_id = row.get('SERIAL', idx)

        if dataset_type == "ground_truth":
            # Ground truth format: "(QUESTION) Name - 2 CZ ConceptName"
            for col in df.columns:
                # Skip non-question columns
                if not any(q in col for q in ['PRPURINT', 'UNIQNESS', 'PRVALMNY', 'LIKBILTY',
                                              'RELVANCE', 'EXCITMENT', 'Understanding', 'BELVBLTY',
                                              'PLAYFLNS', 'INCREMNT']):
                    continue

                # Extract question type from column name
                # Format: "(QUESTION) Name - 2 CZ ConceptName"
                parts = col.split(' - ')
                if len(parts) < 2:
                    continue

                question_part = parts[0].strip()
                concept_part = ' - '.join(parts[1:]).strip()

                # Extract question code
                if '(' in question_part and ')' in question_part:
                    question_code = question_part.split('(')[1].split(')')[0].strip()
                else:
                    continue

                value = row[col]
                if pd.notna(value):
                    records.append({
                        'respondent_id': respondent_id,
                        'concept': concept_part,
                        'question': question_code,
                        'value': value
                    })

        else:  # synthetic
            # Synthetic format: "Concept N: (QUESTION) Name"
            for col in df.columns:
                if not col.startswith('Concept '):
                    continue

                # Skip non-question columns
                if not any(q in col for q in ['PRPURINT', 'UNIQNESS', 'PRVALMNY', 'LIKBILTY',
                                              'RELVANCE', 'EXCITMENT', 'Understanding', 'BELVBLTY',
                                              'PLAYFLNS', 'INCREMNT']):
                    continue

                # Extract concept number and question
                # Format: "Concept N: (QUESTION) Name"
                parts = col.split(': ', 1)
                if len(parts) < 2:
                    continue

                concept_num = parts[0].strip()
                question_part = parts[1].strip()

                # Extract question code
                if '(' in question_part and ')' in question_part:
                    question_code = question_part.split('(')[1].split(')')[0].strip()
                elif 'Understanding' in question_part:
                    question_code = 'Understanding'
                else:
                    continue

                value = row[col]
                if pd.notna(value):
                    records.append({
                        'respondent_id': respondent_id,
                        'concept': concept_num,
                        'question': question_code,
                        'value': value
                    })

    return pd.DataFrame(records)


def extract_numeric(val):
    """Extract numeric value from formatted response"""
    if pd.isna(val):
        return np.nan
    val_str = str(val)
    if val_str.startswith('(') and ')' in val_str:
        try:
            return int(val_str.split(')')[0][1:])
        except:
            return np.nan
    try:
        return float(val_str)
    except:
        return np.nan


def main():
    print("="*80)
    print("VALIDATION AND COMPARISON")
    print("="*80)

    # Load ground truth
    gt_path = Path('source docs/KAP400232611_Respondent_Data_Tech Enabled CZ.xlsx')
    print(f"\nLoading ground truth: {gt_path.name}")
    df_ground_truth = pd.read_excel(gt_path, sheet_name=0)
    print(f"✓ Ground truth: {len(df_ground_truth)} rows, {len(df_ground_truth.columns)} columns")

    # Load synthetic data (most recent)
    synthetic_dir = Path('data/synthetic')
    synthetic_files = list(synthetic_dir.glob('synthetic_data_*.xlsx'))

    if not synthetic_files:
        print("\n❌ No synthetic data found!")
        print("   Run run_full_pipeline.py first to generate synthetic data.")
        return 1

    # Sort by modification time (most recent last)
    synthetic_file = sorted(synthetic_files, key=lambda f: f.stat().st_mtime)[-1]
    print(f"\nLoading synthetic: {synthetic_file.name}")
    df_synthetic = pd.read_excel(synthetic_file, sheet_name=0)
    print(f"✓ Synthetic: {len(df_synthetic)} rows, {len(df_synthetic.columns)} columns")

    # Reshape both datasets
    print("\n" + "="*80)
    print("Reshaping Data")
    print("="*80)

    print("\nReshaping ground truth to long format...")
    df_gt_long = reshape_to_long_format(df_ground_truth, "ground_truth")
    print(f"✓ Ground truth long: {len(df_gt_long)} records")

    print("\nReshaping synthetic to long format...")
    df_syn_long = reshape_to_long_format(df_synthetic, "synthetic")
    print(f"✓ Synthetic long: {len(df_syn_long)} records")

    # Extract numeric values
    print("\nExtracting numeric values...")
    df_gt_long['numeric_value'] = df_gt_long['value'].apply(extract_numeric)
    df_syn_long['numeric_value'] = df_syn_long['value'].apply(extract_numeric)

    # Find questions present in both datasets
    gt_questions = set(df_gt_long['question'].unique())
    syn_questions = set(df_syn_long['question'].unique())
    common_questions = gt_questions & syn_questions

    print(f"\n✓ Questions in ground truth: {len(gt_questions)}")
    print(f"✓ Questions in synthetic: {len(syn_questions)}")
    print(f"✓ Questions in both: {len(common_questions)}")

    if not common_questions:
        print("\n❌ No common questions found!")
        return 1

    print("\nCommon questions:")
    for q in sorted(common_questions):
        print(f"  - {q}")

    # Compute metrics for each question
    print("\n" + "="*80)
    print("Computing Validation Metrics")
    print("="*80)

    metrics_results = []

    for question in sorted(common_questions):
        gt_data = df_gt_long[df_gt_long['question'] == question]['numeric_value'].dropna()
        syn_data = df_syn_long[df_syn_long['question'] == question]['numeric_value'].dropna()

        if len(gt_data) < 5 or len(syn_data) < 5:
            continue

        print(f"\n{question}:")
        print(f"  GT: {len(gt_data)} responses, Syn: {len(syn_data)} responses")

        # Compute metrics
        metrics = ValidationMetrics.compute_distribution_metrics(
            pd.Series(gt_data),
            pd.Series(syn_data),
            question_type='likert'
        )

        metrics['question'] = question
        metrics['gt_n'] = len(gt_data)
        metrics['syn_n'] = len(syn_data)
        metrics_results.append(metrics)

        print(f"  KL Divergence: {metrics['kl_divergence']:.4f}")
        print(f"  Mean GT: {metrics['ground_truth_mean']:.2f}, Syn: {metrics['synthetic_mean']:.2f}")

    df_metrics = pd.DataFrame(metrics_results)

    # Overall performance
    print("\n" + "="*80)
    print("Overall Performance")
    print("="*80)

    mean_kl = df_metrics['kl_divergence'].mean()
    mean_ks = df_metrics['ks_statistic'].mean()
    mean_mae = df_metrics['mean_absolute_error'].mean()

    print(f"\nMean KL Divergence: {mean_kl:.4f}")
    print(f"  (Lower is better, 0 = perfect match)")
    print(f"  < 0.05 = Excellent")
    print(f"  0.05-0.10 = Good")
    print(f"  0.10-0.20 = Acceptable")
    print(f"  > 0.20 = Needs improvement")

    print(f"\nMean KS Statistic: {mean_ks:.4f}")
    print(f"  (Lower is better, 0 = identical)")

    # Mean KS similarity (paper's metric)
    mean_ks_sim = df_metrics['ks_similarity'].mean()
    print(f"\nMean KS Similarity: {mean_ks_sim:.4f}")
    print(f"  Interpretation:")
    print(f"    > 0.85 = Good (paper benchmark)")
    print(f"    Paper results: GPT-4o SSR = 0.88, Gemini-2f SSR = 0.80")

    print(f"\nMean Absolute Error (on means): {mean_mae:.4f}")

    # Correlation on means
    if len(df_metrics) > 2:
        corr = ValidationMetrics.correlation(
            df_metrics['ground_truth_mean'].values,
            df_metrics['synthetic_mean'].values
        )
        print(f"\nCorrelation (on means): {corr:.4f}")

        corr_att = ValidationMetrics.correlation_attainment(corr, 0, reliability=0.85)
        print(f"Correlation Attainment: {corr_att:.1f}%")
        print(f"  (Target: >85%, Paper achieved: ~90%)")

    # Save results
    print("\n" + "="*80)
    print("Saving Results")
    print("="*80)

    output_dir = Path('data/validation')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save metrics
    metrics_file = output_dir / 'validation_metrics.csv'
    df_metrics.to_csv(metrics_file, index=False)
    print(f"\n✓ Saved metrics: {metrics_file}")

    # Save summary report
    summary_report = f"""Validation Report
{'='*80}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Dataset Sizes:
  Ground Truth: {len(df_ground_truth)} respondents, {len(df_gt_long)} responses
  Synthetic: {len(df_synthetic)} respondents, {len(df_syn_long)} responses

Questions Compared: {len(df_metrics)}

Overall Performance:
{'='*80}

Mean KL Divergence: {mean_kl:.4f}
  Interpretation: Lower is better, 0 = perfect match
  < 0.05 = Excellent
  0.05-0.10 = Good
  0.10-0.20 = Acceptable
  > 0.20 = Needs improvement

Mean KS Statistic: {mean_ks:.4f}
  (Lower is better, 0 = identical)

Mean KS Similarity: {mean_ks_sim:.4f}
  Interpretation:
    > 0.85 = Good (paper benchmark)
    Paper results: GPT-4o SSR = 0.88, Gemini-2f SSR = 0.80

Mean Absolute Error (on means): {mean_mae:.4f}
"""

    if len(df_metrics) > 2:
        summary_report += f"""
Correlation (on means): {corr:.4f}
  Interpretation: How well mean scores match
  > 0.9 = Excellent
  0.7-0.9 = Good
  < 0.7 = Needs improvement

Correlation Attainment: {corr_att:.1f}%
  Target: >85% (human test-retest reliability)
  Paper Benchmark: ~90%
"""

    summary_report += f"""

Best Performing Questions (Lowest KL Divergence):
{'='*80}
"""

    best_questions = df_metrics.nsmallest(min(5, len(df_metrics)), 'kl_divergence')
    for _, row in best_questions.iterrows():
        summary_report += f"""
{row['question']}
  KL Divergence: {row['kl_divergence']:.4f}
  Mean GT: {row['ground_truth_mean']:.2f}, Syn: {row['synthetic_mean']:.2f}
  Sample sizes: GT={row['gt_n']}, Syn={row['syn_n']}
"""

    summary_report += f"""

Worst Performing Questions (Highest KL Divergence):
{'='*80}
"""

    worst_questions = df_metrics.nlargest(min(5, len(df_metrics)), 'kl_divergence')
    for _, row in worst_questions.iterrows():
        summary_report += f"""
{row['question']}
  KL Divergence: {row['kl_divergence']:.4f}
  Mean GT: {row['ground_truth_mean']:.2f}, Syn: {row['synthetic_mean']:.2f}
  Sample sizes: GT={row['gt_n']}, Syn={row['syn_n']}
"""

    report_file = output_dir / 'validation_report.txt'
    with open(report_file, 'w') as f:
        f.write(summary_report)

    print(f"✓ Saved report: {report_file}")

    print("\n" + summary_report)

    print("\n" + "="*80)
    print("COMPLETE")
    print("="*80)

    return 0


if __name__ == '__main__':
    sys.exit(main())
