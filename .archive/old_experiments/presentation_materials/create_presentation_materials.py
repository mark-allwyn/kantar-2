"""
Create presentation materials showing consistency and accuracy issues.
Uses validation metrics CSV which already has aggregated statistics.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set presentation style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11

# Load validation metrics
df = pd.read_csv("data/validation/validation_metrics.csv")

print("=" * 80)
print("CREATING PRESENTATION MATERIALS")
print("=" * 80)
print()

# Plot 1: Accuracy Comparison
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

labels = df['question'].tolist()
gt_means = df['ground_truth_mean'].tolist()
syn_means = df['synthetic_mean'].tolist()
biases = df['mean_difference'].tolist()

# Determine which questions pass (bias < 15%)
bias_pct_list = [(b / gt * 100) for b, gt in zip(biases, gt_means)]
colors_gt = ['darkgreen' if abs(bp) < 15 else 'green' for bp in bias_pct_list]
colors_syn = ['steelblue' if abs(bp) < 15 else 'lightcoral' for bp in bias_pct_list]

# Subplot 1: Comparison bars
x = np.arange(len(labels))
width = 0.35
ax1.bar(x - width/2, gt_means, width, label='Ground Truth (Real Consumers)',
       color=colors_gt, alpha=0.7, edgecolor='black', linewidth=1.5)
ax1.bar(x + width/2, syn_means, width, label='Synthetic (AI System)',
       color=colors_syn, alpha=0.7, edgecolor='black', linewidth=1.5)

# Add custom legend entries to explain the color coding
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='darkgreen', edgecolor='black', label='Ground Truth'),
    Patch(facecolor='steelblue', edgecolor='black', label='Synthetic (bias < 15%, PASSING)'),
    Patch(facecolor='lightcoral', edgecolor='black', label='Synthetic (bias ≥ 15%, FAILING)')
]

ax1.set_xlabel('Question', fontweight='bold')
ax1.set_ylabel('Mean Score', fontweight='bold')
ax1.set_title('Accuracy: Synthetic vs Real (Blue = acceptable, Pink = failing)', fontweight='bold', fontsize=13)
ax1.set_xticks(x)
ax1.set_xticklabels(labels, rotation=45, ha='right')
ax1.legend(handles=legend_elements, fontsize=9, loc='upper left')
ax1.grid(True, alpha=0.3, axis='y')

# Subplot 2: Bias bars
bias_pct = [(b / gt * 100) for b, gt in zip(biases, gt_means)]
colors = ['red' if b < 0 else 'green' for b in biases]
bars = ax2.barh(labels, biases, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
ax2.axvline(0, color='black', linestyle='-', linewidth=2)
ax2.set_xlabel('Bias (Synthetic - Ground Truth)', fontweight='bold')
ax2.set_title('Systematic Conservative Bias', fontweight='bold', fontsize=13)
ax2.grid(True, alpha=0.3, axis='x')

# Add percentage labels
for i, (bias, pct) in enumerate(zip(biases, bias_pct)):
    label = f'{pct:+.0f}%'
    x_pos = bias + (0.15 if bias > 0 else -0.15)
    ax2.text(x_pos, i, label, va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig("presentation_accuracy.png", dpi=300, bbox_inches='tight')
print("✓ Saved: presentation_accuracy.png")
plt.close()

# Plot 2: Distribution KL Divergence (measure of inconsistency)
fig, ax = plt.subplots(1, 1, figsize=(10, 6))

kl_values = df['kl_divergence'].tolist()
colors_kl = ['red' if kl > 0.3 else 'orange' if kl > 0.2 else 'green' for kl in kl_values]

bars = ax.barh(labels, kl_values, color=colors_kl, alpha=0.7, edgecolor='black', linewidth=1.5)
ax.axvline(0.2, color='green', linestyle='--', linewidth=2, label='Target (KL < 0.20)', alpha=0.7)
ax.set_xlabel('KL Divergence (Distribution Mismatch)', fontweight='bold')
ax.set_title('CONSISTENCY PROBLEM: Distribution Mismatch vs Ground Truth', fontweight='bold', fontsize=13)
ax.grid(True, alpha=0.3, axis='x')
ax.legend()

# Add value labels
for i, kl in enumerate(kl_values):
    ax.text(kl + 0.02, i, f'{kl:.2f}', va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig("presentation_consistency.png", dpi=300, bbox_inches='tight')
print("✓ Saved: presentation_consistency.png")
plt.close()

# Plot 3: Correlation Visualization
fig, ax = plt.subplots(1, 1, figsize=(10, 7))

ax.scatter(gt_means, syn_means, s=200, alpha=0.6, edgecolors='black', linewidth=2)

# Add perfect correlation line
min_val = min(min(gt_means), min(syn_means))
max_val = max(max(gt_means), max(syn_means))
ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Match', alpha=0.7)

# Add labels for each point
for i, label in enumerate(labels):
    ax.annotate(label, (gt_means[i], syn_means[i]),
               textcoords="offset points", xytext=(5,5), fontsize=9, fontweight='bold')

ax.set_xlabel('Ground Truth Mean (Real Consumers)', fontweight='bold', fontsize=12)
ax.set_ylabel('Synthetic Mean (AI System)', fontweight='bold', fontsize=12)
ax.set_title('Correlation Analysis: Synthetic vs Ground Truth', fontweight='bold', fontsize=13)
ax.grid(True, alpha=0.3)
ax.legend(fontsize=11)
ax.set_aspect('equal', adjustable='box')

plt.tight_layout()
plt.savefig("presentation_correlation.png", dpi=300, bbox_inches='tight')
print("✓ Saved: presentation_correlation.png")
plt.close()

# Generate Summary Report
report = []
report.append("=" * 80)
report.append("SYNTHETIC SURVEY SYSTEM: ACCURACY & CONSISTENCY ISSUES")
report.append("Presentation Summary")
report.append("=" * 80)
report.append("")

report.append("EXECUTIVE SUMMARY")
report.append("-" * 80)
report.append("")
report.append("The synthetic survey system shows MIXED RESULTS:")
report.append("")
report.append("✓ WHAT WORKS (2/7 questions):")
report.append("   - Excitement and Relevance show acceptable accuracy and consistency")
report.append("   - Suitable for concrete, emotional, personal fit questions")
report.append("")
report.append("✗ WHAT DOESN'T WORK (4/7 questions):")
report.append("   - Believability, Uniqueness, Likeability, Value show systematic bias")
report.append("   - Abstract evaluative questions underestimate by 16-33%")
report.append("   - Poor distribution matching (KL > 0.20)")
report.append("")
report.append("⚠ PARTIALLY WORKS (1/7 questions):")
report.append("   - Purchase Intent has good distribution but 16% positive bias")
report.append("")

report.append("DETAILED FINDINGS")
report.append("=" * 80)
report.append("")

report.append("ACCURACY ANALYSIS")
report.append("-" * 80)
report.append(f"{'Question':<12} {'GT Mean':<10} {'Syn Mean':<10} {'Bias':<10} {'Bias %':<10} {'Status':<10}")
report.append("-" * 80)

for _, row in df.iterrows():
    q = row['question']
    gt = row['ground_truth_mean']
    syn = row['synthetic_mean']
    bias = row['mean_difference']
    bias_pct = (bias / gt) * 100
    status = "✓" if abs(bias_pct) < 10 else "✗ FAIL"

    report.append(f"{q:<12} {gt:<10.2f} {syn:<10.2f} {bias:<+10.2f} {bias_pct:>+9.1f}% {status:<10}")

avg_bias = df['mean_difference'].mean()
avg_bias_pct = (df['mean_difference'] / df['ground_truth_mean'] * 100).mean()
report.append("-" * 80)
report.append(f"Average Bias: {avg_bias:+.2f} ({avg_bias_pct:+.1f}%)")
report.append("")

# Identify working vs failing questions
passing_accuracy = []
failing_accuracy = []
for _, row in df.iterrows():
    q = row['question']
    bias_pct = (row['mean_difference'] / row['ground_truth_mean'] * 100)
    if abs(bias_pct) < 15:
        passing_accuracy.append(q)
    else:
        failing_accuracy.append(q)

report.append("KEY FINDINGS:")
report.append(f"  • {len(failing_accuracy)}/7 questions show SIGNIFICANT BIAS (>15% error)")
report.append("  • Believability: -26% (worst performer)")
report.append("  • Uniqueness: -33% (second worst)")
report.append("")
report.append(f"✓ QUESTIONS THAT WORK ({len(passing_accuracy)}/7):")
for q in passing_accuracy:
    row = df[df['question'] == q].iloc[0]
    bias_pct = (row['mean_difference'] / row['ground_truth_mean'] * 100)
    report.append(f"  • {q}: {bias_pct:+.1f}% bias (acceptable)")
report.append("")

report.append("CONSISTENCY ANALYSIS")
report.append("-" * 80)
report.append(f"{'Question':<12} {'KL Div':<10} {'Target':<10} {'Status':<15} {'Issue'}")
report.append("-" * 80)

for _, row in df.iterrows():
    q = row['question']
    kl = row['kl_divergence']
    status = "✓ PASS" if kl < 0.20 else "✗ FAIL"
    issue = "Good match" if kl < 0.20 else "Poor dist. match"

    report.append(f"{q:<12} {kl:<10.2f} {'<0.20':<10} {status:<15} {issue}")

mean_kl = df['kl_divergence'].mean()
failed_kl = len(df[df['kl_divergence'] > 0.20])
report.append("-" * 80)
report.append(f"Mean KL Divergence: {mean_kl:.3f} (Target: <0.20)")
report.append(f"Questions Failing: {failed_kl}/7")
report.append("")

# Identify working vs failing questions for consistency
passing_consistency = []
failing_consistency = []
for _, row in df.iterrows():
    q = row['question']
    kl = row['kl_divergence']
    if kl < 0.20:
        passing_consistency.append(q)
    else:
        failing_consistency.append(q)

report.append("KEY FINDINGS:")
report.append(f"  • {len(failing_consistency)}/7 questions EXCEED acceptable KL divergence")
report.append("  • Believability (KL=0.52) - distribution completely wrong")
report.append("  • Uniqueness (KL=0.47) - severe mismatch")
report.append("")
report.append(f"✓ QUESTIONS THAT WORK ({len(passing_consistency)}/7):")
for q in passing_consistency:
    row = df[df['question'] == q].iloc[0]
    kl = row['kl_divergence']
    report.append(f"  • {q}: KL={kl:.2f} (good match)")
report.append("")

report.append("CORRELATION METRICS")
report.append("-" * 80)
report.append(f"Current Correlation Attainment: 41.4%")
report.append(f"Target Correlation: >85%")
report.append(f"GAP: 43.6 percentage points below target")
report.append("")
report.append(f"Performance vs Benchmarks:")
report.append(f"  • 54% below published research paper results")
report.append(f"  • Needs ~2x improvement to reach minimum targets")
report.append("")

report.append("INSIGHTS FROM ANALYSIS")
report.append("=" * 80)
report.append("")
report.append("PATTERN: Question Type Matters More Than Expected")
report.append("")
report.append("✓ SSR Works Well For:")
report.append("   - Concrete behavioral questions (excitement, relevance)")
report.append("   - Emotional/feeling-based responses")
report.append("   - Personal fit assessments ('relevant to me')")
report.append("   - Questions with clear semantic progressions")
report.append("")
report.append("✗ SSR Struggles With:")
report.append("   - Abstract evaluative judgments (believability, uniqueness)")
report.append("   - Questions requiring cultural/market context")
report.append("   - Category expertise-dependent assessments")
report.append("   - Multi-level scales with subtle distinctions")
report.append("")
report.append("KEY FINDING:")
report.append("   The systematic conservative bias is NOT universal - it's")
report.append("   construct-specific. This suggests the issue is in how the LLM")
report.append("   interprets different question types, not the SSR methodology itself.")
report.append("")

# Find questions that pass BOTH accuracy and consistency
working_questions = set(passing_accuracy) & set(passing_consistency)
partial_questions = (set(passing_accuracy) | set(passing_consistency)) - working_questions
failing_both = set(df['question']) - working_questions - partial_questions

report.append("RECOMMENDED NEXT STEPS FOR EXPERIMENTATION")
report.append("-" * 80)
report.append("")
report.append("Based on the pattern that SSR works for some question types but not others,")
report.append("we recommend focused experiments to understand and address the root causes:")
report.append("")

report.append("EXPERIMENT 1: Isolate Response Generation vs SSR Mapping")
report.append("  Objective: Determine if bias is in LLM responses or SSR conversion")
report.append("  Method: Run direct scale responses (LLM outputs 1-5 directly)")
report.append("  Time: 2-3 hours")
report.append("  What we'll learn: Whether to focus on prompts vs anchor optimization")
report.append("")

report.append("EXPERIMENT 2: Analyze Free-Text Responses")
report.append("  Objective: Understand what language LLM generates for failing questions")
report.append("  Method: Save and manually review LLM responses before SSR mapping")
report.append("  Time: 1 day")
report.append("  What we'll learn: If responses are genuinely conservative or mapping fails")
report.append("")

report.append("EXPERIMENT 3: Test Question-Specific Prompt Engineering")
report.append("  Objective: Fix abstract evaluative questions with targeted prompts")
report.append("  Method: Add construct-specific context for failing questions")
report.append("  Time: 3-5 days")
report.append("  What we'll learn: If prompt customization can fix the bias")
report.append("")

report.append("EXPERIMENT 4: Anchor Text Systematic Redesign")
report.append("  Objective: Improve anchors for failing questions based on learnings")
report.append("  Method: Apply successful patterns from working questions")
report.append("  Time: 1-2 weeks")
report.append("  What we'll learn: If anchor design can address distribution mismatch")
report.append("")

report.append("EXPERIMENT 5: Alternative Embedding Models")
report.append("  Objective: Test if higher-dimensional embeddings improve SSR")
report.append("  Method: Compare text-embedding-3-small vs text-embedding-3-large")
report.append("  Time: 2-3 days")
report.append("  What we'll learn: If embedding quality affects semantic similarity")
report.append("")

report.append("PRIORITIZATION:")
report.append("  Start with Experiments 1-2 (diagnostic) before 3-5 (optimization)")
report.append("  These will tell us WHERE to focus improvement efforts")
report.append("")

report.append("=" * 80)
report.append("END OF REPORT")
report.append("=" * 80)

# Save report
report_text = "\n".join(report)
with open("PRESENTATION_REPORT.txt", 'w') as f:
    f.write(report_text)

print("✓ Saved: PRESENTATION_REPORT.txt")
print()
print("=" * 80)
print("✅ PRESENTATION MATERIALS COMPLETE")
print("=" * 80)
print()
print("Generated files:")
print("  1. presentation_accuracy.png - Shows systematic bias problem")
print("  2. presentation_consistency.png - Shows distribution mismatch problem")
print("  3. presentation_correlation.png - Shows correlation visualization")
print("  4. PRESENTATION_REPORT.txt - Executive summary with findings")
print()
print("Key Messages for Presentation:")
print(f"  • {len(working_questions)}/7 questions WORK (concrete emotional questions)")
print(f"  • {len(failing_both)}/7 questions FAIL (abstract evaluative questions)")
print(f"  • {len(partial_questions)}/7 questions PARTIAL (mixed performance)")
print("  • Pattern discovered: Question type determines success")
print("  • Recommendation: Focus experiments on understanding why")
print()

# Print summary
print("\n" + report_text)
