# Experiment Log - Kantar Synthetic Survey Validation

## Objective
Improve synthetic survey data validation metrics to match human test-retest reliability standards:
- **Target Correlation**: >0.85 (85% of human reliability)
- **Target KL Divergence**: <0.20 (acceptable distribution match)
- **Target KS Similarity**: >0.85 (paper benchmark)

---

## Baseline Performance

### Current Best: fix/uniqueness-scoring branch
**Date**: 2025-12-18
**Branch**: `fix/uniqueness-scoring`
**Respondents**: 75

**Overall Metrics**:
- Mean KL Divergence: 0.3110
- Correlation: 0.2859 (33.6% of target)
- KS Similarity: 0.7256
- Correlation Attainment: 33.6%

**Question-Level Performance**:
| Question | KL Divergence | GT Mean | Syn Mean | Difference |
|----------|---------------|---------|----------|------------|
| EXCITMENT | 0.0961 | 2.59 | 2.24 | -0.35 |
| RELVANCE | 0.1142 | 2.44 | 2.54 | +0.09 |
| PRPURINT | 0.1791 | 3.21 | 3.76 | +0.55 |
| PRVALMNY | 0.1850 | 3.54 | 3.06 | -0.48 |
| LIKBILTY | 0.3926 | 3.71 | 3.12 | -0.59 |
| UNIQNESS | 0.4626 | 3.64 | 2.50 | -1.14 |
| BELVBLTY | 0.7787 | 3.03 | 2.34 | -0.69 |

**Key Observation**: Systematic conservative bias - synthetic respondents rate concepts 15-38% lower than ground truth.

---

## Experiment History

### Experiment 1: Uniqueness Anchor Improvements
**Date**: 2025-12-17
**Branch**: `fix/uniqueness-scoring`
**Hypothesis**: Uniqueness anchors have poor semantic distinctiveness causing mapping errors

**Changes**:
- Revised uniqueness anchors to maximize semantic distance
- Added explicit novelty language at high end
- Added explicit familiarity language at low end

**Results**:
- Uniqueness KL: 0.6479 → 0.4626 (**29% improvement**)
- Overall Mean KL: 0.3449 → 0.3110 (**10% improvement**)
- Correlation: 0.2859 (unchanged)

**Conclusion**: ✓ SUCCESS - Anchor improvements work for specific constructs
**Status**: Merged to main baseline

---

### Experiment 2: Believability Anchor Improvements
**Date**: 2025-12-17
**Branch**: `fix/believability-v2` (deleted)
**Hypothesis**: Believability anchors lack semantic distinctiveness

**Changes**:
- Removed "completely" intensifier
- Added varied uncertainty markers (skeptical, doubtful, uncertain)
- Attempted to increase semantic distance

**Results**:
- Believability KL: 0.6282 → 0.7787 (**24% WORSE**)
- Overall Mean KL: 0.3110 → 0.3159 (**2% worse**)

**Conclusion**: ✗ FAILED - Anchor changes increased semantic overlap
**Root Cause**: Removed intensifier without sufficient compensation
**Status**: Branch deleted, reverted to baseline

---

### Experiment 3: Czech Market Context
**Date**: 2025-12-18
**Branch**: `fix/add-czech-market-context` (deleted)
**Hypothesis**: Missing Czech market context causes conservative bias (ground truth is Czech consumers)

**Changes**:
- Added market parameter to `build_system_prompt()` (default: "Czech Republic")
- Added market familiarity context: "You are familiar with the {market} lottery and scratchcard market, including local brands, typical prices in CZK..."
- Added market-specific response guidance

**Results**:
- Believability KL: 0.7787 → 0.4915 (**37% improvement**)
- Uniqueness KL: 0.4626 → 0.6749 (**46% WORSE**)
- Likeability KL: 0.3926 → 0.5548 (**41% WORSE**)
- Overall Mean KL: 0.3110 → 0.3449 (**11% worse**)
- Correlation: 0.2859 → 0.3318 (**16% improvement**)

**Conclusion**: ✗ FAILED - Mixed results, overall worse performance
**Analysis**: Market context helped one construct but hurt others, suggesting multiple root causes
**Status**: Branch deleted, reverted to baseline

---

## Current Investigation

### Experiment 4: LLM Response Analysis
**Date**: 2025-12-18
**Status**: BLOCKED
**Hypothesis**: Need to understand if bias is in response generation or SSR mapping

**Approach**:
1. Analyze actual free-text responses from LLM
2. Compare language patterns to ground truth (if available)
3. Check if SSR semantic similarity mapping is accurate
4. Identify if responses are genuinely conservative or mapping is faulty

**Questions to Answer**:
- Are LLM responses genuinely more negative/cautious in language?
- Is SSR correctly mapping positive responses to high scores?
- Are there linguistic patterns that explain the systematic bias?
- Does the bias vary by persona type or concept?

**Blocker**: Free-text responses are not saved in output Excel files - only final SSR scores are retained. Would need to modify pipeline to save responses or examine logs.

**Alternative Approach**: Given the systematic nature of the bias (affects ALL questions), the issue is likely in the prompt/response generation rather than SSR mapping. SSR mapping issues would be more random.

### Experiment 5: Direct Scale Response (Proposed)
**Status**: RECOMMENDED NEXT STEP
**Hypothesis**: The conservative bias stems from the two-step process (generate text → map to scale). Direct scale response would isolate whether the problem is response generation or SSR mapping.

**Approach**:
1. Modify prompt to have LLM directly output 1-5 ratings instead of free text
2. Include scale anchors in prompt as context
3. Run 100-respondent generation with direct ratings
4. Compare validation metrics

**Expected Outcomes**:
- **If metrics improve significantly**: Problem is in SSR semantic mapping
- **If bias persists**: Problem is in LLM's understanding/interpretation of constructs
- **If bias worsens**: SSR mapping was actually helping moderate the bias

**Advantages**:
- Quick to implement (modify prompts only)
- Clear diagnostic test
- No API cost increase (no embedding calls)

**Disadvantages**:
- Loses rich qualitative data
- May not match paper's SSR methodology
- Could introduce different biases (number anchoring)

**Estimated time**: 2-3 hours (implementation + generation + validation)

---

## Hypothesis Tracker

### Active Hypotheses
1. **SSR Mapping Error**: Semantic similarity may not be correctly mapping free-text to scales
2. **Response Generation Bias**: LLM may be inherently conservative in synthetic consumer responses
3. **Temperature/Sampling**: Model parameters may need tuning for more varied responses

### Rejected Hypotheses
1. ~~Uniqueness anchors lack semantic distinctiveness~~ → Fixed in Exp 1
2. ~~Missing Czech market context~~ → Mixed results in Exp 3, not primary cause
3. ~~Believability anchors lack semantic distinctiveness~~ → Made worse in Exp 2

---

## Lessons Learned

1. **Anchor improvements work for specific constructs** but don't address systematic bias across all questions
2. **Market context is relevant but not sufficient** - helps some constructs, hurts others
3. **Multiple root causes likely** - no single fix addresses the systematic conservative bias
4. **Need diagnostic analysis** before more fixes - must understand response generation vs mapping issues

---

## Notes

- Always use `gpt-4.1` model (user requirement)
- Ground truth: 400 Czech respondents, 8400 responses
- Synthetic: Target 100 respondents (75-80 valid after screening)
- Validation compares 7 common questions between datasets
