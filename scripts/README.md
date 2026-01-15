# Utility Scripts

This directory contains standalone utility scripts for analysis and reporting.

## Validation Scripts

Located in `validation/` subdirectory:

### statistical_validation_analysis.py
Main validation script that compares synthetic survey data against ground truth Kantar data.

**Usage:**
```bash
python scripts/validation/statistical_validation_analysis.py
```

Analyzes all generated synthetic datasets and computes statistical metrics:
- KL Divergence (distribution similarity)
- KS Similarity
- Spearman correlation (ranking preservation)
- Generates detailed validation reports

### enhanced_statistical_validation.py
Enhanced validation with robustness analysis across multiple runs.

**Usage:**
```bash
python scripts/validation/enhanced_statistical_validation.py
```

Analyzes multiple validation runs to demonstrate:
- Consistency across different datasets
- Robustness of synthetic data generation
- Statistical confidence intervals

### generate_validation_summary.py
Generates markdown summary reports from validation results.

**Usage:**
```bash
python scripts/validation/generate_validation_summary.py
```

Creates formatted reports for presentation and documentation.

## Running Scripts

All scripts should be run from the repository root directory:

```bash
# From project root
python scripts/validation/statistical_validation_analysis.py
```

## Output

Scripts generate reports in:
- `docs/validation/` - Validation reports and analysis
- Console output - Real-time progress and summary statistics
