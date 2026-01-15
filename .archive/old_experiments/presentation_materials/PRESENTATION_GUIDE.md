# Presentation Guide: Synthetic Survey Analysis Results

## Overview

This presentation shows the **results of testing the synthetic survey system** against real consumer data, identifying what works, what doesn't, and recommending next experiments.

## Generated Files

### 1. **presentation_accuracy.png**
Shows accuracy comparison between synthetic and ground truth

**What it shows:**
- Left panel: Ground truth vs synthetic means side-by-side
- Right panel: Bias visualization (how much synthetic deviates)
- Color coding: Darker colors = acceptable performance

**Key finding:** 2/7 questions show acceptable accuracy (<15% bias)

### 2. **presentation_consistency.png**
Shows distribution matching (KL divergence)

**What it shows:**
- KL divergence for each question
- Green line at 0.20 = acceptable threshold
- Red/orange bars = failing questions

**Key finding:** 3/7 questions match distributions well (KL < 0.20)

### 3. **presentation_correlation.png**
Scatter plot showing correlation

**What it shows:**
- Each point = one question
- Distance from diagonal line = error
- Overall correlation: 41.4% (target: >85%)

### 4. **PRESENTATION_REPORT.txt**
Complete technical report with all statistics and experiment recommendations

---

## Key Messages for Your Presentation

### Main Finding: Performance Varies by Question Type

```
✓ WORKS (2/7): Excitement, Relevance
⚠ PARTIAL (1/7): Purchase Intent
✗ FAILS (4/7): Believability, Uniqueness, Likeability, Value
```

### The Pattern We Discovered

**SSR works well for:**
- Concrete behavioral questions (excitement, relevance)
- Emotional/feeling-based responses
- Personal fit assessments ("relevant to me")
- Questions with clear semantic progressions

**SSR struggles with:**
- Abstract evaluative judgments (believability, uniqueness)
- Questions requiring cultural/market context
- Category expertise-dependent assessments
- Multi-level scales with subtle distinctions

### Key Insight

> The systematic conservative bias is NOT universal - it's construct-specific. This suggests the issue is in how the LLM interprets different question types, not the SSR methodology itself.

---

## Results Summary

### What Works ✓

| Question | Accuracy | Consistency | Why It Works |
|----------|----------|-------------|--------------|
| **EXCITMENT** | -13% bias | KL=0.11 | Direct emotional response, 4-level scale |
| **RELVANCE** | +11% bias | KL=0.08 | Personal fit ("to me"), clear progression |

**Characteristics:**
- Both are concrete, emotional questions
- Simple semantic progressions
- No cultural ambiguity
- Personal framing

### What Partially Works ⚠

| Question | Accuracy | Consistency | Issue |
|----------|----------|-------------|-------|
| **PRPURINT** | +16% bias | KL=0.18 | Good distribution, but overestimates intent |

**Characteristics:**
- Behavioral intent (concrete)
- But has positive bias (overestimates by 16%)

### What Doesn't Work ✗

| Question | Accuracy | Consistency | Why It Fails |
|----------|----------|-------------|--------------|
| **BELVBLTY** | -26% bias | KL=0.52 | Requires trust judgment, cultural context |
| **UNIQNESS** | -33% bias | KL=0.47 | Needs category expertise, wrong reference frame |
| **LIKBILTY** | -16% bias | KL=0.32 | Abstract preference, 6-level scale |
| **PRVALMNY** | -16% bias | KL=0.24 | Value judgment, market knowledge needed |

**Characteristics:**
- All are abstract evaluative judgments
- Require cultural/market context
- LLM shows systematic conservative bias
- Poor distribution matching

---

## Performance Metrics

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| Correlation Attainment | 41.4% | >85% | -43.6pp |
| Mean KL Divergence | 0.275 | <0.20 | +38% |
| Questions Passing Accuracy | 2/7 | 7/7 | -5 |
| Questions Passing Consistency | 3/7 | 7/7 | -4 |

---

## Recommended Next Experiments

### Diagnostic Experiments (Do First)

**EXPERIMENT 1: Isolate Response Generation vs SSR Mapping**
- **Time:** 2-3 hours
- **Method:** Have LLM output 1-5 ratings directly (skip SSR)
- **What we'll learn:** Whether bias is in LLM responses or SSR mapping
- **Priority:** HIGH - This tells us where to focus effort

**EXPERIMENT 2: Analyze Free-Text Responses**
- **Time:** 1 day
- **Method:** Save and review LLM responses before SSR conversion
- **What we'll learn:** If responses are genuinely conservative or mapping fails
- **Priority:** HIGH - Diagnostic

### Optimization Experiments (Do After)

**EXPERIMENT 3: Question-Specific Prompt Engineering**
- **Time:** 3-5 days
- **Method:** Add construct-specific context for failing questions
- **What we'll learn:** If targeted prompts fix the bias
- **Priority:** MEDIUM - After we understand root cause

**EXPERIMENT 4: Anchor Text Systematic Redesign**
- **Time:** 1-2 weeks
- **Method:** Apply successful patterns from working questions to failing ones
- **What we'll learn:** If better anchors fix distribution mismatch
- **Priority:** MEDIUM - If Exp 1 shows SSR is the issue

**EXPERIMENT 5: Alternative Embedding Models**
- **Time:** 2-3 days
- **Method:** Test text-embedding-3-large (3072-dim vs current 1536-dim)
- **What we'll learn:** If higher-dimensional embeddings improve semantic matching
- **Priority:** LOW - Minor optimization

### Recommended Order

1. Start with **Experiments 1-2** (diagnostic) to understand WHERE the problem is
2. Then run **Experiments 3-5** (optimization) targeting the identified root cause
3. This prevents wasting time optimizing the wrong component

---

## Presentation Flow Suggestion

### Slide 1: Testing Results Overview
- "We tested the synthetic survey system against real Czech consumer data"
- "Mixed results: 2 questions work, 4 don't, 1 partial"
- Show **presentation_accuracy.png**

### Slide 2: What Works
- "Excitement and Relevance questions show acceptable performance"
- Key stats:
  - Excitement: 13% bias, KL=0.11
  - Relevance: 11% bias, KL=0.08
- "These are concrete, emotional, personal fit questions"

### Slide 3: What Doesn't Work
- "4 questions show systematic conservative bias (16-33%)"
- Show **presentation_accuracy.png** (bias panel)
- Key stats:
  - Believability: -26%
  - Uniqueness: -33%
  - Likeability, Value: -16%

### Slide 4: The Pattern
- "Performance varies by question type"
- Show comparison table:
  - Works: Concrete, emotional, personal
  - Fails: Abstract, evaluative, cultural
- **Key insight:** "Bias is construct-specific, not universal"

### Slide 5: Distribution Analysis
- Show **presentation_consistency.png**
- "3/7 questions match distributions, 4 don't"
- "Failing questions have wrong distribution shape, not just wrong mean"

### Slide 6: Recommended Experiments
- List 5 experiments
- Highlight diagnostic experiments (1-2) as priority
- Timeline: 2-3 hours for first diagnostic test
- "Let's understand the root cause before optimizing"

---

## Q&A Preparation

**Q: Can we use this system for anything?**
A: Not for production use yet. The 2 working questions show promise but we need to understand why they work before expanding. This is experimental data to guide next steps.

**Q: What's causing the conservative bias?**
A: We don't know yet - that's what Experiment 1 will tell us. It could be the LLM generating conservative responses, or the SSR mapping being too strict. We need to isolate which component is the issue.

**Q: Why does it work for some questions but not others?**
A: Concrete emotional questions (Excitement) work, abstract evaluative questions (Believability) don't. This suggests the LLM struggles to simulate cultural context and category expertise, but can handle emotional responses well.

**Q: How long to fix this?**
A: Unknown until we run the diagnostic experiments. If it's prompt engineering, could be 1-2 weeks. If it's fundamental to the SSR approach, might need alternative methods. Experiments 1-2 will tell us.

**Q: Should we continue with this approach?**
A: Yes - 2/7 questions working proves the concept can work. The construct-specific pattern gives us clear direction for experiments. This is valuable data to improve the system.

**Q: What about the research paper that got 90% correlation?**
A: They used extensive manual optimization across 57 surveys and may have had less culturally-specific questions. Our failing questions (Believability, Uniqueness) may be more context-dependent than theirs. This is a hypothesis to test.

**Q: What's the immediate next step?**
A: Run Experiment 1 (2-3 hours) - have LLM output ratings directly to see if bias persists. This will immediately tell us if we should focus on prompt engineering or anchor optimization.

---

## Key Statistics to Reference

- **Overall:** 41.4% correlation vs 85% target
- **Best performer:** Relevance (KL=0.08, 11% bias)
- **Worst performer:** Uniqueness (KL=0.47, -33% bias)
- **Working questions:** 2/7 (29%)
- **Average bias:** -10.8% (conservative)

---

## What NOT to Say

❌ "The system works" - too positive, not accurate
❌ "The system is ready for deployment" - definitely not
❌ "We should abandon this approach" - too negative, we have learnings
❌ "We need 6-12 months to fix it" - don't know timeline yet

## What TO Say

✓ "We have mixed results with clear patterns"
✓ "Some question types work, others don't - this tells us something"
✓ "We've identified the issue is construct-specific, not universal"
✓ "We have a clear experimental roadmap to understand root causes"
✓ "2-3 hours of testing will tell us where to focus efforts"

---

## Files Reference

All supporting documentation available:
- `ANALYSIS_FINDINGS.md` - Detailed systematic bias analysis
- `SSR_MANAGEMENT_REPORT.md` - Comprehensive methodology review
- `EXPERIMENT_LOG.md` - Previous experiments tried
- `data/validation/validation_metrics.csv` - Raw metrics

---

**Created:** 2026-01-05
**Purpose:** Present testing results and experimental recommendations
**Audience:** Research team and stakeholders
**Tone:** Factual, analytical, forward-looking
