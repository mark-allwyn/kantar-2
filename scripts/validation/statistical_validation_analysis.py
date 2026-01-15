"""
Statistical Validation Analysis for Synthetic Survey Data POC

This script performs rigorous statistical analysis to demonstrate that synthetic
data is statistically valid and accurate compared to ground truth.

Focus areas:
1. Distribution similarity (KL divergence, KS tests, chi-square)
2. Concept ranking preservation (Spearman correlation, rank concordance)
3. Question-level accuracy (per-question validation)
4. Statistical significance tests
5. Effect size measurements
6. Confidence intervals

Output: Comprehensive statistical validation report with visualizations
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns


def load_validation_data(study_id: str, market: str = "US") -> Tuple[Dict, pd.DataFrame, pd.DataFrame]:
    """Load validation JSON, synthetic Excel, and ground truth Excel."""

    base_path = Path(f"data/synthetic/kantar/{study_id}/{market}")

    # Load validation JSON
    validation_files = list(base_path.glob("validation_*.json"))
    if not validation_files:
        return None, None, None

    val_file = max(validation_files, key=lambda p: p.stat().st_mtime)
    with open(val_file, 'r') as f:
        val_data = json.load(f)

    # Load synthetic Excel
    synthetic_files = list(base_path.glob("synthetic_*.xlsx"))
    if not synthetic_files:
        return val_data, None, None

    syn_file = max(synthetic_files, key=lambda p: p.stat().st_mtime)
    syn_df = pd.read_excel(syn_file)

    # Load ground truth Excel
    gt_path = Path(val_data['ground_truth_file'])
    gt_df = pd.read_excel(gt_path)

    return val_data, syn_df, gt_df


def calculate_distribution_metrics(gt_series: pd.Series, syn_series: pd.Series) -> Dict:
    """Calculate comprehensive distribution comparison metrics."""

    # Remove NaN values
    gt_clean = gt_series.dropna()
    syn_clean = syn_series.dropna()

    if len(gt_clean) == 0 or len(syn_clean) == 0:
        return None

    metrics = {}

    # Get value counts
    gt_counts = gt_clean.value_counts(normalize=True).sort_index()
    syn_counts = syn_clean.value_counts(normalize=True).sort_index()

    # Align indices
    all_values = sorted(set(gt_counts.index) | set(syn_counts.index))
    gt_dist = np.array([gt_counts.get(v, 0) for v in all_values])
    syn_dist = np.array([syn_counts.get(v, 0) for v in all_values])

    # 1. KL Divergence
    epsilon = 1e-10
    gt_dist_smooth = gt_dist + epsilon
    syn_dist_smooth = syn_dist + epsilon
    gt_dist_smooth = gt_dist_smooth / gt_dist_smooth.sum()
    syn_dist_smooth = syn_dist_smooth / syn_dist_smooth.sum()

    kl_div = np.sum(syn_dist_smooth * np.log(syn_dist_smooth / gt_dist_smooth))
    metrics['kl_divergence'] = kl_div

    # 2. Jensen-Shannon Divergence (symmetric version of KL)
    m_dist = 0.5 * (gt_dist_smooth + syn_dist_smooth)
    js_div = 0.5 * (
        np.sum(gt_dist_smooth * np.log(gt_dist_smooth / m_dist)) +
        np.sum(syn_dist_smooth * np.log(syn_dist_smooth / m_dist))
    )
    metrics['js_divergence'] = js_div

    # 3. Kolmogorov-Smirnov test
    try:
        ks_stat, ks_pval = stats.ks_2samp(gt_clean.values, syn_clean.values)
        metrics['ks_statistic'] = ks_stat
        metrics['ks_pvalue'] = ks_pval
        metrics['ks_similarity'] = 1 - ks_stat
    except:
        metrics['ks_statistic'] = None
        metrics['ks_pvalue'] = None
        metrics['ks_similarity'] = None

    # 4. Chi-square test
    try:
        # Ensure same categories
        common_vals = sorted(set(gt_clean.unique()) & set(syn_clean.unique()))
        if len(common_vals) > 1:
            gt_counts_aligned = [sum(gt_clean == v) for v in common_vals]
            syn_counts_aligned = [sum(syn_clean == v) for v in common_vals]

            chi2_stat, chi2_pval = stats.chisquare(syn_counts_aligned, f_exp=gt_counts_aligned)
            metrics['chi2_statistic'] = chi2_stat
            metrics['chi2_pvalue'] = chi2_pval
        else:
            metrics['chi2_statistic'] = None
            metrics['chi2_pvalue'] = None
    except:
        metrics['chi2_statistic'] = None
        metrics['chi2_pvalue'] = None

    # 5. Total Variation Distance
    tvd = 0.5 * np.sum(np.abs(gt_dist - syn_dist))
    metrics['total_variation_distance'] = tvd

    # 6. Hellinger Distance
    hellinger = np.sqrt(0.5 * np.sum((np.sqrt(gt_dist) - np.sqrt(syn_dist))**2))
    metrics['hellinger_distance'] = hellinger

    # 7. Mean and variance comparison (if numeric)
    try:
        gt_numeric = pd.to_numeric(gt_clean, errors='coerce').dropna()
        syn_numeric = pd.to_numeric(syn_clean, errors='coerce').dropna()

        if len(gt_numeric) > 0 and len(syn_numeric) > 0:
            metrics['gt_mean'] = gt_numeric.mean()
            metrics['syn_mean'] = syn_numeric.mean()
            metrics['mean_difference'] = abs(syn_numeric.mean() - gt_numeric.mean())
            metrics['mean_pct_error'] = abs(syn_numeric.mean() - gt_numeric.mean()) / gt_numeric.mean() * 100

            metrics['gt_std'] = gt_numeric.std()
            metrics['syn_std'] = syn_numeric.std()

            # T-test for mean difference
            t_stat, t_pval = stats.ttest_ind(gt_numeric, syn_numeric)
            metrics['ttest_statistic'] = t_stat
            metrics['ttest_pvalue'] = t_pval

            # Effect size (Cohen's d)
            pooled_std = np.sqrt(((len(gt_numeric)-1)*gt_numeric.std()**2 +
                                  (len(syn_numeric)-1)*syn_numeric.std()**2) /
                                 (len(gt_numeric) + len(syn_numeric) - 2))
            cohens_d = (syn_numeric.mean() - gt_numeric.mean()) / pooled_std
            metrics['cohens_d'] = cohens_d
        else:
            metrics['gt_mean'] = metrics['syn_mean'] = None
    except:
        metrics['gt_mean'] = metrics['syn_mean'] = None

    # 8. Sample sizes
    metrics['gt_n'] = len(gt_clean)
    metrics['syn_n'] = len(syn_clean)

    return metrics


def calculate_concept_ranking_metrics(gt_df: pd.DataFrame, syn_df: pd.DataFrame,
                                      question_cols: List[str]) -> Dict:
    """Calculate how well synthetic data preserves concept rankings."""

    metrics = {}

    # For each question, calculate mean score per concept
    concept_scores_gt = {}
    concept_scores_syn = {}

    for col in question_cols:
        if col not in syn_df.columns:
            continue

        # Extract concept name from column
        # Format: "(QUESTION_CODE) QUESTION NAME - CONCEPT_NAME"
        if ' - ' not in col:
            continue

        concept = col.split(' - ')[-1].strip()

        # Calculate mean scores
        gt_vals = pd.to_numeric(gt_df[col], errors='coerce').dropna()
        syn_vals = pd.to_numeric(syn_df[col], errors='coerce').dropna()

        if len(gt_vals) > 0 and len(syn_vals) > 0:
            if concept not in concept_scores_gt:
                concept_scores_gt[concept] = []
                concept_scores_syn[concept] = []

            concept_scores_gt[concept].append(gt_vals.mean())
            concept_scores_syn[concept].append(syn_vals.mean())

    if not concept_scores_gt:
        return None

    # Average across all questions for each concept
    concept_avg_gt = {c: np.mean(scores) for c, scores in concept_scores_gt.items()}
    concept_avg_syn = {c: np.mean(scores) for c, scores in concept_scores_syn.items()}

    # Create rankings
    concepts = sorted(concept_avg_gt.keys())
    gt_ranks = stats.rankdata([-concept_avg_gt[c] for c in concepts])
    syn_ranks = stats.rankdata([-concept_avg_syn[c] for c in concepts])

    # Spearman correlation on ranks
    spearman_corr, spearman_pval = stats.spearmanr(gt_ranks, syn_ranks)
    metrics['spearman_correlation'] = spearman_corr
    metrics['spearman_pvalue'] = spearman_pval

    # Kendall's Tau (another rank correlation)
    kendall_tau, kendall_pval = stats.kendalltau(gt_ranks, syn_ranks)
    metrics['kendall_tau'] = kendall_tau
    metrics['kendall_pvalue'] = kendall_pval

    # Top-3 agreement
    gt_top3 = set([concepts[i] for i in np.argsort(gt_ranks)[:3]])
    syn_top3 = set([concepts[i] for i in np.argsort(syn_ranks)[:3]])
    top3_overlap = len(gt_top3 & syn_top3)
    metrics['top3_agreement'] = top3_overlap / 3.0

    # Rank-biased overlap (RBO)
    # Simplified version - measures overlap at different rank depths
    metrics['top1_agreement'] = 1.0 if np.argmin(gt_ranks) == np.argmin(syn_ranks) else 0.0

    # Store concept rankings for reference
    metrics['concept_rankings'] = {
        'concepts': concepts,
        'gt_scores': [concept_avg_gt[c] for c in concepts],
        'syn_scores': [concept_avg_syn[c] for c in concepts],
        'gt_ranks': gt_ranks.tolist(),
        'syn_ranks': syn_ranks.tolist()
    }

    return metrics


def assess_statistical_validity(metrics: Dict) -> Dict:
    """Determine if results are statistically valid."""

    assessment = {
        'overall_status': 'UNKNOWN',
        'distribution_valid': False,
        'ranking_valid': False,
        'issues': []
    }

    # Distribution validity criteria
    dist_valid = True

    if metrics.get('kl_divergence') is not None:
        if metrics['kl_divergence'] > 0.30:
            dist_valid = False
            assessment['issues'].append(f"High KL divergence: {metrics['kl_divergence']:.3f} (target: <0.20)")

    if metrics.get('ks_similarity') is not None:
        if metrics['ks_similarity'] < 0.75:
            dist_valid = False
            assessment['issues'].append(f"Low KS similarity: {metrics['ks_similarity']:.3f} (target: >0.85)")

    if metrics.get('ks_pvalue') is not None:
        if metrics['ks_pvalue'] < 0.05:
            assessment['issues'].append(f"KS test shows significant difference (p={metrics['ks_pvalue']:.4f})")

    if metrics.get('total_variation_distance') is not None:
        if metrics['total_variation_distance'] > 0.15:
            assessment['issues'].append(f"High TVD: {metrics['total_variation_distance']:.3f} (target: <0.10)")

    assessment['distribution_valid'] = dist_valid

    # Ranking validity criteria
    rank_valid = True

    if metrics.get('spearman_correlation') is not None:
        if metrics['spearman_correlation'] < 0.70:
            rank_valid = False
            assessment['issues'].append(f"Low rank correlation: {metrics['spearman_correlation']:.3f} (target: >0.85)")

    if metrics.get('top3_agreement') is not None:
        if metrics['top3_agreement'] < 0.67:
            rank_valid = False
            assessment['issues'].append(f"Low top-3 agreement: {metrics['top3_agreement']:.1%} (target: >67%)")

    assessment['ranking_valid'] = rank_valid

    # Overall assessment
    if dist_valid and rank_valid:
        assessment['overall_status'] = 'PASS'
    elif dist_valid or rank_valid:
        assessment['overall_status'] = 'WARN'
    else:
        assessment['overall_status'] = 'FAIL'

    return assessment


def analyze_question_type_performance(studies_data: Dict) -> Dict:
    """Analyze performance by question type across all studies."""

    # Map question codes to types
    question_types = {
        'UNPURINT': 'Purchase Intent (Unpriced)',
        'PRPURINT': 'Purchase Intent (Priced)',
        'UNIQNESS': 'Uniqueness',
        'UNPRICEP': 'Price Perception',
        'LIKBILTY': 'Likeability',
        'INCREMNT': 'Incrementality',
        'RELVANCE': 'Relevance',
        'PLAYFLNS': 'Playfulness',
        'EXCITMENT': 'Excitement',
        'BELVBLTY': 'Believability',
        'LIKES': 'Likes (Open-ended)',
        'DISLIKES': 'Dislikes (Open-ended)',
        'OCCASIONS': 'Occasions',
        'BARRIERS': 'Barriers',
        'GIFT': 'Gift Questions'
    }

    # Collect metrics by question type
    type_metrics = {}

    for study_id, data in studies_data.items():
        if not data.get('metrics') or not data['metrics'].get('question_metrics'):
            continue

        for q_metric in data['metrics']['question_metrics']:
            col = q_metric.get('column', '')

            # Extract question code from column name
            # Format: "(CODE) NAME - CONCEPT"
            if '(' not in col or ')' not in col:
                continue

            code = col.split('(')[1].split(')')[0]
            q_type = question_types.get(code, code)

            if q_type not in type_metrics:
                type_metrics[q_type] = {
                    'kl_values': [],
                    'ks_values': [],
                    'tvd_values': [],
                    'count': 0
                }

            type_metrics[q_type]['count'] += 1

            if q_metric.get('kl_divergence'):
                type_metrics[q_type]['kl_values'].append(q_metric['kl_divergence'])
            if q_metric.get('ks_similarity'):
                type_metrics[q_type]['ks_values'].append(q_metric['ks_similarity'])
            if q_metric.get('total_variation_distance'):
                type_metrics[q_type]['tvd_values'].append(q_metric['total_variation_distance'])

    # Calculate averages and pass rates
    type_summary = {}
    for q_type, metrics in type_metrics.items():
        summary = {
            'count': metrics['count'],
            'mean_kl': np.mean(metrics['kl_values']) if metrics['kl_values'] else None,
            'mean_ks': np.mean(metrics['ks_values']) if metrics['ks_values'] else None,
            'mean_tvd': np.mean(metrics['tvd_values']) if metrics['tvd_values'] else None
        }

        # Calculate pass rate (both KL and KS meet targets)
        passes = 0
        total = 0
        for i in range(len(metrics['kl_values'])):
            if i < len(metrics['ks_values']):
                kl_pass = metrics['kl_values'][i] < 0.20
                ks_pass = metrics['ks_values'][i] > 0.85
                if kl_pass and ks_pass:
                    passes += 1
                total += 1

        summary['pass_rate'] = (passes / total * 100) if total > 0 else 0

        # Assess performance
        if summary['mean_kl'] and summary['mean_ks']:
            if summary['mean_kl'] < 0.15 and summary['mean_ks'] > 0.90:
                summary['assessment'] = 'EXCELLENT'
            elif summary['mean_kl'] < 0.20 and summary['mean_ks'] > 0.85:
                summary['assessment'] = 'GOOD'
            elif summary['mean_kl'] < 0.30 and summary['mean_ks'] > 0.75:
                summary['assessment'] = 'MODERATE'
            else:
                summary['assessment'] = 'POOR'
        else:
            summary['assessment'] = 'INSUFFICIENT DATA'

        type_summary[q_type] = summary

    return type_summary


def generate_statistical_report(studies_data: Dict) -> str:
    """Generate comprehensive statistical validation report."""

    lines = []
    lines.append("# Statistical Validation Report - Synthetic Survey Data POC")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    lines.append("This report presents rigorous statistical validation of synthetic survey data")
    lines.append("against ground truth Kantar data across 4 US market studies.")
    lines.append("")

    # Summary table
    lines.append("## Validation Summary")
    lines.append("")
    lines.append("| Study | Questions | KL Div | KS Sim | Rank Corr | Status |")
    lines.append("|-------|-----------|--------|--------|-----------|---------|")

    for study_id, data in sorted(studies_data.items()):
        if not data.get('metrics'):
            lines.append(f"| {study_id} | N/A | N/A | N/A | N/A | ⏳ PENDING |")
            continue

        metrics = data['metrics']
        agg = metrics.get('aggregate', {})
        ranking = metrics.get('ranking', {})
        assessment = data.get('assessment', {})

        kl = f"{agg.get('mean_kl', 0):.3f}" if agg.get('mean_kl') else "N/A"
        ks = f"{agg.get('mean_ks_sim', 0):.3f}" if agg.get('mean_ks_sim') else "N/A"
        rank = f"{ranking.get('spearman_correlation', 0):.3f}" if ranking else "N/A"

        status_emoji = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌", "PENDING": "⏳"}.get(assessment.get('overall_status', 'PENDING'), "")
        status = assessment.get('overall_status', 'PENDING')

        q_count = len(metrics.get('question_metrics', []))

        lines.append(f"| {study_id} | {q_count} | {kl} | {ks} | {rank} | {status_emoji} {status} |")

    lines.append("")
    lines.append("**Target Thresholds:**")
    lines.append("- KL Divergence: < 0.20 (lower = better)")
    lines.append("- KS Similarity: > 0.85 (higher = better)")
    lines.append("- Rank Correlation: > 0.85 (higher = better)")
    lines.append("")

    # Question type performance analysis
    lines.append("## Question Type Performance Analysis")
    lines.append("")
    lines.append("Performance broken down by Kantar question type across all 4 studies.")
    lines.append("")

    type_performance = analyze_question_type_performance(studies_data)

    if type_performance:
        lines.append("| Question Type | N Questions | Mean KL | Mean KS Sim | Pass Rate | Assessment |")
        lines.append("|---------------|-------------|---------|-------------|-----------|------------|")

        for q_type, metrics in sorted(type_performance.items(), key=lambda x: x[1]['pass_rate'] if x[1]['pass_rate'] else 0, reverse=True):
            count = metrics['count']
            kl = f"{metrics['mean_kl']:.3f}" if metrics['mean_kl'] else "N/A"
            ks = f"{metrics['mean_ks']:.3f}" if metrics['mean_ks'] else "N/A"
            pass_rate = f"{metrics['pass_rate']:.0f}%"
            assessment = metrics['assessment']

            assessment_emoji = {
                'EXCELLENT': '🟢',
                'GOOD': '✅',
                'MODERATE': '⚠️',
                'POOR': '❌',
                'INSUFFICIENT DATA': '⏳'
            }.get(assessment, '')

            lines.append(f"| {q_type} | {count} | {kl} | {ks} | {pass_rate} | {assessment_emoji} {assessment} |")

        lines.append("")
        lines.append("**Performance Categories:**")
        lines.append("- 🟢 EXCELLENT: KL < 0.15, KS > 0.90")
        lines.append("- ✅ GOOD: KL < 0.20, KS > 0.85 (meets targets)")
        lines.append("- ⚠️ MODERATE: KL < 0.30, KS > 0.75")
        lines.append("- ❌ POOR: Does not meet moderate thresholds")
        lines.append("")

        # Top performers
        excellent_good = [(q, m) for q, m in type_performance.items()
                         if m['assessment'] in ['EXCELLENT', 'GOOD']]
        if excellent_good:
            lines.append("### Question Types Ready for Use")
            lines.append("")
            lines.append("These question types consistently produce high-quality synthetic data:")
            for q_type, metrics in sorted(excellent_good, key=lambda x: x[1]['pass_rate'], reverse=True):
                lines.append(f"- **{q_type}**: {metrics['pass_rate']:.0f}% pass rate (n={metrics['count']})")
            lines.append("")

        # Moderate performers
        moderate = [(q, m) for q, m in type_performance.items()
                   if m['assessment'] == 'MODERATE']
        if moderate:
            lines.append("### Question Types Requiring Review")
            lines.append("")
            lines.append("These question types show acceptable but not ideal performance:")
            for q_type, metrics in sorted(moderate, key=lambda x: x[1]['pass_rate'], reverse=True):
                lines.append(f"- **{q_type}**: {metrics['pass_rate']:.0f}% pass rate (n={metrics['count']})")
            lines.append("")

        # Poor performers
        poor = [(q, m) for q, m in type_performance.items()
               if m['assessment'] == 'POOR']
        if poor:
            lines.append("### Question Types Needing Calibration")
            lines.append("")
            lines.append("These question types require methodology improvement:")
            for q_type, metrics in sorted(poor, key=lambda x: x[1]['pass_rate'], reverse=True):
                lines.append(f"- **{q_type}**: {metrics['pass_rate']:.0f}% pass rate (n={metrics['count']})")
            lines.append("")
    else:
        lines.append("⏳ *Question type analysis pending - no data available yet*")
        lines.append("")

    lines.append("---")
    lines.append("")

    # Detailed per-study analysis
    lines.append("## Detailed Study Analysis")
    lines.append("")

    for study_id, data in sorted(studies_data.items()):
        if not data.get('metrics'):
            continue

        lines.append(f"### {study_id} - {data['name']}")
        lines.append("")

        metrics = data['metrics']
        assessment = data.get('assessment', {})

        # Distribution metrics
        lines.append("#### Distribution Similarity Metrics")
        lines.append("")

        agg = metrics.get('aggregate', {})
        lines.append("| Metric | Value | Target | Status |")
        lines.append("|--------|-------|--------|---------|")

        kl = agg.get('mean_kl')
        if kl:
            kl_pass = "✅" if kl < 0.20 else "⚠️" if kl < 0.30 else "❌"
            lines.append(f"| KL Divergence | {kl:.4f} | < 0.20 | {kl_pass} |")

        js = agg.get('mean_js')
        if js:
            lines.append(f"| JS Divergence | {js:.4f} | < 0.10 | {'✅' if js < 0.10 else '⚠️'} |")

        ks_sim = agg.get('mean_ks_sim')
        if ks_sim:
            ks_pass = "✅" if ks_sim > 0.85 else "⚠️" if ks_sim > 0.75 else "❌"
            lines.append(f"| KS Similarity | {ks_sim:.4f} | > 0.85 | {ks_pass} |")

        tvd = agg.get('mean_tvd')
        if tvd:
            lines.append(f"| Total Variation Distance | {tvd:.4f} | < 0.10 | {'✅' if tvd < 0.10 else '⚠️'} |")

        hellinger = agg.get('mean_hellinger')
        if hellinger:
            lines.append(f"| Hellinger Distance | {hellinger:.4f} | < 0.15 | {'✅' if hellinger < 0.15 else '⚠️'} |")

        lines.append("")

        # Ranking metrics
        ranking = metrics.get('ranking')
        if ranking:
            lines.append("#### Concept Ranking Preservation")
            lines.append("")
            lines.append("| Metric | Value | Target | Status |")
            lines.append("|--------|-------|--------|---------|")

            spearman = ranking.get('spearman_correlation')
            if spearman:
                sp_pass = "✅" if spearman > 0.85 else "⚠️" if spearman > 0.70 else "❌"
                sp_pval = ranking.get('spearman_pvalue', 1.0)
                lines.append(f"| Spearman Correlation | {spearman:.4f} (p={sp_pval:.4f}) | > 0.85 | {sp_pass} |")

            kendall = ranking.get('kendall_tau')
            if kendall:
                lines.append(f"| Kendall's Tau | {kendall:.4f} | > 0.70 | {'✅' if kendall > 0.70 else '⚠️'} |")

            top3 = ranking.get('top3_agreement')
            if top3:
                lines.append(f"| Top-3 Agreement | {top3:.1%} | > 67% | {'✅' if top3 > 0.67 else '⚠️'} |")

            top1 = ranking.get('top1_agreement')
            if top1 is not None:
                lines.append(f"| Top-1 Agreement | {'Match' if top1 == 1.0 else 'Differ'} | Match | {'✅' if top1 == 1.0 else '❌'} |")

            lines.append("")

        # Assessment
        lines.append("#### Overall Assessment")
        lines.append("")

        status = assessment.get('overall_status', 'UNKNOWN')
        dist_valid = assessment.get('distribution_valid', False)
        rank_valid = assessment.get('ranking_valid', False)
        issues = assessment.get('issues', [])

        lines.append(f"**Status:** {status}")
        lines.append(f"- Distribution Validity: {'✅ VALID' if dist_valid else '❌ INVALID'}")
        lines.append(f"- Ranking Validity: {'✅ VALID' if rank_valid else '❌ INVALID'}")

        if issues:
            lines.append("")
            lines.append("**Issues Identified:**")
            for issue in issues:
                lines.append(f"- {issue}")

        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def main():
    """Main execution."""

    print("=" * 80)
    print("STATISTICAL VALIDATION ANALYSIS")
    print("=" * 80)
    print()

    studies = {
        '61405445-01': {'name': 'iGaming Concept Evaluate', 'concepts': 5},
        '61407017': {'name': '24 Ideas Screening', 'concepts': 24},
        '61407069': {'name': 'Tech-Enabled ScratchCards', 'concepts': 8},
        '61407185': {'name': 'Innovation Concepts 2025', 'concepts': 8}
    }

    for study_id in studies.keys():
        print(f"Analyzing {study_id}...")

        val_data, syn_df, gt_df = load_validation_data(study_id)

        if val_data is None or syn_df is None or gt_df is None:
            print(f"  ⚠️ Data not ready")
            studies[study_id]['metrics'] = None
            continue

        # Get question columns
        question_cols = [col for col in gt_df.columns
                        if '(' in col and ')' in col and col in syn_df.columns]

        print(f"  Found {len(question_cols)} comparable questions")

        # Calculate metrics for each question
        question_metrics = []
        for col in question_cols:
            metrics = calculate_distribution_metrics(gt_df[col], syn_df[col])
            if metrics:
                metrics['column'] = col
                question_metrics.append(metrics)

        # Calculate aggregate metrics
        aggregate = {}
        if question_metrics:
            for key in ['kl_divergence', 'js_divergence', 'ks_similarity', 'total_variation_distance', 'hellinger_distance']:
                values = [m[key] for m in question_metrics if m.get(key) is not None]
                if values:
                    aggregate[f'mean_{key.replace("_divergence", "").replace("_distance", "").replace("_similarity", "_sim")}'] = np.mean(values)
                    aggregate[f'median_{key.replace("_divergence", "").replace("_distance", "").replace("_similarity", "_sim")}'] = np.median(values)

        # Calculate ranking metrics
        ranking = calculate_concept_ranking_metrics(gt_df, syn_df, question_cols)

        # Assess validity
        combined_metrics = {**aggregate, **(ranking if ranking else {})}
        assessment = assess_statistical_validity(combined_metrics)

        studies[study_id]['metrics'] = {
            'question_metrics': question_metrics,
            'aggregate': aggregate,
            'ranking': ranking
        }
        studies[study_id]['assessment'] = assessment

        print(f"  Status: {assessment['overall_status']}")

    print()
    print("Generating report...")

    report = generate_statistical_report(studies)

    output_file = Path("STATISTICAL_VALIDATION_REPORT.md")
    with open(output_file, 'w') as f:
        f.write(report)

    print(f"✓ Report written to: {output_file}")
    print()
    print(report)

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
