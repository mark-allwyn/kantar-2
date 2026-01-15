"""
Generate validation summary report for management presentation.

This script:
1. Finds all validation JSON files for the 4 US market studies
2. Extracts key metrics (KL divergence, KS similarity, correlation)
3. Generates summary tables and statistics
4. Creates visualizations (optional)
5. Outputs markdown summary for inclusion in reports
"""

import json
from pathlib import Path
from typing import Dict, List
import sys


def load_validation_results(study_id: str, market: str = "US") -> Dict:
    """Load validation results for a study/market."""
    validation_dir = Path(f"data/synthetic/kantar/{study_id}/{market}")

    # Find most recent validation file
    validation_files = list(validation_dir.glob("validation_*.json"))
    if not validation_files:
        return None

    latest_file = max(validation_files, key=lambda p: p.stat().st_mtime)

    with open(latest_file, 'r') as f:
        return json.load(f)


def extract_key_metrics(validation_data: Dict) -> Dict:
    """Extract key metrics from validation results."""
    if not validation_data or 'aggregate_metrics' not in validation_data:
        return None

    agg = validation_data['aggregate_metrics']
    success = validation_data.get('success_criteria', {})

    return {
        'mean_kl': agg.get('mean_kl_divergence'),
        'ks_similarity': agg.get('ks_similarity'),
        'mean_correlation': agg.get('mean_correlation'),
        'questions_validated': agg.get('questions_validated'),
        'kl_pass': success.get('kl_below_0_20', False),
        'ks_pass': success.get('ks_similarity_above_0_85', False),
        'corr_pass': success.get('correlation_above_0_85', False),
        'gt_count': validation_data.get('respondent_counts', {}).get('ground_truth'),
        'synthetic_count': validation_data.get('respondent_counts', {}).get('synthetic')
    }


def assess_overall_status(metrics: Dict) -> str:
    """Determine PASS/WARN/FAIL status."""
    if not metrics:
        return "NO DATA"

    passes = sum([
        metrics.get('kl_pass', False),
        metrics.get('ks_pass', False),
        metrics.get('corr_pass', False) if metrics.get('mean_correlation') else False
    ])

    if passes == 3:
        return "PASS"
    elif passes == 2:
        return "WARN"
    else:
        return "FAIL"


def generate_summary_table(studies_data: Dict[str, Dict]) -> str:
    """Generate markdown table with summary metrics."""

    lines = []
    lines.append("## Validation Summary - 4 US Market Studies")
    lines.append("")
    lines.append("| Study | Concepts | GT n | Syn n | KL Div | KS Sim | Correlation | Status |")
    lines.append("|-------|----------|------|-------|--------|--------|-------------|---------|")

    for study_id, data in studies_data.items():
        study_name = data['name']
        concepts = data['concepts']
        metrics = data['metrics']
        status = data['status']

        if metrics:
            kl = f"{metrics['mean_kl']:.3f}" if metrics['mean_kl'] else "N/A"
            ks = f"{metrics['ks_similarity']:.3f}" if metrics['ks_similarity'] else "N/A"
            corr = f"{metrics['mean_correlation']:.3f}" if metrics['mean_correlation'] else "N/A"
            gt_n = metrics.get('gt_count', 'N/A')
            syn_n = metrics.get('synthetic_count', 'N/A')
        else:
            kl = ks = corr = "N/A"
            gt_n = syn_n = "N/A"

        status_emoji = {
            "PASS": "✅",
            "WARN": "⚠️",
            "FAIL": "❌",
            "NO DATA": "⏳"
        }.get(status, "")

        lines.append(f"| {study_id} | {concepts} | {gt_n} | {syn_n} | {kl} | {ks} | {corr} | {status_emoji} {status} |")

    lines.append("")
    lines.append("**Targets:** KL < 0.20, KS > 0.85, Correlation > 0.85")
    lines.append("")

    return "\n".join(lines)


def generate_detailed_breakdown(studies_data: Dict[str, Dict]) -> str:
    """Generate detailed breakdown per study."""

    lines = []
    lines.append("## Detailed Study Breakdown")
    lines.append("")

    for study_id, data in sorted(studies_data.items()):
        study_name = data['name']
        concepts = data['concepts']
        metrics = data['metrics']
        status = data['status']
        notes = data.get('notes', '')

        lines.append(f"### {study_id} - {study_name}")
        lines.append(f"**Complexity:** {concepts} concepts | **Status:** {status}")
        lines.append("")

        if metrics:
            lines.append("| Metric | Value | Target | Pass |")
            lines.append("|--------|-------|--------|------|")

            kl_val = f"{metrics['mean_kl']:.4f}" if metrics['mean_kl'] else "N/A"
            kl_pass = "✅" if metrics.get('kl_pass') else "❌"
            lines.append(f"| KL Divergence | {kl_val} | < 0.20 | {kl_pass} |")

            ks_val = f"{metrics['ks_similarity']:.4f}" if metrics['ks_similarity'] else "N/A"
            ks_pass = "✅" if metrics.get('ks_pass') else "❌"
            lines.append(f"| KS Similarity | {ks_val} | > 0.85 | {ks_pass} |")

            if metrics.get('mean_correlation'):
                corr_val = f"{metrics['mean_correlation']:.4f}"
                corr_pass = "✅" if metrics.get('corr_pass') else "❌"
                lines.append(f"| Correlation | {corr_val} | > 0.85 | {corr_pass} |")

            lines.append("")
            lines.append(f"**Questions Validated:** {metrics.get('questions_validated', 'N/A')}")
            lines.append(f"**Sample Sizes:** GT={metrics.get('gt_count', 'N/A')}, Synthetic={metrics.get('synthetic_count', 'N/A')}")
        else:
            lines.append("⏳ *Validation pending - generation in progress*")

        if notes:
            lines.append("")
            lines.append(f"**Notes:** {notes}")

        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def calculate_cross_study_stats(studies_data: Dict[str, Dict]) -> str:
    """Calculate cross-study statistics."""

    valid_metrics = [d['metrics'] for d in studies_data.values() if d['metrics']]

    if not valid_metrics:
        return "## Cross-Study Statistics\n\n⏳ *No validation data available yet*\n"

    lines = []
    lines.append("## Cross-Study Statistics")
    lines.append("")

    # Calculate averages
    kl_values = [m['mean_kl'] for m in valid_metrics if m['mean_kl'] is not None]
    ks_values = [m['ks_similarity'] for m in valid_metrics if m['ks_similarity'] is not None]
    corr_values = [m['mean_correlation'] for m in valid_metrics if m['mean_correlation'] is not None]

    if kl_values:
        lines.append(f"**Mean KL Divergence:** {sum(kl_values)/len(kl_values):.4f} (target: < 0.20)")
    if ks_values:
        lines.append(f"**Mean KS Similarity:** {sum(ks_values)/len(ks_values):.4f} (target: > 0.85)")
    if corr_values:
        lines.append(f"**Mean Correlation:** {sum(corr_values)/len(corr_values):.4f} (target: > 0.85)")

    lines.append("")

    # Overall assessment
    passes = sum(1 for d in studies_data.values() if d['status'] == 'PASS')
    warns = sum(1 for d in studies_data.values() if d['status'] == 'WARN')
    fails = sum(1 for d in studies_data.values() if d['status'] == 'FAIL')
    pending = sum(1 for d in studies_data.values() if d['status'] == 'NO DATA')

    lines.append(f"**Overall Results:** {passes} PASS, {warns} WARN, {fails} FAIL, {pending} PENDING")
    lines.append("")

    if passes + warns == len(studies_data) - pending:
        lines.append("✅ **Assessment:** System performs adequately for screening use")
    elif passes >= 2:
        lines.append("⚠️ **Assessment:** System shows promise but requires review of failed studies")
    else:
        lines.append("❌ **Assessment:** System requires calibration before use")

    lines.append("")

    return "\n".join(lines)


def main():
    """Main execution."""

    # Define studies to validate
    studies = {
        '61405445-01': {
            'name': 'iGaming Concept Evaluate',
            'concepts': 5,
            'notes': 'Baseline complexity study'
        },
        '61407017': {
            'name': '24 Ideas Screening',
            'concepts': 24,
            'notes': 'Maximum complexity study. 1 concept unmatched (Wealth Buddy)'
        },
        '61407069': {
            'name': 'Tech-Enabled ScratchCards',
            'concepts': 8,
            'notes': 'Only 3/8 concepts matched. 5 concepts had naming mismatches'
        },
        '61407185': {
            'name': 'Innovation Concepts 2025',
            'concepts': 8,
            'notes': '6/8 concepts matched. 2 concepts unmatched (Drop\'d, Goals Feel Better Together)'
        }
    }

    print("=" * 80)
    print("SYNTHETIC SURVEY DATA VALIDATION SUMMARY")
    print("=" * 80)
    print()

    # Load validation results for each study
    for study_id in studies.keys():
        print(f"Loading validation results for {study_id}...")
        validation_data = load_validation_results(study_id)

        if validation_data:
            metrics = extract_key_metrics(validation_data)
            status = assess_overall_status(metrics)
            studies[study_id]['metrics'] = metrics
            studies[study_id]['status'] = status
            print(f"  ✓ Found validation data - Status: {status}")
        else:
            studies[study_id]['metrics'] = None
            studies[study_id]['status'] = "NO DATA"
            print(f"  ⚠️ No validation data found")

    print()

    # Generate summary
    print("Generating summary report...")

    output_lines = []
    output_lines.append("# Validation Summary Report")
    output_lines.append("")
    output_lines.append(f"**Generated:** {Path('.').absolute()}")
    output_lines.append("")
    output_lines.append("---")
    output_lines.append("")

    # Summary table
    output_lines.append(generate_summary_table(studies))
    output_lines.append("")

    # Cross-study stats
    output_lines.append(calculate_cross_study_stats(studies))
    output_lines.append("")

    # Detailed breakdown
    output_lines.append(generate_detailed_breakdown(studies))

    # Write to file
    output_file = Path("VALIDATION_SUMMARY.md")
    with open(output_file, 'w') as f:
        f.write("\n".join(output_lines))

    print(f"✓ Summary report written to: {output_file}")
    print()

    # Also print to console
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print("\n".join(output_lines))

    return 0


if __name__ == "__main__":
    sys.exit(main())
