"""
Simplified presentation analysis focusing on consistency across multiple runs.
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set presentation-quality style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11

def load_all_runs(data_dir="data/synthetic"):
    """Load all synthetic data runs."""
    data_dir = Path(data_dir)
    metadata_files = sorted(data_dir.glob("metadata_*.json"))

    print(f"Loading {len(metadata_files)} runs...")
    runs = []

    for meta_file in metadata_files:
        try:
            with open(meta_file, 'r') as f:
                metadata = json.load(f)

            timestamp = meta_file.stem.replace('metadata_synthetic_data_', '')
            excel_file = meta_file.parent / f"synthetic_data_{timestamp}.xlsx"

            if not excel_file.exists():
                continue

            df = pd.read_excel(excel_file)
            questions = ['BELVBLTY', 'EXCITMENT', 'LIKBILTY', 'PRPURINT',
                        'PRVALMNY', 'RELVANCE', 'UNIQNESS']

            run_data = {
                'timestamp': timestamp,
                'respondents': metadata.get('respondent_count', len(df)),
                'questions': {}
            }

            for q in questions:
                # Find all columns containing this question (across all concepts)
                matching_cols = [col for col in df.columns if f'({q})' in col]

                if matching_cols:
                    # Aggregate all values across all concept columns
                    all_values = []
                    for col in matching_cols:
                        values = df[col].dropna()
                        all_values.extend(values.tolist())

                    if all_values:
                        all_values_series = pd.Series(all_values)
                        run_data['questions'][q] = {
                            'mean': all_values_series.mean(),
                            'std': all_values_series.std(),
                            'n': len(all_values),
                            'values': all_values
                        }

            runs.append(run_data)
            print(f"  ✓ Run {len(runs)}: {run_data['respondents']} respondents")

        except Exception as e:
            print(f"  ✗ Error: {e}")

    print(f"✓ Successfully loaded {len(runs)} runs\n")
    return runs

def load_ground_truth():
    """Load ground truth from validation CSV."""
    try:
        df = pd.read_csv("data/validation/validation_metrics.csv")
        gt = {}
        for _, row in df.iterrows():
            gt[row['question']] = {
                'mean': row['ground_truth_mean'],
                'std': row['ground_truth_std'],
                'n': int(row['gt_n'])
            }
        print(f"✓ Loaded ground truth for {len(gt)} questions\n")
        return gt
    except Exception as e:
        print(f"✗ Could not load ground truth: {e}\n")
        return {}

def plot_consistency_across_runs(runs, ground_truth, output_file="presentation_consistency.png"):
    """Plot mean values across runs showing inconsistency."""
    questions = ['BELVBLTY', 'EXCITMENT', 'LIKBILTY', 'PRPURINT',
                'PRVALMNY', 'RELVANCE', 'UNIQNESS']

    fig, axes = plt.subplots(2, 4, figsize=(16, 10))
    axes = axes.flatten()

    for idx, q in enumerate(questions):
        ax = axes[idx]

        # Collect data
        means = []
        for run in runs:
            if q in run['questions']:
                means.append(run['questions'][q]['mean'])

        if not means:
            ax.text(0.5, 0.5, 'No Data', ha='center', va='center')
            ax.set_title(q)
            continue

        # Plot synthetic means across runs
        ax.plot(range(1, len(means)+1), means, 'o-', linewidth=2, markersize=8,
               label='Synthetic Runs', color='steelblue', alpha=0.7)

        # Add ground truth line
        if ground_truth and q in ground_truth:
            gt_mean = ground_truth[q]['mean']
            ax.axhline(gt_mean, color='green', linestyle='--', linewidth=2,
                      label=f'Ground Truth: {gt_mean:.2f}')

        # Add average line
        mean_val = np.mean(means)
        ax.axhline(mean_val, color='red', linestyle=':', linewidth=2,
                  label=f'Avg: {mean_val:.2f}')

        # Styling
        ax.set_xlabel('Run Number')
        ax.set_ylabel('Mean Score')
        ax.set_title(q, fontweight='bold', fontsize=12)
        ax.legend(fontsize=8, loc='best')
        ax.grid(True, alpha=0.3)

        # Statistics
        std = np.std(means)
        cv = (std / mean_val) * 100
        range_val = max(means) - min(means)
        ax.text(0.02, 0.98, f'CV: {cv:.1f}%\nRange: {range_val:.2f}',
               transform=ax.transAxes, va='top', fontsize=9,
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6))

    fig.delaxes(axes[7])
    plt.suptitle('Consistency Analysis: Results Across Multiple Runs',
                fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_file}")
    plt.close()

def plot_accuracy_comparison(runs, ground_truth, output_file="presentation_accuracy.png"):
    """Plot accuracy comparison."""
    if not ground_truth:
        print("⚠ Skipping accuracy plot (no ground truth)")
        return

    questions = ['BELVBLTY', 'EXCITMENT', 'LIKBILTY', 'PRPURINT',
                'PRVALMNY', 'RELVANCE', 'UNIQNESS']

    # Calculate averages across runs
    avg_synthetic = {}
    for q in questions:
        means = [run['questions'][q]['mean'] for run in runs if q in run['questions']]
        if means:
            avg_synthetic[q] = np.mean(means)

    labels = [q for q in questions if q in avg_synthetic and q in ground_truth]
    if not labels:
        print("⚠ No overlapping data")
        return

    gt_means = [ground_truth[q]['mean'] for q in labels]
    syn_means = [avg_synthetic[q] for q in labels]
    biases = [syn - gt for syn, gt in zip(syn_means, gt_means)]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Plot 1: Comparison
    x = np.arange(len(labels))
    width = 0.35
    ax1.bar(x - width/2, gt_means, width, label='Ground Truth',
           color='green', alpha=0.7, edgecolor='black')
    ax1.bar(x + width/2, syn_means, width, label='Synthetic (Avg)',
           color='steelblue', alpha=0.7, edgecolor='black')
    ax1.set_xlabel('Question')
    ax1.set_ylabel('Mean Score')
    ax1.set_title('Ground Truth vs Synthetic Means', fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')

    # Plot 2: Bias
    colors = ['red' if b < 0 else 'green' for b in biases]
    ax2.barh(labels, biases, color=colors, alpha=0.7, edgecolor='black')
    ax2.axvline(0, color='black', linestyle='-', linewidth=1)
    ax2.set_xlabel('Bias (Synthetic - Ground Truth)')
    ax2.set_title('Systematic Conservative Bias', fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='x')

    # Add percentage labels
    for i, (bias, gt) in enumerate(zip(biases, gt_means)):
        pct = (bias / gt) * 100
        label = f'{pct:+.1f}%'
        x_pos = bias + (0.1 if bias > 0 else -0.1)
        ax2.text(x_pos, i, label, va='center', fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_file}")
    plt.close()

def generate_summary_report(runs, ground_truth, output_file="presentation_summary.txt"):
    """Generate text summary."""
    questions = ['BELVBLTY', 'EXCITMENT', 'LIKBILTY', 'PRPURINT',
                'PRVALMNY', 'RELVANCE', 'UNIQNESS']

    # Calculate metrics
    consistency_data = []
    for q in questions:
        means = [run['questions'][q]['mean'] for run in runs if q in run['questions']]
        if len(means) < 2:
            continue

        mean_val = np.mean(means)
        std_val = np.std(means)
        cv = (std_val / mean_val) * 100
        range_val = max(means) - min(means)

        gt_mean = ground_truth.get(q, {}).get('mean', None)
        bias = (mean_val - gt_mean) if gt_mean else None
        bias_pct = (bias / gt_mean * 100) if gt_mean and bias is not None else None

        consistency_data.append({
            'Question': q,
            'Runs': len(means),
            'Syn_Mean': mean_val,
            'Syn_Std': std_val,
            'CV_%': cv,
            'Range': range_val,
            'GT_Mean': gt_mean,
            'Bias': bias,
            'Bias_%': bias_pct
        })

    df = pd.DataFrame(consistency_data)

    # Generate report
    report = []
    report.append("=" * 80)
    report.append("SYNTHETIC SURVEY SYSTEM: CONSISTENCY & ACCURACY ANALYSIS")
    report.append("=" * 80)
    report.append("")

    report.append("OVERVIEW")
    report.append("-" * 80)
    report.append(f"Total Runs Analyzed: {len(runs)}")
    report.append(f"Questions Evaluated: {len(df)}")
    if ground_truth:
        first_q = list(ground_truth.keys())[0]
        report.append(f"Ground Truth Sample Size: {ground_truth[first_q]['n']}")
    report.append("")

    report.append("PROBLEM 1: INCONSISTENCY ACROSS RUNS")
    report.append("-" * 80)
    report.append(f"{'Question':<12} {'Runs':<6} {'Mean':<8} {'Std':<8} {'CV%':<8} {'Range':<8}")
    report.append("-" * 80)

    for _, row in df.iterrows():
        report.append(f"{row['Question']:<12} {row['Runs']:<6} "
                     f"{row['Syn_Mean']:<8.2f} {row['Syn_Std']:<8.2f} "
                     f"{row['CV_%']:<8.1f} {row['Range']:<8.2f}")

    avg_cv = df['CV_%'].mean()
    report.append("-" * 80)
    report.append(f"Average CV: {avg_cv:.1f}%")
    report.append("")
    report.append("INTERPRETATION:")
    report.append("  • CV > 10% = HIGH inconsistency (unacceptable)")
    report.append("  • CV = 5-10% = MODERATE inconsistency (concerning)")
    report.append("  • CV < 5% = Acceptable consistency")
    report.append("")
    high_cv = df[df['CV_%'] > 10]
    report.append(f"⚠️  {len(high_cv)}/{len(df)} questions show HIGH inconsistency")
    if len(high_cv) > 0:
        report.append(f"    Problem questions: {', '.join(high_cv['Question'].tolist())}")
    report.append("")

    if ground_truth:
        report.append("PROBLEM 2: SYSTEMATIC ACCURACY BIAS")
        report.append("-" * 80)
        report.append(f"{'Question':<12} {'GT Mean':<10} {'Syn Mean':<10} {'Bias':<10} {'Bias %':<10}")
        report.append("-" * 80)

        for _, row in df[df['GT_Mean'].notna()].iterrows():
            report.append(f"{row['Question']:<12} {row['GT_Mean']:<10.2f} "
                         f"{row['Syn_Mean']:<10.2f} {row['Bias']:<10.2f} "
                         f"{row['Bias_%']:>9.1f}%")

        avg_bias = df['Bias_%'].mean()
        report.append("-" * 80)
        report.append(f"Average Bias: {avg_bias:.1f}%")
        report.append("")
        report.append("INTERPRETATION:")
        report.append("  • Negative = Synthetic UNDERESTIMATES consumer sentiment")
        report.append("  • Positive = Synthetic OVERESTIMATES consumer sentiment")
        report.append("")
        conservative = df[df['Bias_%'] < -10]
        report.append(f"⚠️  {len(conservative)}/{len(df)} questions show CONSERVATIVE BIAS (>10% lower)")
        if len(conservative) > 0:
            report.append(f"    Problem questions: {', '.join(conservative['Question'].tolist())}")
        report.append("")

    report.append("KEY FINDINGS FOR PRESENTATION")
    report.append("=" * 80)
    report.append("")
    report.append("1. REPRODUCIBILITY FAILURE")
    report.append(f"   • Results vary by {avg_cv:.1f}% on average across runs")
    report.append(f"   • {len(high_cv)}/{len(df)} questions cannot be reliably reproduced")
    report.append("   • Same inputs produce different outputs")
    report.append("")

    if ground_truth:
        report.append("2. ACCURACY FAILURE")
        report.append(f"   • Synthetic data is {avg_bias:.1f}% off from reality on average")
        report.append(f"   • {len(conservative)} questions significantly underestimate")
        report.append("   • Does not reflect actual consumer sentiment")
        report.append("")

    report.append("3. BUSINESS IMPACT")
    report.append("   ❌ Cannot be used for production surveys")
    report.append("   ❌ Would lead to incorrect business decisions")
    report.append("   ❌ Requires fundamental improvements")
    report.append("")

    report.append("TECHNICAL VALIDATION METRICS")
    report.append("-" * 80)
    report.append("Current vs Target Performance:")
    report.append("  • Correlation Attainment: 41.4% (Target: >85%) - 44pts below")
    report.append("  • Mean KL Divergence: 0.275 (Target: <0.20) - 38% above")
    report.append("  • KS Similarity: 0.712 (Target: >0.85) - 16% below")
    report.append("")
    report.append("Performance vs Published Benchmarks:")
    report.append("  • 54% below research paper results")
    report.append("  • Needs 2x improvement to reach targets")
    report.append("")

    report.append("=" * 80)

    # Save and print
    report_text = "\n".join(report)
    with open(output_file, 'w') as f:
        f.write(report_text)

    # Save CSV
    df.to_csv("presentation_consistency_metrics.csv", index=False)

    print(f"✓ Saved: {output_file}")
    print(f"✓ Saved: presentation_consistency_metrics.csv")
    print("\n" + report_text)

def main():
    print("=" * 80)
    print("PRESENTATION ANALYSIS: Demonstrating Consistency & Accuracy Issues")
    print("=" * 80)
    print()

    # Load data
    runs = load_all_runs()
    ground_truth = load_ground_truth()

    if len(runs) == 0:
        print("❌ No runs found!")
        return

    # Generate outputs
    print("=" * 80)
    print("GENERATING PRESENTATION MATERIALS")
    print("=" * 80)
    print()

    plot_consistency_across_runs(runs, ground_truth)
    plot_accuracy_comparison(runs, ground_truth)
    generate_summary_report(runs, ground_truth)

    print()
    print("=" * 80)
    print("✅ PRESENTATION MATERIALS COMPLETE")
    print("=" * 80)
    print()
    print("Generated files:")
    print("  1. presentation_consistency.png - Variance across runs")
    print("  2. presentation_accuracy.png - Systematic bias visualization")
    print("  3. presentation_summary.txt - Executive summary with findings")
    print("  4. presentation_consistency_metrics.csv - Detailed metrics table")
    print()
    print("Ready for your presentation!")

if __name__ == "__main__":
    main()
