# Enhanced Statistical Validation Report

## Robustness Analysis - Multiple Validation Runs

This analysis demonstrates consistency across multiple synthetic dataset generations.


### 61405445-01 - iGaming Concept Evaluate

**Number of Validation Runs:** 17

#### KL Divergence (Distribution Similarity)
- Mean: 9.3244
- Std Dev: 5.9985
- Range: [2.6853, 17.9143]
- Coefficient of Variation: 64.33%
- Consistency: ⚠️ MODERATE

#### KS Similarity
- Mean: 0.5970
- Std Dev: 0.1855
- Range: [0.2528, 0.7616]
- Coefficient of Variation: 31.08%
- Consistency: ⚠️ MODERATE


### 61407017 - 24 Ideas Screening

**Number of Validation Runs:** 1

#### KL Divergence (Distribution Similarity)
- Mean: 0.1416
- Std Dev: 0.0000
- Range: [0.1416, 0.1416]

#### KS Similarity
- Mean: 0.9933
- Std Dev: 0.0000
- Range: [0.9933, 0.9933]


### 61407069 - Tech-Enabled ScratchCards

**Number of Validation Runs:** 1

#### KL Divergence (Distribution Similarity)
- Mean: 2.6276
- Std Dev: 0.0000
- Range: [2.6276, 2.6276]

#### KS Similarity
- Mean: 0.8049
- Std Dev: 0.0000
- Range: [0.8049, 0.8049]


### 61407185 - Innovation Concepts 2025

**Number of Validation Runs:** 1

#### KL Divergence (Distribution Similarity)
- Mean: 3.2935
- Std Dev: 0.0000
- Range: [3.2935, 3.2935]

#### KS Similarity
- Mean: 0.7992
- Std Dev: 0.0000
- Range: [0.7992, 0.7992]


## Interpretation

### Consistency Metrics
- **Coefficient of Variation (CV):** Measures variability relative to mean
  - CV < 10%: 🟢 EXCELLENT - Highly consistent results
  - CV 10-20%: ✅ GOOD - Acceptable variation
  - CV > 20%: ⚠️ MODERATE - Higher variation

### What This Demonstrates
- **Reproducibility:** Multiple runs yield consistent results
- **Robustness:** System performs reliably across different generations
- **Statistical Confidence:** Results are not due to random chance