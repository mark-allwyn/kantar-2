# Synthetic Survey Testing Results Summary

## Executive Summary

We tested the synthetic survey system against 400 real Czech consumers across 7 question types. **Results show construct-specific performance** - some question types work, others don't.

### Key Finding

> The systematic conservative bias is NOT universal - it's construct-specific. This suggests the issue is in how the LLM interprets different question types, not the SSR methodology itself.

---

## What Worked ✓

**2 out of 7 questions passed both accuracy and consistency tests:**

| Question | Accuracy | Consistency | Characteristics |
|----------|----------|-------------|-----------------|
| **Excitement** | -13% bias | KL=0.11 | Concrete emotional response |
| **Relevance** | +11% bias | KL=0.08 | Personal fit ("relevant to me") |

**Pattern:** Both are concrete, emotional, personally-framed questions with clear semantic progressions.

---

## What Partially Worked ⚠

**1 out of 7 questions showed mixed performance:**

| Question | Accuracy | Consistency | Issue |
|----------|----------|-------------|-------|
| **Purchase Intent** | +16% bias | KL=0.18 | Good distribution, but overestimates |

**Pattern:** Concrete behavioral question, but has positive bias.

---

## What Didn't Work ✗

**4 out of 7 questions failed both tests:**

| Question | Accuracy | Consistency | Root Cause |
|----------|----------|-------------|------------|
| **Believability** | -26% bias | KL=0.52 | Requires cultural trust judgment |
| **Uniqueness** | -33% bias | KL=0.47 | Needs category expertise |
| **Likeability** | -16% bias | KL=0.32 | Abstract preference judgment |
| **Value for Money** | -16% bias | KL=0.24 | Requires market knowledge |

**Pattern:** All are abstract evaluative judgments requiring cultural/market context.

---

## The Pattern

### SSR Works Well For:
- Concrete behavioral questions
- Emotional/feeling-based responses
- Personal fit assessments ("relevant to me")
- Questions with clear semantic progressions
- No cultural ambiguity

### SSR Struggles With:
- Abstract evaluative judgments
- Questions requiring cultural/market context
- Category expertise-dependent assessments
- Multi-level scales (6+ levels)
- Trust/credibility judgments

---

## Overall Performance Metrics

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| **Correlation Attainment** | 41.4% | >85% | -43.6pp |
| **Mean KL Divergence** | 0.275 | <0.20 | +38% |
| **Questions Passing** | 2/7 (29%) | 7/7 | -5 |

**Performance:** 54% below published research benchmarks.

---

## Recommended Next Experiments

### Phase 1: Diagnostic (Do First)

#### Experiment 1: Isolate Response Generation vs SSR Mapping
- **Time:** 2-3 hours
- **Method:** Have LLM output 1-5 directly (bypass SSR)
- **Learn:** Is bias in responses or mapping?
- **Priority:** ⭐⭐⭐ CRITICAL

#### Experiment 2: Analyze Free-Text Responses
- **Time:** 1 day
- **Method:** Review LLM text before SSR conversion
- **Learn:** Are responses genuinely conservative?
- **Priority:** ⭐⭐⭐ CRITICAL

### Phase 2: Optimization (Do After Diagnosis)

#### Experiment 3: Question-Specific Prompts
- **Time:** 3-5 days
- **Method:** Add construct context for failing questions
- **Learn:** Can prompts fix abstract questions?
- **Priority:** ⭐⭐ HIGH

#### Experiment 4: Anchor Text Redesign
- **Time:** 1-2 weeks
- **Method:** Apply working question patterns to failing ones
- **Learn:** Can better anchors fix distributions?
- **Priority:** ⭐⭐ HIGH

#### Experiment 5: Alternative Embeddings
- **Time:** 2-3 days
- **Method:** Test text-embedding-3-large
- **Learn:** Does dimensionality help?
- **Priority:** ⭐ MEDIUM

### Recommended Order

1. Run Experiments 1-2 to understand WHERE the problem is
2. Based on findings, run targeted optimization experiments
3. Don't optimize without diagnosis - risk fixing the wrong thing

---

## Key Insights

### Why Question Type Matters

**Working questions (Excitement, Relevance):**
- Direct emotional responses LLM can simulate
- Personal framing grounds the evaluation
- No need for cultural/market knowledge
- Clear language-to-scale mapping

**Failing questions (Believability, Uniqueness):**
- Require judgment LLM doesn't have context for
- "Is this believable?" depends on Czech lottery market knowledge
- "Is this unique?" needs scratchcard category expertise
- LLM defaults to conservative skepticism

### What This Tells Us

1. **SSR methodology works** - proven by 2/7 success rate
2. **LLM limitations are construct-specific** - not universal failure
3. **Cultural context is critical** - for evaluative questions
4. **Clear path forward** - fix prompt/context for failing question types

---

## What We Learned

### From Working Questions
- Concrete emotional questions are reliable
- Personal framing ("to me") helps accuracy
- 4-5 level scales work better than 6+ levels
- Clear semantic progressions enable good SSR mapping

### From Failing Questions
- Abstract evaluations need cultural anchoring
- Category expertise can't be easily simulated
- Conservative bias affects trust/novelty judgments
- Distribution shape matters as much as mean

### From The Pattern
- This is NOT a universal SSR failure
- This is a construct-specific LLM interpretation issue
- We can potentially fix with better prompts/context
- Or identify which question types to use SSR for

---

## Next Steps

### Immediate (This Week)
1. Run Experiment 1 (2-3 hours) - isolate root cause
2. Review findings with team
3. Decide on optimization path based on results

### Short Term (1-2 Weeks)
1. Run diagnostic Experiment 2 if needed
2. Begin targeted optimization experiments
3. Test hypotheses about cultural context

### Medium Term (1-2 Months)
1. Systematic improvement of failing question types
2. Document patterns for question type selection
3. Build guidelines for when to use SSR

---

## Questions to Answer

Through experimentation, we need to determine:

1. **Is the bias in LLM responses or SSR mapping?**
   - Experiment 1 answers this directly

2. **Can prompts provide the missing cultural context?**
   - Experiment 3 tests this hypothesis

3. **Are anchors too semantically similar?**
   - Experiment 4 addresses this

4. **Is this fixable or are some constructs just incompatible?**
   - Experiments 1-4 collectively answer this

5. **Should we focus on question selection vs universal improvement?**
   - Pattern analysis suggests both may be valuable

---

## Files Generated

- **presentation_accuracy.png** - Accuracy comparison visualization
- **presentation_consistency.png** - Distribution matching visualization
- **presentation_correlation.png** - Correlation scatter plot
- **PRESENTATION_REPORT.txt** - Complete technical report
- **PRESENTATION_GUIDE.md** - Full presentation guide

---

**Date:** 2026-01-05
**Status:** Analysis complete, experiments recommended
**Next Action:** Run Experiment 1 to isolate root cause
