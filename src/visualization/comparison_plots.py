"""
Comparison Visualization

Creates plots comparing ground truth and synthetic data.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import List, Dict, Optional


class ComparisonVisualizer:
    """Visualizer for comparing ground truth and synthetic data"""

    def __init__(self, style: str = "seaborn-v0_8-darkgrid"):
        """
        Initialize the visualizer.

        Args:
            style: Matplotlib style to use
        """
        try:
            plt.style.use(style)
        except:
            pass  # Use default if style not available

        sns.set_palette("husl")
        self.colors = {
            'ground_truth': '#2E86AB',
            'synthetic': '#A23B72'
        }

    def plot_distribution_comparison(self,
                                    ground_truth: pd.Series,
                                    synthetic: pd.Series,
                                    title: str,
                                    xlabel: str = "Response",
                                    figsize: tuple = (10, 6)) -> plt.Figure:
        """
        Create side-by-side bar chart comparing distributions.

        Args:
            ground_truth: Ground truth responses
            synthetic: Synthetic responses
            title: Plot title
            xlabel: X-axis label
            figsize: Figure size

        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)

        # Get value counts
        gt_dist = ground_truth.value_counts(normalize=True).sort_index()
        syn_dist = synthetic.value_counts(normalize=True).sort_index()

        # Ensure same categories
        all_categories = sorted(set(gt_dist.index) | set(syn_dist.index))
        gt_dist = gt_dist.reindex(all_categories, fill_value=0)
        syn_dist = syn_dist.reindex(all_categories, fill_value=0)

        # Create bar positions
        x = np.arange(len(all_categories))
        width = 0.35

        # Plot bars
        ax.bar(x - width/2, gt_dist.values, width,
              label='Ground Truth', color=self.colors['ground_truth'], alpha=0.8)
        ax.bar(x + width/2, syn_dist.values, width,
              label='Synthetic', color=self.colors['synthetic'], alpha=0.8)

        # Customize plot
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel('Proportion', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(all_categories, rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        return fig

    def plot_kl_heatmap(self,
                       metrics_df: pd.DataFrame,
                       figsize: tuple = (12, 8)) -> plt.Figure:
        """
        Create heatmap of KL divergence values across questions.

        Args:
            metrics_df: DataFrame with 'question' and 'kl_divergence' columns
            figsize: Figure size

        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)

        # Prepare data
        questions = metrics_df['question'].values
        kl_values = metrics_df['kl_divergence'].values

        # Create heatmap data
        heatmap_data = kl_values.reshape(-1, 1)

        # Plot
        sns.heatmap(heatmap_data, annot=True, fmt='.3f',
                   yticklabels=questions, xticklabels=['KL Divergence'],
                   cmap='RdYlGn_r', ax=ax, cbar_kws={'label': 'KL Divergence'})

        ax.set_title('KL Divergence by Question\n(Lower = Better Match)',
                    fontsize=14, fontweight='bold')

        plt.tight_layout()
        return fig

    def plot_mean_scatter(self,
                         metrics_df: pd.DataFrame,
                         figsize: tuple = (10, 10)) -> plt.Figure:
        """
        Create scatter plot of mean scores (ground truth vs synthetic).

        Args:
            metrics_df: DataFrame with mean columns
            figsize: Figure size

        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)

        # Extract means
        gt_means = metrics_df['ground_truth_mean'].values
        syn_means = metrics_df['synthetic_mean'].values

        # Scatter plot
        ax.scatter(gt_means, syn_means, alpha=0.6, s=100, color=self.colors['synthetic'])

        # Add diagonal reference line (perfect match)
        min_val = min(gt_means.min(), syn_means.min())
        max_val = max(gt_means.max(), syn_means.max())
        ax.plot([min_val, max_val], [min_val, max_val],
               'k--', alpha=0.5, label='Perfect Match')

        # Calculate correlation
        corr = np.corrcoef(gt_means, syn_means)[0, 1]

        # Customize plot
        ax.set_xlabel('Ground Truth Mean', fontsize=12)
        ax.set_ylabel('Synthetic Mean', fontsize=12)
        ax.set_title(f'Mean Score Comparison\n(Correlation: {corr:.3f})',
                    fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(alpha=0.3)

        plt.tight_layout()
        return fig

    def plot_metric_dashboard(self,
                             metrics_df: pd.DataFrame,
                             figsize: tuple = (14, 10)) -> plt.Figure:
        """
        Create dashboard with multiple metric visualizations.

        Args:
            metrics_df: DataFrame with all metrics
            figsize: Figure size

        Returns:
            Matplotlib figure
        """
        fig, axes = plt.subplots(2, 2, figsize=figsize)

        # 1. KL Divergence distribution
        ax = axes[0, 0]
        ax.hist(metrics_df['kl_divergence'], bins=20, color=self.colors['synthetic'], alpha=0.7)
        ax.axvline(metrics_df['kl_divergence'].mean(), color='red',
                  linestyle='--', label=f"Mean: {metrics_df['kl_divergence'].mean():.3f}")
        ax.set_xlabel('KL Divergence')
        ax.set_ylabel('Frequency')
        ax.set_title('Distribution of KL Divergence')
        ax.legend()
        ax.grid(alpha=0.3)

        # 2. Mean correlation
        ax = axes[0, 1]
        gt_means = metrics_df['ground_truth_mean'].values
        syn_means = metrics_df['synthetic_mean'].values
        ax.scatter(gt_means, syn_means, alpha=0.6, color=self.colors['ground_truth'])
        min_val = min(gt_means.min(), syn_means.min())
        max_val = max(gt_means.max(), syn_means.max())
        ax.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5)
        corr = np.corrcoef(gt_means, syn_means)[0, 1]
        ax.set_xlabel('Ground Truth Mean')
        ax.set_ylabel('Synthetic Mean')
        ax.set_title(f'Mean Correlation (r={corr:.3f})')
        ax.grid(alpha=0.3)

        # 3. KS Statistic distribution
        ax = axes[1, 0]
        ax.hist(metrics_df['ks_statistic'], bins=20, color=self.colors['ground_truth'], alpha=0.7)
        ax.axvline(metrics_df['ks_statistic'].mean(), color='red',
                  linestyle='--', label=f"Mean: {metrics_df['ks_statistic'].mean():.3f}")
        ax.set_xlabel('KS Statistic')
        ax.set_ylabel('Frequency')
        ax.set_title('Distribution of KS Statistic')
        ax.legend()
        ax.grid(alpha=0.3)

        # 4. Mean Absolute Error
        ax = axes[1, 1]
        ax.hist(metrics_df['mean_absolute_error'], bins=20, color=self.colors['synthetic'], alpha=0.7)
        ax.axvline(metrics_df['mean_absolute_error'].mean(), color='red',
                  linestyle='--', label=f"Mean: {metrics_df['mean_absolute_error'].mean():.3f}")
        ax.set_xlabel('Mean Absolute Error')
        ax.set_ylabel('Frequency')
        ax.set_title('Distribution of MAE')
        ax.legend()
        ax.grid(alpha=0.3)

        plt.suptitle('Validation Metrics Dashboard', fontsize=16, fontweight='bold', y=1.00)
        plt.tight_layout()
        return fig

    def plot_overlap_histogram(self,
                              ground_truth: pd.Series,
                              synthetic: pd.Series,
                              title: str,
                              bins: int = 20,
                              figsize: tuple = (10, 6)) -> plt.Figure:
        """
        Create overlapping histograms.

        Args:
            ground_truth: Ground truth data
            synthetic: Synthetic data
            title: Plot title
            bins: Number of bins
            figsize: Figure size

        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)

        ax.hist(ground_truth, bins=bins, alpha=0.5,
               label='Ground Truth', color=self.colors['ground_truth'], density=True)
        ax.hist(synthetic, bins=bins, alpha=0.5,
               label='Synthetic', color=self.colors['synthetic'], density=True)

        ax.set_xlabel('Value', fontsize=12)
        ax.set_ylabel('Density', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(alpha=0.3)

        plt.tight_layout()
        return fig
