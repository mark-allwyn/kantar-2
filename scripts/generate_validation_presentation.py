#!/usr/bin/env python3
"""
Generate Presentation-Ready Validation Report

Creates a comprehensive report comparing synthetic data generation
performance vs ground truth across all 4 Kantar studies.

This report is designed to demonstrate the capability and readiness
of the synthetic data generation system.
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

def load_validation_results():
    """Load validation results for all studies."""
    studies = {
        "61405445-01": {
            "name": "iGaming Concept Evaluate",
            "concepts": 5,
            "validation": "data/synthetic/kantar/61405445-01/US/validation_US_20260115_094742.json"
        },
        "61407017": {
            "name": "24 Ideas Screening",
            "concepts": 24,
            "validation": "data/synthetic/kantar/61407017/US/validation_US_20260115_094742.json"
        },
        "61407069": {
            "name": "Tech-Enabled ScratchCards",
            "concepts": 8,
            "validation": "data/synthetic/kantar/61407069/US/validation_US_20260115_094743.json"
        },
        "61407185": {
            "name": "Innovation Concepts 2025",
            "concepts": 8,
            "validation": "data/synthetic/kantar/61407185/US/validation_US_20260115_094743.json"
        }
    }

    for study_id, info in studies.items():
        val_path = Path(info["validation"])
        if val_path.exists():
            with open(val_path, 'r') as f:
                info["results"] = json.load(f)
        else:
            info["results"] = None

    return studies


def generate_markdown_report(studies):
    """Generate markdown validation report."""

    lines = []

    # Header
    lines.append("# Synthetic Survey Data Validation Report")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Executive Summary
    lines.append("## Executive Summary")
    lines.append("")
    lines.append("This report presents validation results comparing synthetic survey data generation")
    lines.append("against ground truth Kantar data across 4 US market studies. The goal is to")
    lines.append("demonstrate the system's capability to replace Kantar studies with synthetic")
    lines.append("generation for cost and efficiency savings.")
    lines.append("")

    # Key Findings
    lines.append("### Key Findings")
    lines.append("")

    # Calculate overall stats
    all_kl = []
    all_ks = []
    all_questions = []

    for study_id, info in studies.items():
        if info["results"] and "aggregate_metrics" in info["results"]:
            agg = info["results"]["aggregate_metrics"]
            if agg.get("mean_kl_divergence"):
                all_kl.append(agg["mean_kl_divergence"])
            if agg.get("ks_similarity"):
                all_ks.append(agg["ks_similarity"])
            if agg.get("questions_validated"):
                all_questions.append(agg["questions_validated"])

    if all_kl and all_ks:
        avg_kl = sum(all_kl) / len(all_kl)
        avg_ks = sum(all_ks) / len(all_ks)
        total_q = sum(all_questions)

        lines.append(f"- **Studies Validated:** {len(studies)} Kantar US market studies")
        lines.append(f"- **Total Questions Analyzed:** {total_q} question columns")
        lines.append(f"- **Average KL Divergence:** {avg_kl:.4f} (target: <0.20)")
        lines.append(f"- **Average KS Similarity:** {avg_ks:.4f} (target: >0.85)")
        lines.append("")

    # Data Quality Issues
    lines.append("### ⚠️ Data Quality Observations")
    lines.append("")
    lines.append("The validation revealed that synthetic data generation is **incomplete**:")
    lines.append("")
    lines.append("- **61405445-01**: 33/112 questions populated (29%)")
    lines.append("- **61407017**: 2/148 questions populated (1%) - Demographics only")
    lines.append("- **61407069**: 13/175 questions populated (7%)")
    lines.append("- **61407185**: 24/175 questions populated (14%)")
    lines.append("")
    lines.append("**Interpretation:** The generation pipeline may have encountered errors or")
    lines.append("timeouts during the January 14th run. Questions that *were* generated show")
    lines.append("varying quality metrics (see detailed results below).")
    lines.append("")

    lines.append("---")
    lines.append("")

    # Detailed Study Results
    lines.append("## Detailed Validation Results")
    lines.append("")

    for study_id, info in sorted(studies.items()):
        lines.append(f"### {study_id} - {info['name']}")
        lines.append("")
        lines.append(f"**Study Configuration:**")
        lines.append(f"- Concepts: {info['concepts']}")

        if not info["results"]:
            lines.append("")
            lines.append("⚠️ *No validation results available*")
            lines.append("")
            lines.append("---")
            lines.append("")
            continue

        results = info["results"]

        lines.append(f"- Ground Truth Respondents: {results['respondent_counts']['ground_truth']}")
        lines.append(f"- Synthetic Respondents: {results['respondent_counts']['synthetic']}")
        lines.append(f"- Total Question Columns: {results['column_counts']['questions']}")
        lines.append("")

        if "aggregate_metrics" in results:
            agg = results["aggregate_metrics"]
            lines.append("**Validation Metrics:**")
            lines.append("")
            lines.append("| Metric | Value | Target | Status |")
            lines.append("|--------|-------|--------|---------|")

            kl = agg.get("mean_kl_divergence")
            if kl is not None:
                kl_status = "✅ Pass" if kl < 0.20 else "⚠️ Review" if kl < 1.0 else "❌ Fail"
                lines.append(f"| Mean KL Divergence | {kl:.4f} | < 0.20 | {kl_status} |")

            ks = agg.get("ks_similarity")
            if ks is not None:
                ks_status = "✅ Pass" if ks > 0.85 else "⚠️ Review" if ks > 0.75 else "❌ Fail"
                lines.append(f"| KS Similarity | {ks:.4f} | > 0.85 | {ks_status} |")

            q_validated = agg.get("questions_validated", 0)
            q_total = results['column_counts']['questions']
            pct_complete = (q_validated / q_total * 100) if q_total > 0 else 0
            complete_status = "✅ Complete" if pct_complete > 90 else "⚠️ Partial" if pct_complete > 20 else "❌ Incomplete"
            lines.append(f"| Questions Validated | {q_validated}/{q_total} ({pct_complete:.0f}%) | 100% | {complete_status} |")

            lines.append("")

        # Success Criteria
        if "success_criteria" in results:
            criteria = results["success_criteria"]
            lines.append("**Success Criteria:**")
            lines.append("")
            for key, value in criteria.items():
                status = "✅" if value else "❌"
                label = key.replace("_", " ").title()
                lines.append(f"- {status} {label}")
            lines.append("")

        lines.append("---")
        lines.append("")

    # Metrics Explanation
    lines.append("## Metrics Explanation")
    lines.append("")
    lines.append("### KL Divergence (Kullback-Leibler)")
    lines.append("Measures how different the synthetic distribution is from ground truth.")
    lines.append("- **0.0**: Perfect match")
    lines.append("- **< 0.20**: Excellent similarity (target)")
    lines.append("- **> 1.0**: Significant divergence")
    lines.append("")
    lines.append("### KS Similarity (Kolmogorov-Smirnov)")
    lines.append("Measures distributional similarity (1 - KS statistic).")
    lines.append("- **1.0**: Perfect match")
    lines.append("- **> 0.85**: High similarity (target)")
    lines.append("- **< 0.75**: Poor similarity")
    lines.append("")

    # Next Steps
    lines.append("---")
    lines.append("")
    lines.append("## Recommendations & Next Steps")
    lines.append("")
    lines.append("### Immediate Actions")
    lines.append("")
    lines.append("1. **Investigate Generation Failures**")
    lines.append("   - Review logs from January 14th runs to identify why most questions weren't populated")
    lines.append("   - Check for timeout errors, API failures, or logic bugs")
    lines.append("")
    lines.append("2. **Re-run Generation with Full Completion**")
    lines.append("   - Execute new 50-respondent runs ensuring all questions are generated")
    lines.append("   - Monitor progress to catch failures early")
    lines.append("")
    lines.append("3. **Address High KL Divergence**")
    lines.append("   - For studies with KL > 1.0, review question generation logic")
    lines.append("   - Check if distribution calibration is working correctly")
    lines.append("   - Verify persona generation is using proper ground truth schemas")
    lines.append("")
    lines.append("### Success Path Forward")
    lines.append("")
    lines.append("Once generation completes successfully:")
    lines.append("- Re-validate with all questions populated")
    lines.append("- Generate visualization dashboards showing distribution comparisons")
    lines.append("- Create concept ranking correlation analysis")
    lines.append("- Prepare executive presentation with confidence intervals")
    lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append(f"*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    lines.append("")

    return "\n".join(lines)


def main():
    """Generate validation presentation report."""
    print("Loading validation results...")
    studies = load_validation_results()

    print("Generating markdown report...")
    report = generate_markdown_report(studies)

    output_file = Path("VALIDATION_PRESENTATION_REPORT.md")
    with open(output_file, 'w') as f:
        f.write(report)

    print(f"\n✅ Report generated: {output_file}")
    print(f"   File size: {output_file.stat().st_size} bytes")
    print(f"\nYou can view the report or convert to PDF for presentation.")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
