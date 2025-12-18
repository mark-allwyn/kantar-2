"""
Validation Metrics

Computes metrics to compare synthetic vs ground truth data.
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.special import rel_entr
from typing import Dict, List, Tuple, Optional


class ValidationMetrics:
    """Metrics for comparing synthetic and ground truth data"""

    @staticmethod
    def kl_divergence(p: np.ndarray, q: np.ndarray, epsilon: float = 1e-10) -> float:
        """
        Compute KL divergence: KL(P || Q) = sum(P * log(P / Q))

        Lower values indicate better match (0 = identical distributions)

        Args:
            p: Ground truth probability distribution
            q: Synthetic probability distribution
            epsilon: Small value to avoid log(0)

        Returns:
            KL divergence value
        """
        # Ensure arrays are numpy and normalized
        p = np.asarray(p, dtype=float)
        q = np.asarray(q, dtype=float)

        # Normalize if not already
        if not np.isclose(p.sum(), 1.0):
            p = p / p.sum()
        if not np.isclose(q.sum(), 1.0):
            q = q / q.sum()

        # Add epsilon to avoid division by zero
        p = p + epsilon
        q = q + epsilon

        # Renormalize after adding epsilon
        p = p / p.sum()
        q = q / q.sum()

        # Compute KL divergence
        kl = np.sum(rel_entr(p, q))

        return float(kl)

    @staticmethod
    def js_divergence(p: np.ndarray, q: np.ndarray) -> float:
        """
        Compute Jensen-Shannon divergence (symmetric version of KL).

        JS(P || Q) = 0.5 * KL(P || M) + 0.5 * KL(Q || M) where M = 0.5 * (P + Q)

        Range: [0, 1] where 0 = identical

        Args:
            p: Ground truth distribution
            q: Synthetic distribution

        Returns:
            JS divergence value
        """
        p = np.asarray(p, dtype=float)
        q = np.asarray(q, dtype=float)

        # Normalize
        p = p / p.sum()
        q = q / q.sum()

        # Compute mean distribution
        m = 0.5 * (p + q)

        # Compute JS divergence
        js = 0.5 * ValidationMetrics.kl_divergence(p, m) + 0.5 * ValidationMetrics.kl_divergence(q, m)

        return float(js)

    @staticmethod
    def ks_statistic(ground_truth: np.ndarray, synthetic: np.ndarray) -> Tuple[float, float]:
        """
        Compute Kolmogorov-Smirnov test statistic.

        Higher statistic = distributions are more different
        Lower p-value = more significant difference

        Args:
            ground_truth: Ground truth data
            synthetic: Synthetic data

        Returns:
            (statistic, p_value)
        """
        statistic, p_value = stats.ks_2samp(ground_truth, synthetic)
        return float(statistic), float(p_value)

    @staticmethod
    def ks_similarity(ground_truth: np.ndarray, synthetic: np.ndarray) -> float:
        """
        Compute KS similarity (1 - KS statistic).

        This is the metric used in the paper "LLMs Reproduce Human Purchase Intent
        via Semantic Similarity Elicitation of Likert Ratings".

        Higher values = more similar distributions
        Range: [0, 1] where 1 = identical distributions

        Paper benchmark: > 0.85 is considered good
        Paper results with SSR: GPT-4o = 0.88, Gemini-2f = 0.80

        Args:
            ground_truth: Ground truth data
            synthetic: Synthetic data

        Returns:
            KS similarity value (higher = better match)
        """
        statistic, _ = ValidationMetrics.ks_statistic(ground_truth, synthetic)
        return 1.0 - statistic

    @staticmethod
    def correlation(ground_truth: np.ndarray, synthetic: np.ndarray) -> float:
        """
        Compute Pearson correlation coefficient.

        Args:
            ground_truth: Ground truth values
            synthetic: Synthetic values

        Returns:
            Correlation coefficient (-1 to 1)
        """
        if len(ground_truth) != len(synthetic):
            raise ValueError("Arrays must have same length")

        corr, _ = stats.pearsonr(ground_truth, synthetic)
        return float(corr)

    @staticmethod
    def correlation_attainment(ground_truth_corr: float,
                              synthetic_corr: float,
                              reliability: float = 0.85) -> float:
        """
        Compute correlation attainment (% of test-retest reliability).

        From the paper: synthetic correlation / human test-retest reliability

        Args:
            ground_truth_corr: Correlation between ground truth and synthetic
            synthetic_corr: Not used (kept for API compatibility)
            reliability: Human test-retest reliability (default 0.85 from paper)

        Returns:
            Correlation attainment as percentage (e.g., 90.2 means 90.2%)
        """
        return (ground_truth_corr / reliability) * 100

    @staticmethod
    def mean_absolute_error(ground_truth: np.ndarray, synthetic: np.ndarray) -> float:
        """
        Compute Mean Absolute Error.

        Args:
            ground_truth: Ground truth values
            synthetic: Synthetic values

        Returns:
            MAE value
        """
        return float(np.mean(np.abs(ground_truth - synthetic)))

    @staticmethod
    def chi_square_test(ground_truth_dist: np.ndarray,
                       synthetic_dist: np.ndarray) -> Tuple[float, float]:
        """
        Compute chi-square test for categorical distributions.

        Args:
            ground_truth_dist: Ground truth frequency distribution
            synthetic_dist: Synthetic frequency distribution

        Returns:
            (chi2_statistic, p_value)
        """
        chi2, p_value = stats.chisquare(synthetic_dist, ground_truth_dist)
        return float(chi2), float(p_value)

    @staticmethod
    def compute_distribution_metrics(ground_truth: pd.Series,
                                    synthetic: pd.Series,
                                    question_type: str = "likert") -> Dict[str, float]:
        """
        Compute all relevant metrics for a question.

        Args:
            ground_truth: Ground truth responses
            synthetic: Synthetic responses
            question_type: "likert", "binary", "continuous"

        Returns:
            Dictionary of metric values
        """
        metrics = {}

        if question_type in ["likert", "binary"]:
            # Get value counts normalized
            gt_dist = ground_truth.value_counts(normalize=True).sort_index()
            syn_dist = synthetic.value_counts(normalize=True).sort_index()

            # Ensure same categories
            all_categories = sorted(set(gt_dist.index) | set(syn_dist.index))
            gt_dist = gt_dist.reindex(all_categories, fill_value=0)
            syn_dist = syn_dist.reindex(all_categories, fill_value=0)

            # KL divergence
            metrics['kl_divergence'] = ValidationMetrics.kl_divergence(
                gt_dist.values, syn_dist.values
            )

            # JS divergence
            metrics['js_divergence'] = ValidationMetrics.js_divergence(
                gt_dist.values, syn_dist.values
            )

            # Chi-square test
            gt_counts = ground_truth.value_counts().sort_index()
            syn_counts = synthetic.value_counts().sort_index()
            gt_counts = gt_counts.reindex(all_categories, fill_value=0)
            syn_counts = syn_counts.reindex(all_categories, fill_value=0)

            # Normalize counts to percentages for chi-square test when sample sizes differ
            gt_total = gt_counts.sum()
            syn_total = syn_counts.sum()

            # Scale synthetic counts to match ground truth total for chi-square test
            syn_counts_scaled = (syn_counts / syn_total) * gt_total if syn_total > 0 else syn_counts

            try:
                chi2, p_value = ValidationMetrics.chi_square_test(
                    gt_counts.values, syn_counts_scaled.values
                )
                metrics['chi2_statistic'] = chi2
                metrics['chi2_p_value'] = p_value
            except ValueError:
                # If chi-square still fails, skip it
                metrics['chi2_statistic'] = np.nan
                metrics['chi2_p_value'] = np.nan

        # KS statistic (works for all types)
        ks_stat, ks_p = ValidationMetrics.ks_statistic(
            ground_truth.values, synthetic.values
        )
        metrics['ks_statistic'] = ks_stat
        metrics['ks_p_value'] = ks_p

        # KS similarity (paper's metric: 1 - KS statistic)
        metrics['ks_similarity'] = ValidationMetrics.ks_similarity(
            ground_truth.values, synthetic.values
        )

        # Mean comparison
        metrics['ground_truth_mean'] = float(ground_truth.mean())
        metrics['synthetic_mean'] = float(synthetic.mean())
        metrics['mean_difference'] = metrics['synthetic_mean'] - metrics['ground_truth_mean']
        metrics['mean_absolute_error'] = abs(metrics['mean_difference'])

        # Standard deviation comparison
        metrics['ground_truth_std'] = float(ground_truth.std())
        metrics['synthetic_std'] = float(synthetic.std())

        return metrics

    @staticmethod
    def compute_overall_metrics(ground_truth_df: pd.DataFrame,
                              synthetic_df: pd.DataFrame,
                              question_columns: List[str],
                              question_types: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """
        Compute metrics for all questions.

        Args:
            ground_truth_df: Ground truth data
            synthetic_df: Synthetic data
            question_columns: List of question column names
            question_types: Optional dict mapping column names to types

        Returns:
            DataFrame with metrics for each question
        """
        results = []

        for col in question_columns:
            if col not in ground_truth_df.columns or col not in synthetic_df.columns:
                continue

            # Determine question type
            q_type = "likert"
            if question_types and col in question_types:
                q_type = question_types[col]

            # Compute metrics
            metrics = ValidationMetrics.compute_distribution_metrics(
                ground_truth_df[col],
                synthetic_df[col],
                question_type=q_type
            )

            metrics['question'] = col
            results.append(metrics)

        return pd.DataFrame(results)
