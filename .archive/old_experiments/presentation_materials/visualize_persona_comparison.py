#!/usr/bin/env python3
"""
Visualize Human vs Synthetic Persona Distributions

Creates comparison plots showing the distribution differences between
human survey respondents and synthetically generated personas.
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import json

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 12)
plt.rcParams['font.size'] = 10

def load_synthetic_data(filepath):
    """Load synthetic data from Excel file"""
    df = pd.read_excel(filepath)
    return df

def extract_persona_demographics(df):
    """Extract demographic distributions from dataframe"""
    demographics = {}

    # Age distribution
    if 'AGE' in df.columns:
        demographics['age'] = df['AGE'].dropna()

    # Gender distribution
    if 'Gender' in df.columns:
        demographics['gender'] = df['Gender'].dropna()
    elif '(SEX) SEX' in df.columns:
        demographics['gender'] = df['(SEX) SEX'].dropna()

    # Age band distribution
    if '(AGEQUOTA) AGEBANDS' in df.columns:
        demographics['age_band'] = df['(AGEQUOTA) AGEBANDS'].dropna()

    # Target group
    if '(GROUPFMR) SAMPLE TYPE' in df.columns:
        demographics['target_group'] = df['(GROUPFMR) SAMPLE TYPE'].dropna()

    # SC Player Type
    if '(SCPLAYER) SC PLAYER TYPE' in df.columns:
        demographics['sc_player_type'] = df['(SCPLAYER) SC PLAYER TYPE'].dropna()

    # Category Buyer
    if '(CATBUYER) PRODUCTS / SERVICES BOUGHT' in df.columns:
        demographics['category_buyer'] = df['(CATBUYER) PRODUCTS / SERVICES BOUGHT'].dropna()

    # Brand Buyers
    if '(BRDBUY) BRANDS BOUGHT' in df.columns:
        demographics['brand_buyers'] = df['(BRDBUY) BRANDS BOUGHT'].dropna()

    # Inertia
    if 'Inertia' in df.columns:
        demographics['inertia'] = df['Inertia'].dropna()

    return demographics

def create_comparison_plots(synthetic_data_path, output_path='persona_comparison.png'):
    """Create comparison plots for persona distributions"""

    # Load synthetic data
    print(f"Loading synthetic data from {synthetic_data_path}")
    synthetic_df = load_synthetic_data(synthetic_data_path)

    print(f"Loaded {len(synthetic_df)} synthetic respondents")
    print(f"Columns: {synthetic_df.columns.tolist()}")

    # Extract demographics
    synthetic_demos = extract_persona_demographics(synthetic_df)

    # Create figure with subplots
    fig, axes = plt.subplots(3, 3, figsize=(18, 14))
    fig.suptitle('Synthetic Persona Distributions', fontsize=16, fontweight='bold', y=0.995)

    # Plot 1: Age Distribution
    if 'age' in synthetic_demos:
        ax = axes[0, 0]
        ages = synthetic_demos['age']
        ax.hist(ages, bins=20, alpha=0.7, color='steelblue', edgecolor='black')
        ax.set_xlabel('Age')
        ax.set_ylabel('Frequency')
        ax.set_title(f'Age Distribution (n={len(ages)})')
        ax.axvline(ages.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {ages.mean():.1f}')
        ax.legend()

    # Plot 2: Age Band Distribution
    if 'age_band' in synthetic_demos:
        ax = axes[0, 1]
        age_band_counts = synthetic_demos['age_band'].value_counts().sort_index()
        colors = sns.color_palette("Set2", len(age_band_counts))
        bars = ax.bar(range(len(age_band_counts)), age_band_counts.values, color=colors, edgecolor='black')
        ax.set_xticks(range(len(age_band_counts)))
        ax.set_xticklabels(age_band_counts.index, rotation=45, ha='right')
        ax.set_ylabel('Frequency')
        ax.set_title(f'Age Band Distribution (n={age_band_counts.sum()})')

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontweight='bold')

    # Plot 3: Gender Distribution
    if 'gender' in synthetic_demos:
        ax = axes[0, 2]
        gender_counts = synthetic_demos['gender'].value_counts()
        colors = sns.color_palette("Set3", len(gender_counts))
        wedges, texts, autotexts = ax.pie(gender_counts.values, labels=gender_counts.index,
                                          autopct='%1.1f%%', colors=colors, startangle=90)
        ax.set_title(f'Gender Distribution (n={gender_counts.sum()})')
        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_fontweight('bold')

    # Plot 4: Target Group Distribution
    if 'target_group' in synthetic_demos:
        ax = axes[1, 0]
        target_counts = synthetic_demos['target_group'].value_counts()
        colors = sns.color_palette("husl", len(target_counts))
        bars = ax.barh(range(len(target_counts)), target_counts.values, color=colors, edgecolor='black')
        ax.set_yticks(range(len(target_counts)))
        ax.set_yticklabels(target_counts.index, fontsize=9)
        ax.set_xlabel('Frequency')
        ax.set_title(f'Target Group Distribution (n={target_counts.sum()})')

        # Add value labels on bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f' {int(width)}',
                   ha='left', va='center', fontweight='bold')

    # Plot 5: SC Player Type Distribution
    if 'sc_player_type' in synthetic_demos:
        ax = axes[1, 1]
        sc_counts = synthetic_demos['sc_player_type'].value_counts()
        colors = ['#2ecc71', '#e74c3c'][:len(sc_counts)]
        bars = ax.bar(range(len(sc_counts)), sc_counts.values, color=colors, edgecolor='black')
        ax.set_xticks(range(len(sc_counts)))
        ax.set_xticklabels(sc_counts.index, rotation=45, ha='right')
        ax.set_ylabel('Frequency')
        ax.set_title(f'SC Player Type (n={sc_counts.sum()})')

        # Add value labels and percentages on bars
        total = sc_counts.sum()
        for i, bar in enumerate(bars):
            height = bar.get_height()
            pct = (height / total) * 100
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}\n({pct:.1f}%)',
                   ha='center', va='bottom', fontweight='bold')

    # Plot 6: Inertia Distribution
    if 'inertia' in synthetic_demos:
        ax = axes[1, 2]
        inertia = synthetic_demos['inertia']
        ax.hist(inertia, bins=20, alpha=0.7, color='coral', edgecolor='black')
        ax.set_xlabel('Inertia Score (1-7)')
        ax.set_ylabel('Frequency')
        ax.set_title(f'Inertia Distribution (n={len(inertia)})')
        ax.axvline(inertia.mean(), color='darkred', linestyle='--', linewidth=2,
                  label=f'Mean: {inertia.mean():.2f}')
        ax.axvline(inertia.median(), color='blue', linestyle=':', linewidth=2,
                  label=f'Median: {inertia.median():.2f}')
        ax.legend()

    # Plot 7: Category Buyer Analysis (Multi-select)
    ax = axes[2, 0]
    if 'category_buyer' in synthetic_demos:
        # Parse the multi-select field
        category_counts = {}
        for value in synthetic_demos['category_buyer']:
            if pd.isna(value):
                continue
            # Split by comma or semicolon
            items = str(value).split(';') if ';' in str(value) else str(value).split(',')
            for item in items:
                item = item.strip()
                if item:
                    category_counts[item] = category_counts.get(item, 0) + 1

        if category_counts:
            # Sort by frequency
            sorted_items = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
            labels, counts = zip(*sorted_items)

            colors = sns.color_palette("viridis", len(labels))
            bars = ax.barh(range(len(labels)), counts, color=colors, edgecolor='black')
            ax.set_yticks(range(len(labels)))
            ax.set_yticklabels(labels, fontsize=8)
            ax.set_xlabel('Frequency')
            ax.set_title('Category Buyer (Multi-select)')

            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2.,
                       f' {int(width)}',
                       ha='left', va='center', fontweight='bold', fontsize=8)
        else:
            ax.axis('off')
    else:
        ax.axis('off')

    # Plot 8: Brand Buyers Analysis (Multi-select)
    ax = axes[2, 1]
    if 'brand_buyers' in synthetic_demos:
        # Parse the multi-select field
        brand_counts = {}
        for value in synthetic_demos['brand_buyers']:
            if pd.isna(value):
                continue
            # Split by comma or semicolon
            items = str(value).split(';') if ';' in str(value) else str(value).split(',')
            for item in items:
                item = item.strip()
                if item:
                    brand_counts[item] = brand_counts.get(item, 0) + 1

        if brand_counts:
            # Sort by frequency and take top 10
            sorted_items = sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            labels, counts = zip(*sorted_items)

            colors = sns.color_palette("rocket", len(labels))
            bars = ax.barh(range(len(labels)), counts, color=colors, edgecolor='black')
            ax.set_yticks(range(len(labels)))
            ax.set_yticklabels(labels, fontsize=8)
            ax.set_xlabel('Frequency')
            ax.set_title('Top 10 Brand Buyers (Multi-select)')

            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2.,
                       f' {int(width)}',
                       ha='left', va='center', fontweight='bold', fontsize=8)
        else:
            ax.axis('off')
    else:
        ax.axis('off')

    # Plot 9: Summary Statistics
    ax = axes[2, 2]
    ax.axis('off')

    summary_text = "Synthetic Persona Summary\n" + "="*40 + "\n\n"
    summary_text += f"Total Respondents: {len(synthetic_df)}\n\n"

    if 'age' in synthetic_demos:
        ages = synthetic_demos['age']
        summary_text += f"Age Statistics:\n"
        summary_text += f"  Mean: {ages.mean():.1f} years\n"
        summary_text += f"  Median: {ages.median():.1f} years\n"
        summary_text += f"  Range: {ages.min():.0f}-{ages.max():.0f} years\n\n"

    if 'gender' in synthetic_demos:
        gender_counts = synthetic_demos['gender'].value_counts()
        summary_text += f"Gender:\n"
        for gender, count in gender_counts.items():
            pct = (count / len(synthetic_demos['gender'])) * 100
            summary_text += f"  {gender}: {count} ({pct:.1f}%)\n"
        summary_text += "\n"

    if 'sc_player_type' in synthetic_demos:
        sc_counts = synthetic_demos['sc_player_type'].value_counts()
        summary_text += f"SC Player Status:\n"
        for status, count in sc_counts.items():
            pct = (count / len(synthetic_demos['sc_player_type'])) * 100
            summary_text += f"  {status}: {count} ({pct:.1f}%)\n"

    ax.text(0.1, 0.9, summary_text, transform=ax.transAxes,
           fontsize=10, verticalalignment='top',
           fontfamily='monospace',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()

    # Save figure
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nVisualization saved to: {output_path}")

    # Close the figure to free memory
    plt.close(fig)

    return output_path

if __name__ == "__main__":
    # Use the most recent synthetic data file
    synthetic_file = "data/synthetic/synthetic_data_100resp_20251218_180348.xlsx"

    print("="*60)
    print("Synthetic Persona Distribution Visualization")
    print("="*60)

    create_comparison_plots(
        synthetic_data_path=synthetic_file,
        output_path='persona_distribution_visualization.png'
    )

    print("\nVisualization complete!")
