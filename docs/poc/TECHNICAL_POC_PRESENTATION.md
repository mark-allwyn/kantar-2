# Synthetic Survey Data - Technical Proof of Concept

**Statistical Validation of LLM-Generated Survey Responses**

---

## Objective

**Prove:** Synthetic survey data generated using LLMs + Semantic Similarity Rating (SSR) is statistically indistinguishable from ground truth human responses.

**Method:** Validate across 4 US market studies (5-24 concepts each) using rigorous statistical tests.

**Success Criteria:**
- Distribution similarity (KL divergence, KS tests)
- Concept ranking preservation (Spearman correlation)
- Statistical significance tests pass

---

## Methodology: Semantic Similarity Rating (SSR)

### The Core Innovation

**Problem:** LLMs can't directly rate on Likert scales (1-5) reliably.

**Solution:** SSR maps natural language responses to scales using semantic similarity.

### How SSR Works

```
1. Prompt LLM for free-text response
   "How likely would you be to purchase this concept?"
   → "I'd definitely try this, it looks really appealing"

2. Embed response + scale anchors
   Level 5: "I would definitely purchase/highly likely"
   Level 4: "I would probably purchase/likely"
   ... (5-9 anchors per level)

3. Calculate cosine similarity
   Response embedding vs each anchor embedding

4. Softmax normalization → probability distribution

5. Select level with highest probability
   → Maps to scale value (1-5)
```

**Why This Works:**
- Captures nuanced semantic meaning
- Research-backed: 90% correlation vs human test-retest reliability
- More realistic than forcing LLMs to pick numbers

---

## Validation Design

### 4 US Market Studies

| Study | Concepts | GT Respondents | Synthetic Respondents | Complexity |
|-------|----------|----------------|----------------------|------------|
| 61405445-01 | 5 | 150 | 50 | Low (baseline) |
| 61407017 | 24 | 600 | 50 | **High** (stress test) |
| 61407069 | 8 | 805 | 50 | Medium |
| 61407185 | 8 | 400 | 50 | Medium |

### Key Design Choices

**3 Concepts per Respondent**
- Matches Kantar methodology (concept rotation)
- Tests realistic survey conditions
- Ensures comparable data structure

**Ground Truth Demographics**
- Sample gender, age, occupation from GT distributions
- Ensures synthetic personas match real market
- Controls for demographic effects

**50 Respondents**
- Sufficient for distribution-level analysis
- Comparable sample sizes (not trying to match GT n)
- Cost-effective for POC

---

## Statistical Metrics

### Distribution Similarity Tests

**1. KL Divergence (Kullback-Leibler)**
- Measures how much synthetic distribution diverges from GT
- Range: 0 (identical) to ∞
- **Target: < 0.20** (within 20% of GT distribution)

**2. KS Statistic (Kolmogorov-Smirnov)**
- Non-parametric test for distribution equality
- Returns similarity score (0-1) and p-value
- **Target: Similarity > 0.85** (85%+ match)

**3. Total Variation Distance (TVD)**
- Measures maximum difference between distributions
- Range: 0 (identical) to 1 (completely different)
- **Target: < 0.10** (less than 10% total variation)

**4. Jensen-Shannon Divergence (JS)**
- Symmetric version of KL divergence
- Bounded between 0 and 1
- **Target: < 0.10**

**5. Hellinger Distance**
- Another measure of distribution similarity
- Bounded between 0 and 1
- **Target: < 0.15**

### Ranking Preservation Tests

**1. Spearman Rank Correlation**
- Measures if concepts rank in same order (GT vs Synthetic)
- Range: -1 (opposite) to +1 (perfect agreement)
- **Target: > 0.85** (85%+ rank agreement)

**2. Kendall's Tau**
- Alternative rank correlation measure
- More robust to outliers
- **Target: > 0.70**

**3. Top-3 Agreement**
- Do the top 3 concepts match between GT and Synthetic?
- Binary measure (2/3, 3/3 matches)
- **Target: ≥ 67%** (at least 2/3 concepts match)

**4. Top-1 Agreement**
- Does the winning concept match?
- Most critical for business decisions
- **Target: 100%** (winner must match)

### Why These Metrics?

**Distribution Tests** → Proves synthetic data has correct shape/spread
**Ranking Tests** → Proves synthetic data makes correct decisions
**Multiple Metrics** → No single test is perfect; convergent validity

---

## Results Summary

### Cross-Study Performance

| Study | KL Div | KS Sim | Rank Corr | Top-1 Match | Status |
|-------|--------|--------|-----------|-------------|---------|
| 61405445-01 | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| 61407017 | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| 61407069 | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| 61407185 | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| **MEAN** | [TBD] | [TBD] | [TBD] | [TBD%] | [TBD] |

**Target Thresholds:**
- KL < 0.20 ✓
- KS > 0.85 ✓
- Rank Corr > 0.85 ✓
- Top-1 Match = 100% ✓

### Interpretation

**PASS (All 4 metrics meet targets):**
- Synthetic data is statistically equivalent to ground truth
- Safe to use for decision-making
- System validated for this use case

**WARN (2-3 metrics meet targets):**
- Generally good performance with some gaps
- Review specific questions/concepts that underperform
- Use with caution, validate critical decisions

**FAIL (<2 metrics meet targets):**
- System not ready for this use case
- Requires calibration or methodology changes
- Do not use for decision-making

---

## Distribution Comparison Examples

### Example: Purchase Intent (Study 61405445-01)

[PLACEHOLDER FOR CHART]

**Synthetic vs Ground Truth Distribution:**
- Scale: 1 (Definitely not purchase) to 5 (Definitely purchase)
- KL Divergence: [TBD]
- KS Similarity: [TBD]
- Visual Assessment: [Nearly identical | Some drift | Significant difference]

**Statistical Tests:**
- KS Test p-value: [TBD] ([Fail to reject | Reject] null hypothesis of equal distributions)
- Chi-square p-value: [TBD]

### Example: Concept Rankings

[PLACEHOLDER FOR RANK COMPARISON TABLE]

| Concept | GT Rank | GT Score | Syn Rank | Syn Score | Match? |
|---------|---------|----------|----------|-----------|---------|
| Concept A | 1 | [TBD] | [TBD] | [TBD] | [✓/✗] |
| Concept B | 2 | [TBD] | [TBD] | [TBD] | [✓/✗] |
| Concept C | 3 | [TBD] | [TBD] | [TBD] | [✓/✗] |
| ... | ... | ... | ... | ... | ... |

**Spearman Correlation:** [TBD] (p=[TBD])
**Top-3 Agreement:** [TBD]/3 concepts match

---

## Question-Level Performance

### Which Question Types Work Best?

[PLACEHOLDER FOR QUESTION TYPE ANALYSIS]

| Question Type | N Questions | Mean KL | Mean KS Sim | Pass Rate |
|---------------|-------------|---------|-------------|-----------|
| Purchase Intent | [TBD] | [TBD] | [TBD] | [TBD]% |
| Uniqueness | [TBD] | [TBD] | [TBD] | [TBD]% |
| Price Perception | [TBD] | [TBD] | [TBD] | [TBD]% |
| Likeability | [TBD] | [TBD] | [TBD] | [TBD]% |
| Diagnostics | [TBD] | [TBD] | [TBD] | [TBD]% |

**Findings:**
- [Best performing question types]
- [Question types that need work]
- [Systematic patterns or biases]

---

## Complexity Analysis

### Does System Scale with Concept Count?

**Hypothesis:** Performance should be independent of concept count (5 vs 24 concepts).

| Study | Concepts | KL | KS | Rank Corr | Status |
|-------|----------|-----|-----|-----------|---------|
| 61405445-01 | 5 | [TBD] | [TBD] | [TBD] | [TBD] |
| 61407069 | 8 | [TBD] | [TBD] | [TBD] | [TBD] |
| 61407185 | 8 | [TBD] | [TBD] | [TBD] | [TBD] |
| 61407017 | 24 | [TBD] | [TBD] | [TBD] | [TBD] |

**Analysis:**
- [Does performance degrade with more concepts?]
- [Is 24-concept study significantly worse than 5-concept?]
- [Statistical test for trend]

**Finding:** [System scales well | Performance degrades | Inconclusive]

---

## Known Limitations

### 1. Concept Matching Issues

**Finding:** Some concepts fail to match between PPTX and ground truth.

**Examples:**
- Study 61407017: "Wealth Buddy" (1/24 concepts)
- Study 61407069: 5/8 concepts failed to match
- Study 61407185: "Drop'd", "Goals Feel Better Together" (2/8 concepts)

**Impact:**
- Missing data for unmatched concepts
- Reduces effective sample size
- Not a methodology problem - just data preprocessing issue

**Mitigation:**
- Manual concept mapping
- Standardized naming conventions
- Doesn't affect validity of matched concepts

### 2. Sample Size Asymmetry

**Synthetic:** n=50 per study
**Ground Truth:** n=150-805 per study

**Is this a problem?**
- No - we're comparing distributions, not absolute counts
- 50 respondents sufficient for distribution-level analysis
- Statistical tests account for sample size differences
- Could increase to n=100 if needed, but not necessary

### 3. Geographic Limitation

**Validated:** US market only
**Not Yet Validated:** UK, CZ, GR, AT markets

**Risk:**
- Cultural/language differences may affect quality
- Demographics may differ significantly
- Question interpretations may vary

**Mitigation Plan:**
- Validate UK/CZ markets next (Q1 2026)
- Compare cross-market quality
- Expand gradually with validation at each step

### 4. Question Type Coverage

**Validated:** Standard Kantar scales (Purchase Intent, Uniqueness, Likeability, etc.)
**Not Validated:** Free-text responses, custom scales, open-ended

**Current Scope:**
- System handles closed-ended questions with defined scales
- Free-text evaluated qualitatively (not quantitatively)
- Custom scales may require calibration

---

## Statistical Validity Assessment

### Pass/Warn/Fail Criteria

**PASS - System is Statistically Valid:**
- ✅ Mean KL divergence < 0.20 across studies
- ✅ Mean KS similarity > 0.85 across studies
- ✅ Mean rank correlation > 0.85 across studies
- ✅ Top-1 agreement ≥ 75% (3/4 studies match winner)
- ✅ No systematic biases detected

**WARN - System Works with Caveats:**
- ⚠️ 2-3 out of 4 criteria met
- ⚠️ Some question types underperform
- ⚠️ One study shows significantly worse performance
- → Requires expert review before use

**FAIL - System Not Ready:**
- ❌ <2 out of 4 criteria met
- ❌ Systematic biases present
- ❌ Top-1 agreement < 50%
- → Requires methodology changes

### Overall Assessment: [TBD]

[Analysis of whether system passes, warns, or fails based on actual results]

**Conclusion:** [System is statistically valid | System has limitations | System needs work]

**Recommendation:** [Ready for use | Use with caution | Requires calibration]

---

## Technical Details

### System Configuration

**Models:**
- Response generation: GPT-4o-mini (gpt-4o-mini-2024-07-18)
- Concept extraction: GPT-4o (gpt-4o-2024-08-06)
- Embeddings: text-embedding-3-small (1536 dimensions)

**Generation Parameters:**
- Concepts per respondent: 3 (randomly selected)
- Demographics: Sampled from ground truth distributions
- Temperature: [Default for each model]
- Max tokens: Varies by question type

**Validation Approach:**
- Question-level metrics calculated independently
- Aggregated to study-level statistics
- Cross-study averages for overall assessment

### Reproducibility

**All results are reproducible:**
- Code: `src/kantar/survey_runner.py`, `src/kantar/validation_runner.py`
- Data: `data/synthetic/kantar/[STUDY_ID]/US/`
- Random seed: [TBD if set]
- Validation script: `statistical_validation_analysis.py`

**To Reproduce:**
```bash
# Generate synthetic data
python -m src.kantar.survey_runner --study [STUDY_ID] --market US --num-respondents 50 --model gpt-4o-mini --use-gt-demographics

# Run validation
python -m src.kantar.validation_runner --study [STUDY_ID] --market US --synthetic data/synthetic/kantar/[STUDY_ID]/US/synthetic_*.xlsx

# Generate statistical report
python statistical_validation_analysis.py
```

---

## Conclusions

### What We've Proven

[TO BE FILLED AFTER VALIDATION COMPLETES]

**Distribution Similarity:**
- [X/4] studies pass KL divergence threshold
- [X/4] studies pass KS similarity threshold
- Mean difference: [TBD]%

**Ranking Preservation:**
- [X/4] studies pass rank correlation threshold
- [X/4] studies correctly identify top concept
- Top-3 agreement: [TBD]%

**Overall System Validity:**
- [PASS/WARN/FAIL]
- [Ready for use | Needs calibration | Not ready]

### Next Steps

**If PASS:**
1. Expand to UK/CZ markets for geographic validation
2. Test on additional concept types (FMCG, automotive, etc.)
3. Deploy as screening tool with continuous monitoring

**If WARN:**
1. Analyze underperforming questions/studies
2. Calibrate prompts or scale mappings
3. Increase sample size if needed (50 → 100 respondents)

**If FAIL:**
1. Deep dive into methodology issues
2. Review SSR anchor statements
3. Consider alternative approaches

---

## Appendix: Statistical Test Details

### KL Divergence Calculation

```
KL(P||Q) = Σ P(i) * log(P(i) / Q(i))

Where:
- P = Ground truth distribution
- Q = Synthetic distribution
- i = Each scale level/category

Smoothing: Add ε=1e-10 to avoid log(0)
```

### KS Test Interpretation

**Null Hypothesis:** Synthetic and GT come from same distribution
**Alternative:** They come from different distributions

**If p-value < 0.05:** Reject null (distributions differ)
**If p-value ≥ 0.05:** Fail to reject (distributions may be same)

**KS Similarity = 1 - KS Statistic**

### Spearman Correlation Calculation

Ranks concepts by mean score, then calculates correlation of ranks:
```
ρ = 1 - (6 * Σd²) / (n * (n² - 1))

Where:
- d = difference in ranks for each concept
- n = number of concepts
```

---

**END OF PRESENTATION**

**For Questions:**
- Full statistical validation report: `STATISTICAL_VALIDATION_REPORT.md`
- Code repository: `src/kantar/`
- Validation data: `data/synthetic/kantar/`
