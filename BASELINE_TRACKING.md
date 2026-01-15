# Baseline Tracking - Synthetic Data Generation Configuration

This document tracks the configuration evolution and baseline datasets for the Kantar synthetic survey data generation system.

---

## Configuration History

### Configuration v1: Initial Setup (December 18, 2025)

**Purpose:** Proof of concept for synthetic survey generation

**Configuration:**
- **LLM Model:** gpt-4.1
- **Embedding Model:** text-embedding-3-small
- **Generation Mode:** Default distributions (no ground truth integration)
- **Scale Definitions:** Initial version
  - PURCHASE_INTENT (5-point)
  - UNIQUENESS (5-point)
  - VALUE_FOR_MONEY (5-point)
  - LIKEABILITY (5-point)
  - RELEVANCE (5-point)
  - EXCITEMENT (5-point)
  - BELIEVABILITY (5-point)
- **Demographics:** Generic market profiles

**Baseline Dataset:**
- **File:** `data/synthetic/synthetic_data_100resp_20251218_161648.xlsx`
- **Metadata:** `data/synthetic/metadata_synthetic_data_100resp_20251218_161648.json`
- **Respondents:** 100
- **Concepts:** 8 generic concepts
- **Timestamp:** 2025-12-18 16:16:48

**Status:** ✅ Archived baseline - represents initial capability

---

### Configuration v2: Ground Truth Integration + Scale Fixes (January 8-13, 2026)

**Purpose:** Integrate with Kantar ground truth data and fix scale label mismatches

**Major Changes:**
1. **Ground Truth Demographics:** Added ability to sample demographics from actual Kantar data
2. **Kantar Study Integration:** Added study catalog and market-specific generation
3. **Scale Bug Fix #1 (Jan 13, commit `689b4b9`):**
   - Fixed LIKEABILITY scale level 4 semantic mismatch
   - Changed from generic description to Kantar-compliant wording

4. **Scale Bug Fix #2 (Jan 13, commit `9340fcf`):**
   - Fixed UNPRICEP (Price Perception) scale labels
   - Aligned with ground truth format exactly

**Configuration:**
- **LLM Model:** gpt-4o-mini (switched from gpt-4.1)
- **Embedding Model:** text-embedding-3-small
- **Generation Mode:** Ground truth demographics enabled
- **Scale Definitions:** Fixed version (post-689b4b9 and 9340fcf)
- **Demographics:** Extracted from Kantar ground truth Excel files
- **Demographics Schema:** Mandatory validation in GT mode

**Baseline Dataset:**
- **File:** `data/synthetic/kantar/61405445-01/US/synthetic_US_50resp_20260113_174608.xlsx`
- **Metadata:** `data/synthetic/kantar/61405445-01/US/metadata_US_20260113_174608.json`
- **Study:** 61405445-01 (iGaming Concept Evaluate)
- **Market:** US
- **Respondents:** 50
- **Concepts:** 5 (Pulse Play, Standard or VIP Mode, Happy Hour, Bet-Volume Must-Win Jackpots, Time-Locked Must-Win Jackpots)
- **Ground Truth:** 250 respondents
- **Timestamp:** 2026-01-13 17:46:08

**Validation Metrics (Jan 13):**
- Mean KL Divergence: TBD (validation added later)
- KS Similarity: TBD
- Questions Validated: 112 question columns available

**Status:** ✅ Current production baseline (as of Jan 15, 2026)

---

### Configuration v3: Validation Infrastructure (January 14-15, 2026)

**Purpose:** Add automated validation and multi-study support

**Major Changes:**
1. **Validation Runner:** `src/kantar/validation_runner.py`
   - Automated KL divergence calculation
   - KS statistic for distribution similarity
   - Correlation metrics
   - Success criteria thresholds

2. **Multi-Study Support:**
   - Expanded to 4 studies: 61405445-01, 61407017, 61407069, 61407185
   - Study catalog with auto-discovery

3. **Presentation Reports:**
   - `scripts/generate_validation_presentation.py`
   - Statistical analysis scripts

**Configuration:**
- **LLM Model:** gpt-4o-mini
- **Embedding Model:** text-embedding-3-small
- **Generation Mode:** Ground truth demographics enabled
- **Scale Definitions:** Same as v2 (fixed version)
- **Validation:** Automated metrics tracking
- **Success Criteria:**
  - KL Divergence < 0.20 (target)
  - KS Similarity > 0.85 (target)
  - Correlation > 0.85 (target)

**Latest Validation Run (Jan 15, 2026):**
- **Study 61405445-01:**
  - Mean KL: 3.0510 (❌ above target - incomplete generation)
  - KS Similarity: 0.7519 (❌ below target)
  - Questions Validated: 30/112 (only 27% - incomplete)

- **Study 61407017:**
  - Mean KL: 0.0561 (✅ excellent)
  - KS Similarity: 0.9945 (✅ excellent)
  - Questions Validated: 2/148 (only demographics - incomplete)

- **Study 61407069:**
  - Mean KL: 3.4778 (❌ above target)
  - KS Similarity: 0.7996 (❌ below target)
  - Questions Validated: 12/175 (incomplete)

- **Study 61407185:**
  - Mean KL: 3.3763 (❌ above target)
  - KS Similarity: 0.7924 (❌ below target)
  - Questions Validated: 22/175 (incomplete)

**Status:** 🔄 Active development - Jan 14 runs were incomplete, fresh generation in progress (Jan 15)

---

## Scale Definition Evolution

### Initial Scales (v1)
All scales used generic 5-point definitions.

### Fixed Scales (v2+)

**LIKEABILITY Scale:**
- **Bug:** Level 4 had semantic mismatch
- **Fix (commit 689b4b9):** Aligned level 4 description with Kantar ground truth
- **Impact:** Improved distribution accuracy for likeability questions

**UNPRICEP (Price Perception) Scale:**
- **Bug:** Scale labels didn't match ground truth format
- **Fix (commit 9340fcf):** Updated all level labels to match Kantar exactly
- **Impact:** Critical fix for price perception question validation

### Current Scale Registry
Located in: `src/scales/registry.py`

Scales supported:
- PURCHASE_INTENT (5-point, unpriced)
- PURCHASE_INTENT_PRICED (5-point, priced)
- UNIQUENESS (5-point)
- UNPRICEP (Price Perception, 5-point) ✅ Fixed
- LIKEABILITY (5-point) ✅ Fixed
- INCREMENTALITY (5-point)
- RELEVANCE (5-point)
- PLAYFULNESS (5-point)
- EXCITEMENT (5-point)
- BELIEVABILITY (5-point)

---

## Cleanup History

### January 15, 2026 - Full Baseline Cleanup

**Deleted Files (38 total):**
- Root level: 2 duplicate 100-resp runs + metadata
- Study 61405445-01: 32 outdated files
  - All 1/2/5-respondent test runs
  - Pre-scale-fix 20/50-respondent runs
  - Old validation JSONs
- Studies 61407017/61407069/61407185: 4 validation-only artifacts

**Preserved Files:**
- v1 baseline: `synthetic_data_100resp_20251218_161648.xlsx`
- v2 baseline: `synthetic_US_50resp_20260113_174608.xlsx`
- Associated metadata and latest validations

**Rationale:**
- Old generations used outdated configurations (pre-scale-fixes)
- Jan 14 generations were incomplete (most questions empty)
- Clean slate for current configuration runs

---

## Current Baseline (as of January 15, 2026)

**Active Configuration:** v2 (ground truth + scale fixes)

**Baseline Dataset:**
- Study 61405445-01, US market
- 50 respondents, 5 concepts
- Post-scale-fixes (both LIKEABILITY and UNPRICEP)
- File: `synthetic_US_50resp_20260113_174608.xlsx`

**Next Steps:**
1. Complete fresh 50-respondent generation for all 4 studies (in progress)
2. Run full validation on complete datasets
3. Establish validated baselines for each study
4. Document final metrics in this file

---

## Future Configuration Changes

When configuration changes occur, document:
1. What changed and why
2. Git commit hash
3. Generate new baseline dataset
4. Run validation comparing to previous baseline
5. Update this document
6. Archive or delete superseded baselines (keep 1-2 for reference)

---

**Last Updated:** January 15, 2026
**Current Config Version:** v3 (validation infrastructure)
**Active Baseline:** v2 dataset (Jan 13, 2026)
