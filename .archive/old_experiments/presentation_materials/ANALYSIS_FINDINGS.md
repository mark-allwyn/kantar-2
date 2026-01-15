# Analysis Findings: Systematic Conservative Bias

**Date**: 2025-12-18
**Branch**: `fix/uniqueness-scoring` (current best baseline)
**Current Performance**: Mean KL 0.3110, Correlation 0.2859 (33.6% of target)

---

## Problem Statement

Synthetic survey respondents consistently rate scratchcard concepts **15-38% lower** than Czech ground truth respondents across all constructs. This systematic conservative bias prevents us from achieving validation targets (Correlation >0.85, KL <0.20).

### Evidence of Systematic Bias

| Question | Ground Truth Mean | Synthetic Mean | Difference | % Lower |
|----------|-------------------|----------------|------------|---------|
| Believability | 3.03 | 2.34 | -0.69 | -23% |
| Uniqueness | 3.64 | 2.50 | -1.14 | -31% |
| Likeability | 3.71 | 3.12 | -0.59 | -16% |
| Value for Money | 3.54 | 3.06 | -0.48 | -14% |
| Purchase Intent | 3.21 | 3.76 | +0.55 | +17% |
| Relevance | 2.44 | 2.54 | +0.09 | +4% |
| Excitement | 2.59 | 2.24 | -0.35 | -14% |

**Pattern**: 5 out of 7 questions show conservative bias; only Purchase Intent and Relevance show near-accurate or positive bias.

---

## Experiments Conducted

### Experiment 1: Uniqueness Anchor Improvements ✓ SUCCESS
- **Result**: Uniqueness KL improved 29% (0.65 → 0.46)
- **Learning**: Anchor text improvements work for specific constructs
- **Limitation**: Does not address systematic bias across all questions

### Experiment 2: Believability Anchor Improvements ✗ FAILED
- **Result**: Believability KL worsened 24% (0.63 → 0.78)
- **Root Cause**: Removed intensifier without sufficient semantic compensation
- **Learning**: Anchor modifications require careful semantic distance analysis

### Experiment 3: Czech Market Context ✗ FAILED
- **Result**: Overall Mean KL worsened 11% (0.31 → 0.34)
- **Mixed Results**:
  - Believability improved 37% (0.78 → 0.49)
  - Uniqueness worsened 46% (0.46 → 0.67)
  - Likeability worsened 41% (0.39 → 0.55)
- **Learning**: Market context helps some constructs but hurts others; not a universal solution

### Experiment 4: LLM Response Analysis ⚠ BLOCKED
- **Blocker**: Free-text responses not saved in output files
- **Alternative Conclusion**: Systematic bias (affects ALL questions consistently) suggests problem is in prompt/response generation rather than SSR mapping
- **Reasoning**: SSR mapping errors would be more random, not systematic

---

## Key Insights

### 1. Systematic Nature Points to Prompt Issues
The bias affects nearly all questions with similar magnitude, suggesting:
- LLM is interpreting ALL constructs conservatively
- Problem is likely in system prompt or persona conditioning
- Not an SSR mapping issue (which would be more variable)

### 2. Anchor Improvements Have Limited Scope
- Work well for individual constructs (see Uniqueness success)
- Do not address underlying systematic bias
- Can even backfire if not carefully tuned (see Believability failure)

### 3. Market Context is Construct-Specific
- Helps constructs tied to local knowledge (Believability)
- Hurts constructs that are more universal (Likeability, Uniqueness)
- Not a universal fix for systematic bias

### 4. Purchase Intent Bucking the Trend
Purchase Intent is the ONLY question showing positive bias (+17%). Why?
- Different prompt structure (includes price explicitly)?
- More concrete/actionable question?
- Suggests systematic bias may be construct-type dependent

---

## Root Cause Hypotheses (Ranked)

### 1. SSR Two-Step Process Introduces Conservative Bias (HIGH PRIORITY)
**Hypothesis**: The generate-text-then-map approach causes conservatism
- LLM generates nuanced text → SSR maps to nearest anchor → systematically underestimates
- Analogous to "regression to the mean" in statistical mapping

**Test**: Direct scale response (LLM outputs 1-5 directly)
**Priority**: HIGH - Quick to test, clear diagnostic

### 2. System Prompt Induces Conservative Responses (MEDIUM PRIORITY)
**Hypothesis**: Current prompt language makes LLM overly cautious
- "Be honest" → LLM interprets as "be critical"
- "Express genuine opinions" → LLM expresses skepticism
- No positive framing or enthusiasm cues

**Test**: Add prompt variations encouraging authentic enthusiasm
**Priority**: MEDIUM - Requires careful prompt engineering

### 3. Persona Conditioning Too Generic (LOW PRIORITY)
**Hypothesis**: Personas lack sufficient detail to generate varied responses
- Current personas: age, gender, basic demographics
- Missing: personality traits, risk tolerance, enthusiasm levels

**Test**: Enrich personas with psychographic attributes
**Priority**: LOW - More complex, less clear diagnostic

### 4. Model Temperature/Sampling Too Conservative (LOW PRIORITY)
**Hypothesis**: Current model parameters favor safe/middle responses
**Test**: Increase temperature, adjust top_p
**Priority**: LOW - Paper doesn't specify these parameters

---

## Recommended Next Steps

### Option A: Direct Scale Response Experiment (RECOMMENDED)
**Objective**: Isolate whether bias is in response generation vs. SSR mapping

**Implementation**:
1. Modify prompts to request direct 1-5 ratings
2. Include scale anchor descriptions in prompt
3. Run 100-respondent generation
4. Compare validation metrics to SSR baseline

**Expected Outcomes**:
- **Metrics improve**: SSR mapping is the problem → optimize embedding model or anchors
- **Bias persists**: Response generation is the problem → focus on prompts/personas
- **Metrics worsen**: SSR was helping → investigate hybrid approaches

**Time**: 2-3 hours
**Cost**: Lower (no embedding API calls)
**Risk**: Low (easy to revert)

### Option B: Prompt Engineering for Enthusiasm (ALTERNATIVE)
**Objective**: Test if prompt language induces conservatism

**Implementation**:
1. Add positive framing: "Share what excites you" vs "Be honest"
2. Include enthusiasm cues in system prompt
3. Test with 25-respondent pilot

**Time**: 3-4 hours
**Risk**: Medium (could introduce opposite bias)

### Option C: Hybrid SSR + Direct Rating (FUTURE)
**Objective**: Get best of both worlds

**Implementation**:
1. LLM generates text + confidence rating (1-5)
2. Use SSR for validation, confidence for weighting
3. Blend approaches based on validation performance

**Time**: 1-2 days
**Risk**: High (complex implementation)

---

## Success Criteria

For any next experiment to be considered successful:
1. **Mean KL Divergence**: < 0.25 (currently 0.31)
2. **Correlation**: > 0.50 (currently 0.29)
3. **No question degrades**: No question's KL should worsen by >20%

Ultimate targets (paper benchmark):
- **Correlation**: > 0.85
- **Mean KL**: < 0.20
- **KS Similarity**: > 0.85

---

## Open Questions

1. Why does Purchase Intent show positive bias when others don't?
2. Would few-shot examples from ground truth calibrate responses?
3. Is the conservative bias model-specific (gpt-4.1) or universal?
4. Do different persona types show different bias magnitudes?
5. Would ensemble approaches (multiple models) reduce bias?

---

## Documentation

All experiments tracked in: `EXPERIMENT_LOG.md`
Validation reports: `data/validation/validation_report.txt`
Metrics CSV: `data/validation/validation_metrics.csv`
