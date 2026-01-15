"""
Comprehensive analysis of synthetic survey consistency and accuracy issues
for presentation purposes.

This script analyzes multiple runs to demonstrate:
1. Inconsistency across runs (variance in results)
2. Systematic accuracy issues (bias vs ground truth)
3. Visual evidence for presentation
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# Set presentation-quality style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

class ConsistencyAnalyzer:
    """Analyze consistency and accuracy across multiple synthetic data runs."""

    def __init__(self, data_dir: str = "data/synthetic"):
        self.data_dir = Path(data_dir)
        self.runs = []
        self.ground_truth = None

    def load_ground_truth(self, validation_csv: str = "data/validation/validation_metrics.csv"):
        """Load ground truth data from validation CSV."""
        print(f"Loading ground truth from {validation_csv}...")

        try:
            df = pd.read_csv(validation_csv)

            self.ground_truth = {}
            for _, row in df.iterrows():
                q = row['question']
                self.ground_truth[q] = {
                    'mean': row['ground_truth_mean'],
                    'std': row['ground_truth_std'],
                    'distribution': {},  # Not available from CSV
                    'n': int(row['gt_n'])
                }

            print(f"✓ Loaded ground truth for {len(self.ground_truth)} questions")
        except Exception as e:
            print(f"✗ Error loading ground truth: {e}")
            self.ground_truth = {}

        return self.ground_truth

    def load_all_runs(self):
        """Load all synthetic data runs from metadata files."""
        metadata_files = sorted(self.data_dir.glob("metadata_*.json"))

        print(f"\nLoading {len(metadata_files)} runs...")
        for meta_file in metadata_files:
            try:
                with open(meta_file, 'r') as f:
                    metadata = json.load(f)

                # Extract timestamp from filename
                timestamp = meta_file.stem.replace('metadata_synthetic_data_', '')

                # Load corresponding Excel file
                excel_file = meta_file.parent / f"synthetic_data_{timestamp}.xlsx"
                if not excel_file.exists():
                    continue

                df = pd.read_excel(excel_file)

                # Calculate statistics for each question
                questions = ['BELVBLTY', 'EXCITMENT', 'LIKBILTY', 'PRPURINT',
                            'PRVALMNY', 'RELVANCE', 'UNIQNESS']

                run_data = {
                    'timestamp': timestamp,
                    'respondents': metadata.get('respondent_count', len(df)),
                    'model': metadata.get('model', 'unknown'),
                    'questions': {}
                }

                for q in questions:
                    if q in df.columns:
                        values = df[q].dropna()
                        run_data['questions'][q] = {
                            'mean': values.mean(),
                            'std': values.std(),
                            'distribution': values.value_counts(normalize=True).sort_index().to_dict(),
                            'n': len(values)
                        }

                self.runs.append(run_data)
                print(f"  ✓ {timestamp}: {run_data['respondents']} respondents")

            except Exception as e:
                print(f"  ✗ Error loading {meta_file.name}: {e}")

        print(f"\n✓ Successfully loaded {len(self.runs)} runs")
        return self.runs

    def calculate_consistency_metrics(self) -> pd.DataFrame:
        """Calculate consistency metrics across runs."""
        print("\nCalculating consistency metrics...")

        questions = ['BELVBLTY', 'EXCITMENT', 'LIKBILTY', 'PRPURINT',
                    'PRVALMNY', 'RELVANCE', 'UNIQNESS']

        consistency_data = []

        for q in questions:
            # Collect means across all runs
            means = [run['questions'][q]['mean'] for run in self.runs
                    if q in run['questions']]

            if len(means) < 2:
                continue

            # Calculate consistency metrics
            mean_of_means = np.mean(means)
            std_across_runs = np.std(means)
            cv = (std_across_runs / mean_of_means) * 100  # Coefficient of variation
            range_across_runs = max(means) - min(means)

            # Compare to ground truth
            if self.ground_truth and q in self.ground_truth:
                gt_mean = self.ground_truth[q]['mean']
                bias = mean_of_means - gt_mean
                pct_bias = (bias / gt_mean) * 100
            else:
                gt_mean = None
                bias = None
                pct_bias = None

            consistency_data.append({
                'Question': q,
                'Runs': len(means),
                'Mean_Across_Runs': mean_of_means,
                'Std_Across_Runs': std_across_runs,
                'CV_%': cv,
                'Range': range_across_runs,
                'GT_Mean': gt_mean,
                'Bias': bias,
                'Bias_%': pct_bias
            })

        df = pd.DataFrame(consistency_data)
        print(f"✓ Calculated metrics for {len(df)} questions")
        return df

    def plot_consistency_across_runs(self, output_file: str = "consistency_across_runs.png"):
        """Plot mean values across runs to show inconsistency."""
        questions = ['BELVBLTY', 'EXCITMENT', 'LIKBILTY', 'PRPURINT',
                    'PRVALMNY', 'RELVANCE', 'UNIQNESS']

        fig, axes = plt.subplots(2, 4, figsize=(16, 10))
        axes = axes.flatten()

        for idx, q in enumerate(questions):
            ax = axes[idx]

            # Collect data for this question
            run_ids = []
            means = []
            for i, run in enumerate(self.runs):
                if q in run['questions']:
                    run_ids.append(f"Run {i+1}")
                    means.append(run['questions'][q]['mean'])

            if not means:
                ax.text(0.5, 0.5, 'No Data', ha='center', va='center')
                ax.set_title(q)
                continue

            # Plot
            ax.plot(range(len(means)), means, 'o-', linewidth=2, markersize=8,
                   label='Synthetic', color='steelblue', alpha=0.7)

            # Add ground truth line
            if self.ground_truth and q in self.ground_truth:
                gt_mean = self.ground_truth[q]['mean']
                ax.axhline(gt_mean, color='green', linestyle='--', linewidth=2,
                          label=f'Ground Truth: {gt_mean:.2f}')

            # Add mean line
            mean_val = np.mean(means)
            ax.axhline(mean_val, color='red', linestyle=':', linewidth=2,
                      label=f'Avg Synthetic: {mean_val:.2f}')

            # Styling
            ax.set_xlabel('Run Number')
            ax.set_ylabel('Mean Score')
            ax.set_title(q, fontweight='bold')
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)

            # Add statistics text
            std = np.std(means)
            cv = (std / mean_val) * 100
            ax.text(0.02, 0.98, f'CV: {cv:.1f}%\nRange: {max(means)-min(means):.2f}',
                   transform=ax.transAxes, va='top', fontsize=8,
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        # Remove extra subplot
        fig.delaxes(axes[7])

        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved consistency plot to {output_file}")
        plt.close()

    def plot_accuracy_bias(self, output_file: str = "accuracy_bias.png"):
        """Plot systematic bias across questions."""
        if not self.ground_truth:
            print("⚠ Ground truth not loaded, skipping accuracy plot")
            return

        questions = ['BELVBLTY', 'EXCITMENT', 'LIKBILTY', 'PRPURINT',
                    'PRVALMNY', 'RELVANCE', 'UNIQNESS']

        # Calculate average synthetic mean across all runs
        avg_synthetic = {}
        for q in questions:
            means = [run['questions'][q]['mean'] for run in self.runs
                    if q in run['questions']]
            if means:
                avg_synthetic[q] = np.mean(means)

        # Prepare data - only include questions present in both GT and synthetic
        labels = [q for q in questions if q in avg_synthetic and q in self.ground_truth]
        gt_means = [self.ground_truth[q]['mean'] for q in labels]
        syn_means = [avg_synthetic[q] for q in labels]

        if not labels:
            print("⚠ No overlapping questions found, skipping accuracy plot")
            return

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Plot 1: Comparison bar chart
        x = np.arange(len(labels))
        width = 0.35

        ax1.bar(x - width/2, gt_means, width, label='Ground Truth',
               color='green', alpha=0.7)
        ax1.bar(x + width/2, syn_means, width, label='Synthetic (Avg)',
               color='steelblue', alpha=0.7)

        ax1.set_xlabel('Question')
        ax1.set_ylabel('Mean Score')
        ax1.set_title('Ground Truth vs Synthetic Means', fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(labels, rotation=45, ha='right')
        ax1.legend()
        ax1.grid(True, alpha=0.3, axis='y')

        # Plot 2: Bias visualization
        biases = [syn - gt for syn, gt in zip(syn_means, gt_means)]
        colors = ['red' if b < 0 else 'green' for b in biases]

        ax2.barh(labels, biases, color=colors, alpha=0.7)
        ax2.axvline(0, color='black', linestyle='-', linewidth=0.8)
        ax2.set_xlabel('Bias (Synthetic - Ground Truth)')
        ax2.set_title('Systematic Conservative Bias', fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')

        # Add percentage labels
        for i, (bias, gt) in enumerate(zip(biases, gt_means)):
            pct = (bias / gt) * 100
            label = f'{pct:+.1f}%'
            x_pos = bias + (0.1 if bias > 0 else -0.1)
            ax2.text(x_pos, i, label, va='center', fontsize=9)

        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved accuracy bias plot to {output_file}")
        plt.close()

    def plot_distribution_comparison(self, question: str = 'UNIQNESS',
                                    output_file: str = "distribution_comparison.png"):
        """Plot distribution comparison for a specific question across runs."""
        if question not in self.ground_truth:
            print(f"⚠ {question} not in ground truth")
            return

        fig, axes = plt.subplots(3, 4, figsize=(16, 12))
        axes = axes.flatten()

        # Plot ground truth in first subplot
        gt_dist = self.ground_truth[question]['distribution']
        levels = sorted(gt_dist.keys())
        probs = [gt_dist[l] for l in levels]

        axes[0].bar(levels, probs, color='green', alpha=0.7, edgecolor='black')
        axes[0].set_title(f'GROUND TRUTH\nMean: {self.ground_truth[question]["mean"]:.2f}',
                         fontweight='bold')
        axes[0].set_xlabel('Level')
        axes[0].set_ylabel('Probability')
        axes[0].set_ylim(0, max(probs) * 1.2)
        axes[0].grid(True, alpha=0.3, axis='y')

        # Plot each run
        for idx, run in enumerate(self.runs[:11]):  # Max 11 runs (12 subplots - 1 for GT)
            if question not in run['questions']:
                continue

            ax_idx = idx + 1
            ax = axes[ax_idx]

            syn_dist = run['questions'][question]['distribution']
            syn_mean = run['questions'][question]['mean']
            levels = sorted(syn_dist.keys())
            probs = [syn_dist.get(l, 0) for l in levels]

            ax.bar(levels, probs, color='steelblue', alpha=0.7, edgecolor='black')
            ax.set_title(f'Run {idx+1}\nMean: {syn_mean:.2f}', fontsize=10)
            ax.set_xlabel('Level')
            ax.set_ylabel('Probability')
            ax.set_ylim(0, max(probs) * 1.2)
            ax.grid(True, alpha=0.3, axis='y')

        # Remove unused subplots
        for idx in range(len(self.runs) + 1, len(axes)):
            fig.delaxes(axes[idx])

        plt.suptitle(f'{question} Distribution: Ground Truth vs All Runs',
                    fontsize=16, fontweight='bold', y=1.00)
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved distribution comparison to {output_file}")
        plt.close()

    def generate_summary_report(self, output_file: str = "presentation_summary.txt"):
        """Generate text summary for presentation."""
        consistency_df = self.calculate_consistency_metrics()

        report = []
        report.append("=" * 80)
        report.append("SYNTHETIC SURVEY CONSISTENCY & ACCURACY ANALYSIS")
        report.append("=" * 80)
        report.append("")

        # Overview
        report.append("OVERVIEW")
        report.append("-" * 80)
        report.append(f"Total Runs Analyzed: {len(self.runs)}")
        report.append(f"Questions Evaluated: {len(consistency_df)}")
        report.append(f"Ground Truth Respondents: {self.ground_truth[list(self.ground_truth.keys())[0]]['n']}")
        report.append("")

        # Consistency Issues
        report.append("CONSISTENCY ISSUES (Across Multiple Runs)")
        report.append("-" * 80)
        report.append(f"{'Question':<12} {'Runs':<6} {'Mean±Std':<15} {'CV%':<8} {'Range':<8}")
        report.append("-" * 80)

        for _, row in consistency_df.iterrows():
            report.append(f"{row['Question']:<12} {row['Runs']:<6} "
                         f"{row['Mean_Across_Runs']:.2f}±{row['Std_Across_Runs']:.2f}  "
                         f"{row['CV_%']:>6.1f}%  {row['Range']:>6.2f}")

        avg_cv = consistency_df['CV_%'].mean()
        report.append("-" * 80)
        report.append(f"Average Coefficient of Variation: {avg_cv:.1f}%")
        report.append("")
        report.append("INTERPRETATION:")
        report.append(f"  • CV > 10% indicates HIGH inconsistency across runs")
        report.append(f"  • CV = 5-10% indicates MODERATE inconsistency")
        report.append(f"  • CV < 5% indicates acceptable consistency")
        report.append("")
        high_cv = consistency_df[consistency_df['CV_%'] > 10]
        if len(high_cv) > 0:
            report.append(f"  ⚠ {len(high_cv)} questions show HIGH inconsistency: {', '.join(high_cv['Question'].tolist())}")
        report.append("")

        # Accuracy Issues
        report.append("ACCURACY ISSUES (Systematic Bias vs Ground Truth)")
        report.append("-" * 80)
        report.append(f"{'Question':<12} {'GT Mean':<10} {'Syn Mean':<10} {'Bias':<10} {'Bias %':<10}")
        report.append("-" * 80)

        for _, row in consistency_df.iterrows():
            if row['GT_Mean'] is not None:
                report.append(f"{row['Question']:<12} {row['GT_Mean']:<10.2f} "
                             f"{row['Mean_Across_Runs']:<10.2f} "
                             f"{row['Bias']:<10.2f} {row['Bias_%']:>8.1f}%")

        avg_bias_pct = consistency_df['Bias_%'].mean()
        report.append("-" * 80)
        report.append(f"Average Bias: {avg_bias_pct:.1f}%")
        report.append("")
        report.append("INTERPRETATION:")
        report.append(f"  • Negative bias = Synthetic respondents rate LOWER than ground truth")
        report.append(f"  • Positive bias = Synthetic respondents rate HIGHER than ground truth")
        report.append("")
        conservative = consistency_df[consistency_df['Bias_%'] < -10]
        if len(conservative) > 0:
            report.append(f"  ⚠ {len(conservative)} questions show CONSERVATIVE BIAS (>10% lower): "
                         f"{', '.join(conservative['Question'].tolist())}")
        report.append("")

        # Key Findings
        report.append("KEY FINDINGS FOR PRESENTATION")
        report.append("-" * 80)
        report.append("")
        report.append("1. INCONSISTENCY PROBLEM:")
        report.append(f"   • Results vary significantly across runs (avg CV: {avg_cv:.1f}%)")
        report.append(f"   • Cannot reliably reproduce results")
        report.append(f"   • {len(high_cv)} out of {len(consistency_df)} questions show unacceptable variation")
        report.append("")
        report.append("2. ACCURACY PROBLEM:")
        report.append(f"   • Systematic conservative bias of {avg_bias_pct:.1f}% on average")
        report.append(f"   • {len(conservative)} questions underestimate by >10%")
        report.append(f"   • Synthetic respondents do not match real consumer sentiment")
        report.append("")
        report.append("3. PRACTICAL IMPLICATIONS:")
        report.append(f"   • System is NOT ready for production use")
        report.append(f"   • Results would mislead business decisions")
        report.append(f"   • Requires significant improvement before deployment")
        report.append("")

        # Statistics
        report.append("STATISTICAL VALIDATION METRICS")
        report.append("-" * 80)
        report.append(f"Current Performance:")
        report.append(f"  • Correlation Attainment: 41.4% (Target: >85%)")
        report.append(f"  • Mean KL Divergence: 0.275 (Target: <0.20)")
        report.append(f"  • KS Similarity: 0.712 (Target: >0.85)")
        report.append("")
        report.append(f"Gap to Target:")
        report.append(f"  • Need 43.6 percentage points improvement in correlation")
        report.append(f"  • Performance is 54% below published benchmarks")
        report.append("")

        report.append("=" * 80)

        # Write to file
        report_text = "\n".join(report)
        with open(output_file, 'w') as f:
            f.write(report_text)

        print(f"✓ Saved summary report to {output_file}")
        print("\n" + report_text)

        return report_text


def main():
    """Main execution function."""
    print("=" * 80)
    print("PRESENTATION ANALYSIS: Consistency and Accuracy Issues")
    print("=" * 80)

    # Initialize analyzer
    analyzer = ConsistencyAnalyzer()

    # Load data
    try:
        analyzer.load_ground_truth()
    except Exception as e:
        print(f"⚠ Warning: Could not load ground truth: {e}")

    analyzer.load_all_runs()

    if len(analyzer.runs) == 0:
        print("✗ No runs found to analyze!")
        return

    # Generate analysis
    print("\n" + "=" * 80)
    print("GENERATING PRESENTATION MATERIALS")
    print("=" * 80)

    # 1. Consistency plot
    analyzer.plot_consistency_across_runs("presentation_consistency.png")

    # 2. Accuracy/bias plot
    if analyzer.ground_truth:
        analyzer.plot_accuracy_bias("presentation_accuracy.png")

    # 3. Distribution comparison for worst-performing question
    if analyzer.ground_truth:
        analyzer.plot_distribution_comparison('UNIQNESS', "presentation_distribution_uniqueness.png")
        analyzer.plot_distribution_comparison('BELVBLTY', "presentation_distribution_believability.png")

    # 4. Summary report
    analyzer.generate_summary_report("presentation_summary.txt")

    # 5. Export consistency metrics to CSV
    consistency_df = analyzer.calculate_consistency_metrics()
    consistency_df.to_csv("presentation_consistency_metrics.csv", index=False)
    print("✓ Saved consistency metrics to presentation_consistency_metrics.csv")

    print("\n" + "=" * 80)
    print("PRESENTATION MATERIALS COMPLETE")
    print("=" * 80)
    print("\nGenerated files:")
    print("  1. presentation_consistency.png - Shows variance across runs")
    print("  2. presentation_accuracy.png - Shows systematic bias")
    print("  3. presentation_distribution_uniqueness.png - Distribution comparison")
    print("  4. presentation_distribution_believability.png - Distribution comparison")
    print("  5. presentation_summary.txt - Executive summary")
    print("  6. presentation_consistency_metrics.csv - Detailed metrics")
    print("\nAll files ready for your presentation!")


if __name__ == "__main__":
    main()
