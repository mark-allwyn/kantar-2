# Statistical Validation Workflow

**Goal:** Prove that synthetic survey data is statistically valid through rigorous quantitative analysis.

---

## Quick Start

### Current Status

✅ **Generation:** 3 jobs running (61407017, 61407069, 61407185)
✅ **Existing Data:** 1 study validated (61405445-01/US)
⏳ **Waiting:** For generation jobs to complete (~15-30 min)

### When Ready

```bash
# 1. Check if generation is complete
ls -lh data/synthetic/kantar/61407017/US/synthetic_*.xlsx
ls -lh data/synthetic/kantar/61407069/US/synthetic_*.xlsx
ls -lh data/synthetic/kantar/61407185/US/synthetic_*.xlsx

# 2. Run validation on all 4 studies
python -m src.kantar.validation_runner --study 61405445-01 --market US --synthetic data/synthetic/kantar/61405445-01/US/synthetic_US_50resp_*.xlsx
python -m src.kantar.validation_runner --study 61407017 --market US --synthetic data/synthetic/kantar/61407017/US/synthetic_US_50resp_*.xlsx
python -m src.kantar.validation_runner --study 61407069 --market US --synthetic data/synthetic/kantar/61407069/US/synthetic_US_50resp_*.xlsx
python -m src.kantar.validation_runner --study 61407185 --market US --synthetic data/synthetic/kantar/61407185/US/synthetic_US_50resp_*.xlsx

# 3. Generate statistical validation report
python statistical_validation_analysis.py

# 4. View results
cat STATISTICAL_VALIDATION_REPORT.md
```

---

## Detailed Workflow

### Step 1: Wait for Generation to Complete

**Check status of background jobs:**
```bash
ps aux | grep survey_runner | grep -v grep
```

**If jobs are still running:** They output to `stderr` with progress logs. Estimated time: 15-30 minutes total.

**When complete:** You'll see 3 new Excel files:
- `data/synthetic/kantar/61407017/US/synthetic_US_50resp_[timestamp].xlsx`
- `data/synthetic/kantar/61407069/US/synthetic_US_50resp_[timestamp].xlsx`
- `data/synthetic/kantar/61407185/US/synthetic_US_50resp_[timestamp].xlsx`

### Step 2: Run Validation

**For each study, run validation:**

```bash
python -m src.kantar.validation_runner \
  --study [STUDY_ID] \
  --market US \
  --synthetic data/synthetic/kantar/[STUDY_ID]/US/synthetic_US_50resp_*.xlsx
```

**What this does:**
1. Loads ground truth Excel from `data/kantar-survey-source/[STUDY_ID]/US/`
2. Loads synthetic Excel from specified path
3. Identifies common question columns
4. Calculates validation metrics for each question:
   - KL divergence (distribution similarity)
   - KS statistic (statistical test)
   - Correlation (if numeric)
5. Aggregates to study-level metrics
6. Saves results to JSON: `data/synthetic/kantar/[STUDY_ID]/US/validation_US_[timestamp].json`

**Expected output per study:**
```
INFO - Loading ground truth: [filename]
INFO - Loading synthetic: [filename]
INFO - Ground truth: X rows, Y columns
INFO - Synthetic: X rows, Y columns
INFO - Found Z question columns to validate
INFO - Checking categorical alignment...
INFO - Categorical alignment check: PASSED
INFO - Calculating validation metrics...
INFO - Progress: 10/Z questions
INFO - Progress: 20/Z questions
...
INFO - Validation complete: Z questions validated
INFO - Mean KL: X.XXX
INFO - KS Similarity: X.XXX
INFO - Saved validation results to: [path]
```

### Step 3: Run Statistical Analysis

**Execute the statistical validation script:**
```bash
python statistical_validation_analysis.py
```

**What this does:**
1. Finds all validation JSON files for the 4 studies
2. Loads synthetic and ground truth Excel files
3. Calculates comprehensive statistical metrics:
   - **Distribution metrics:** KL divergence, JS divergence, KS test, Chi-square, TVD, Hellinger
   - **Ranking metrics:** Spearman correlation, Kendall's Tau, Top-3/Top-1 agreement
   - **Statistical tests:** T-tests, effect sizes (Cohen's d)
4. Assesses PASS/WARN/FAIL status per study
5. Generates cross-study statistics
6. Outputs markdown report: `STATISTICAL_VALIDATION_REPORT.md`

**Expected output:**
```
================================================================================
STATISTICAL VALIDATION ANALYSIS
================================================================================

Analyzing 61405445-01...
  Found X comparable questions
  Status: [PASS/WARN/FAIL]

Analyzing 61407017...
  Found X comparable questions
  Status: [PASS/WARN/FAIL]

Analyzing 61407069...
  Found X comparable questions
  Status: [PASS/WARN/FAIL]

Analyzing 61407185...
  Found X comparable questions
  Status: [PASS/WARN/FAIL]

Generating report...
✓ Report written to: STATISTICAL_VALIDATION_REPORT.md
```

### Step 4: Review Results

**Open the statistical validation report:**
```bash
cat STATISTICAL_VALIDATION_REPORT.md
# or open in your markdown viewer
```

**Key sections to review:**

1. **Validation Summary Table**
   - Shows KL, KS, Rank Corr for each study
   - Overall PASS/WARN/FAIL status

2. **Detailed Study Analysis**
   - Per-study metrics breakdown
   - Which thresholds passed/failed
   - Specific issues identified

3. **Cross-Study Statistics**
   - Mean performance across all 4 studies
   - Overall assessment (PASS/WARN/FAIL)

**Look for:**
- ✅ All 4 studies PASS → System is statistically valid
- ⚠️ 3/4 PASS, 1 WARN → System works with caveats
- ❌ 2+ FAIL → System needs calibration

### Step 5: Populate Presentation

**Once you have results, update the presentation:**

Edit `TECHNICAL_POC_PRESENTATION.md` and replace all `[TBD]` with actual values from the statistical report.

**Key sections to fill in:**
- Slide 5: Results Summary table
- Slide 6: Distribution comparison examples
- Slide 7: Question-level performance
- Slide 8: Complexity analysis
- Slide 10: Overall assessment & conclusions

---

## Understanding the Metrics

### Distribution Similarity Metrics

**KL Divergence (Kullback-Leibler)**
- **What it measures:** How much synthetic distribution diverges from ground truth
- **Range:** 0 (identical) to ∞ (completely different)
- **Target:** < 0.20 (synthetic within 20% of GT)
- **Interpretation:**
  - 0.00-0.10: Excellent match
  - 0.10-0.20: Good match (within target)
  - 0.20-0.30: Moderate match (warning)
  - >0.30: Poor match (fail)

**KS Similarity (Kolmogorov-Smirnov)**
- **What it measures:** Maximum distance between cumulative distributions
- **Range:** 0-1 (calculated as 1 - KS statistic)
- **Target:** > 0.85 (85%+ similarity)
- **Interpretation:**
  - 0.90-1.00: Excellent
  - 0.85-0.90: Good (within target)
  - 0.75-0.85: Moderate (warning)
  - <0.75: Poor (fail)

**Total Variation Distance (TVD)**
- **What it measures:** Sum of absolute differences in probabilities
- **Range:** 0-1
- **Target:** < 0.10
- **Interpretation:** Maximum amount by which distributions differ

### Ranking Metrics

**Spearman Rank Correlation**
- **What it measures:** Whether concepts rank in same order (GT vs Synthetic)
- **Range:** -1 (opposite) to +1 (perfect agreement)
- **Target:** > 0.85 (85%+ rank agreement)
- **Interpretation:**
  - 0.90-1.00: Excellent ranking preservation
  - 0.85-0.90: Good (within target)
  - 0.70-0.85: Moderate (warning)
  - <0.70: Poor (fail)

**Top-3 Agreement**
- **What it measures:** Do the top 3 concepts match?
- **Range:** 0% to 100%
- **Target:** ≥ 67% (at least 2/3 match)
- **Interpretation:**
  - 100%: All 3 match (perfect)
  - 67%: 2/3 match (acceptable)
  - 33%: 1/3 match (poor)
  - 0%: None match (fail)

**Top-1 Agreement**
- **What it measures:** Does the winning concept match?
- **Binary:** Yes/No
- **Target:** 100% (winner must match)
- **Critical:** This is the most important for business decisions

### Statistical Significance Tests

**KS Test p-value**
- **Null hypothesis:** Distributions are the same
- **If p < 0.05:** Reject null (distributions significantly different)
- **If p ≥ 0.05:** Fail to reject (distributions may be same)
- **Note:** With small samples, may not reject even if distributions differ

**T-test for Means**
- Tests if mean scores differ significantly
- p-value interpretation same as KS test

**Chi-square Test**
- Tests if categorical distributions differ
- p-value interpretation same as KS test

---

## Troubleshooting

### Generation Jobs Not Completing

**Check if still running:**
```bash
ps aux | grep survey_runner
```

**Check for errors:**
```bash
# View output of background job (use job ID from when started)
# Job IDs were: 3a3a4b, f9c02a, 037490
```

**If stuck/failed:**
- Kill and restart: `kill [PID]`
- Check API quota/rate limits
- Review error messages in job output

### Validation Fails with "File Not Found"

**Check if synthetic file exists:**
```bash
ls data/synthetic/kantar/[STUDY_ID]/US/synthetic_*.xlsx
```

**If missing:**
- Generation may not have completed
- Check generation job status
- Look for error messages

### Concept Matching Issues

**Warning in validation output:**
```
WARNING - No match found for concept: 'Wealth Buddy'
```

**This is expected:**
- Some concepts have naming variations between PPTX and ground truth
- Doesn't affect validity of matched concepts
- Just means those specific concepts have no data in synthetic output

**Known issues:**
- 61407017: "Wealth Buddy" (1/24)
- 61407069: 5/8 concepts (naming mismatches)
- 61407185: "Drop'd", "Goals Feel Better Together" (2/8)

### Statistical Analysis Script Errors

**"No data available":**
- Check that validation JSONs exist in `data/synthetic/kantar/[STUDY]/US/`
- Run validation step first

**Import errors:**
- Install required packages: `pip install scipy matplotlib seaborn`

---

## Success Criteria

### PASS - System is Statistically Valid

All of the following must be true:
- ✅ Mean KL divergence < 0.20 across all 4 studies
- ✅ Mean KS similarity > 0.85 across all 4 studies
- ✅ Mean Spearman correlation > 0.85 across all 4 studies
- ✅ Top-1 agreement ≥ 75% (3/4 studies correctly identify winner)

**If PASS:**
- System is proven statistically valid
- Ready for use as screening tool
- Can present as successful POC

### WARN - System Works with Caveats

If 2-3 out of 4 main criteria are met, or:
- ⚠️ Some studies pass, others fail
- ⚠️ Specific question types consistently underperform
- ⚠️ One outlier study drags down averages

**If WARN:**
- System shows promise but has gaps
- Identify and document limitations
- Use with expert oversight
- May still be acceptable for POC depending on management risk tolerance

### FAIL - System Not Ready

If <2 out of 4 criteria met, or:
- ❌ Systematic biases detected across studies
- ❌ Top-1 agreement < 50%
- ❌ Multiple studies fail badly

**If FAIL:**
- System requires significant work
- Not ready for POC presentation
- Need to debug methodology, prompts, or SSR calibration

---

## Expected Timeline

**Total time from now:** ~1-2 hours

1. **Generation completion:** 15-30 minutes (already running)
2. **Validation (4 studies):** 5-10 minutes total (mostly I/O)
3. **Statistical analysis:** 2-5 minutes
4. **Review & present:** 30-60 minutes

**You can start presenting as soon as STATISTICAL_VALIDATION_REPORT.md is generated.**

---

## Next Steps After Validation

### If Results are Good (PASS)

1. **Present POC:**
   - Use `TECHNICAL_POC_PRESENTATION.md` as slide deck
   - Share `STATISTICAL_VALIDATION_REPORT.md` as supporting document
   - Highlight statistical rigor and validation methodology

2. **Expand Validation:**
   - Add UK, CZ markets (geographic generalization)
   - Test other concept types (FMCG, automotive, etc.)
   - Validate segmented studies (61406317, 61407240)

3. **Production Deployment:**
   - Deploy as internal screening tool
   - Set up continuous monitoring
   - Build feedback loop for calibration

### If Results Need Work (WARN/FAIL)

1. **Diagnose Issues:**
   - Which questions underperform?
   - Which studies fail?
   - Are there systematic patterns?

2. **Calibrate:**
   - Adjust SSR anchor statements
   - Refine prompts for weak question types
   - Increase sample size (50 → 100)

3. **Revalidate:**
   - Generate new synthetic data with improvements
   - Rerun validation
   - Compare before/after metrics

---

## Files Created

**Statistical Analysis:**
- `statistical_validation_analysis.py` - Main analysis script
- `STATISTICAL_VALIDATION_REPORT.md` - Generated output (after running script)

**Presentation:**
- `TECHNICAL_POC_PRESENTATION.md` - Technical presentation focused on statistics
- `VALIDATION_REPORT_TEMPLATE.md` - Comprehensive technical report template

**Workflow Guides:**
- `STATISTICAL_VALIDATION_WORKFLOW.md` - This file
- `PRESENTATION_DELIVERABLES_README.md` - Overview of all deliverables

**Legacy/Optional:**
- `PRESENTATION_POC.md` - Business-focused presentation (includes cost analysis)
- `COST_MODEL.csv` - Financial model (if needed later)

---

**Ready to Execute!** Just wait for generation to complete, then run the 3-step workflow above.
