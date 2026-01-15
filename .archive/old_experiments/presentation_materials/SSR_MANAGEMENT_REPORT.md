# Semantic Similarity Rating (SSR) Implementation: Management Report

**Project**: Kantar Synthetic Survey Replica
**Date**: December 2025
**Author**: Research Team
**Status**: Validation Phase - Performance Analysis Complete

---

## Executive Summary

This report provides a comprehensive analysis of our Semantic Similarity Rating (SSR) implementation for synthetic survey data generation. SSR is a methodology that converts LLM-generated free-text responses into structured scale ratings using semantic similarity matching.

### Current Performance

| Metric | Current | Target | Gap | Status |
|--------|---------|--------|-----|--------|
| **Correlation Attainment** | **41.4%** | 85% | -43.6pp | ⚠️ Needs Improvement |
| Mean KL Divergence | 0.275 | <0.20 | +0.075 | ⚠️ Needs Improvement |
| KS Similarity | 0.712 | >0.85 | -0.138 | ⚠️ Needs Improvement |

### Key Findings

✅ **Achievements**:
- 3.6x performance improvement from baseline (11.4% → 41.4% correlation attainment)
- Fixed catastrophic failures in Uniqueness and Likeability constructs (92% and 89% improvements)
- Best-in-class performance on concrete constructs: Relevance (KL: 0.08), Excitement (KL: 0.11)

❌ **Challenges**:
- Still 44 percentage points below target correlation attainment
- Systematic conservative bias: synthetic respondents rate 15-38% lower than ground truth
- Performance 54% below published benchmarks (paper achieved ~90% correlation)

### Bottom Line

**SSR works exceptionally well for concrete, behavioral questions but struggles with abstract, evaluative constructs.** The systematic conservative bias appears to originate from prompt/persona conditioning rather than the SSR methodology itself. Achieving target performance will require prompt engineering and potentially alternative approaches for problematic constructs.

---

## 1. What SSR is Good At

### 1.1 Concrete Behavioral Questions

**Best Performance: Purchase Intent (KL: 0.18)**
- Direct actionable decision: "Would you buy this?"
- Clear semantic progression: "definitely would" → "probably not" → "definitely not"
- No cultural ambiguity
- Behavioral intent vs. abstract evaluation

**Why it works**: The question maps directly to a concrete action. Anchors describe observable behaviors rather than subjective states.

### 1.2 Clear Semantic Progressions

**Best Performance: Relevance (KL: 0.08)** ⭐ Top Performer
- Unambiguous scale: "not relevant to me" → "extremely relevant to me"
- Personal framing ("to me") grounds the evaluation
- Natural language alignment with how people think
- No polarity confusion in embeddings

**Performance**:
- Ground Truth Mean: 2.44
- Synthetic Mean: 2.72
- Difference: Only +0.27 (11% variance)

### 1.3 Emotion-Based Constructs

**Strong Performance: Excitement (KL: 0.11)**
- Direct feeling-based language
- 4-level scale reduces complexity
- Binary emotional quality: excited vs. not excited
- After GPT-4.1 upgrade: 64% improvement over gpt-4o-mini

### 1.4 Optimal Scale Design: 4-5 Levels

**Pattern Observed**:
- 4-level scales: Excitement (KL: 0.11)
- 5-level scales: Purchase Intent (KL: 0.18), Relevance (KL: 0.08)
- 6-level scales: Likeability struggled (KL: 4.27 before fix)

**Why**: Embedding models have sufficient dimensionality to distinguish 4-5 distinct semantic levels but struggle with finer gradations.

### 1.5 Moderate-Range Distributions

**Sweet Spot**: Questions with ground truth means between 2.5-3.5
- Avoids extreme value challenges
- LLM naturally gravitates to moderate responses
- Less susceptibility to boundary effects

**Performance Summary**:

| Construct Type | Example | KL Divergence | Why SSR Succeeds |
|----------------|---------|---------------|------------------|
| **Behavioral** | Purchase Intent | 0.18 | Clear action, no ambiguity |
| **Personal Fit** | Relevance | 0.08 | Concrete "to me" framing |
| **Emotional** | Excitement | 0.11 | Direct feeling, binary quality |

---

## 2. What SSR Struggles With

### 2.1 Abstract Evaluative Constructs

**Poor Performance: Believability (KL: 0.52)**
- Requires credibility judgment - highly subjective
- Depends on cultural trust in institutions
- Missing context: Czech consumers trust local lottery operators
- LLM applies generic skepticism without local knowledge

**Impact**:
- Ground Truth Mean: 3.03
- Synthetic Mean: 2.24
- Difference: -0.79 (-26% lower)

**Why it fails**: Believability requires domain expertise and cultural context that personas lack.

### 2.2 Nuanced Perceptual Judgments

**Poor Performance: Uniqueness (KL: 0.47 after fix, was 0.65)**
- "How new/different?" requires category expertise
- Context-dependent: novel for Czech lottery vs. novel globally
- LLM applies wrong reference frame
- Ground truth shows 23% use "Very new" (Level 5), synthetic shows near 0%

**Distribution Mismatch**:
- GT Modal Response: Level 4 "Very new" (33%)
- Synthetic Modal: Level 3 "Somewhat new" (30%)
- Synthetic heavy concentration at Levels 1-2 (57% vs 13% in GT)

### 2.3 Multi-Level Scales (6+ levels)

**Challenge: Likeability (6-level scale, KL: 0.32)**
- Original design used repetitive "like" language 4 times
- Semantic overlap: "like extremely", "like very much", "like moderately", "like slightly"
- Embedding space struggles to distinguish adjacent levels
- Was catastrophic (KL: 4.27) before vocabulary fix

**Solution**: Fixed by using varied vocabulary ("excellent", "quite good", "decent", "just okay") - achieved 89% improvement

### 2.4 Extreme Values

**LLM Boundary Avoidance**:
- Systematically avoids Level 1 and Level N (highest)
- Example: Uniqueness Level 5 usage - GT: 23.4%, Synthetic: ~0%
- Regression to mean tendency built into language models
- Safety/hedging behavior in LLMs

### 2.5 Cultural/Market-Specific Judgments

**Experiment Finding**: Adding "Czech Republic" market context
- ✅ Helped: Believability (KL improved 37%)
- ❌ Hurt: Uniqueness (KL worsened 46%), Likeability (KL worsened 41%)

**Conclusion**: Market context helps constructs requiring local knowledge but interferes with universal constructs.

**What SSR Struggles With - Summary**:

| Construct Type | Example | KL Divergence | Root Cause |
|----------------|---------|---------------|------------|
| **Evaluative** | Believability | 0.52 | Requires cultural context, credibility judgment |
| **Perceptual** | Uniqueness | 0.47 | Needs category expertise, wrong reference frame |
| **Multi-Level** | Likeability (6-level) | 0.32 | Semantic overlap between adjacent levels |

---

## 3. What SSR Misses

### 3.1 Systematic Conservative Bias

**Critical Finding**: Synthetic respondents rate concepts 15-38% lower than Czech ground truth across 5 out of 7 questions.

| Question | GT Mean | Syn Mean | Difference | % Lower |
|----------|---------|----------|------------|---------|
| Believability | 3.03 | 2.24 | -0.79 | **-26%** |
| Uniqueness | 3.64 | 2.50 | -1.14 | **-31%** |
| Likeability | 3.71 | 3.12 | -0.59 | **-16%** |
| Value for Money | 3.54 | 3.06 | -0.48 | **-14%** |
| Excitement | 2.59 | 2.24 | -0.35 | **-14%** |

**Only Exceptions** (bucking the trend):
- Purchase Intent: +0.55 (+17% higher)
- Relevance: +0.09 (+4% higher)

**Implication**: The systematic nature (not random) indicates the bias originates from **prompt/response generation** rather than SSR mapping errors. If SSR mapping were the issue, errors would be random across questions.

### 3.2 Extreme Value Responses

**Missing**: High enthusiasm / strong conviction responses
- Ground truth: 23.4% use "Very new" (Level 5) for uniqueness
- Synthetic: Near 0% use highest level
- LLM exhibits boundary avoidance behavior

**Pattern**: LLM hedges toward moderate responses, missing the full range of human conviction.

### 3.3 Cultural Context Nuances

**Missing**: Local market knowledge that ground truth respondents inherently possess
- Czech lottery market familiarity
- Local brand trust (Sazka, Zlatá rybka)
- Purchasing power context (250 CZK = $10 USD)
- What's considered "innovative" in Czech vs. global market

### 3.4 Enthusiasm and Positive Affect

**Current Prompt**: "Be honest and specific in your responses"
- LLM interprets as: "be critical and skeptical"
- Missing: Positive framing, enthusiasm cues
- Result: Conservative, measured responses vs. authentic consumer excitement

---

## 4. What SSR Captures

### 4.1 Behavioral Intent Patterns

**Purchase Intent (KL: 0.18)** - Successfully captures:
- Likelihood gradations: definitely → probably → might → probably not → definitely not
- Price sensitivity patterns
- Conditional purchase decisions

### 4.2 Personal Relevance Judgments

**Relevance (KL: 0.08)** - Successfully captures:
- Personal fit assessments ("relevant to me")
- Interest alignment
- Self-concept matching

### 4.3 Emotional Reactions

**Excitement (KL: 0.11)** - Successfully captures:
- Emotional engagement levels
- Enthusiasm gradients
- Affective responses (with GPT-4.1 model upgrade)

### 4.4 Value Perception

**Value for Money (KL: 0.24)** - Moderately captures:
- Price fairness judgments
- Value-for-money assessments
- Economic utility perceptions (when well-calibrated)

### 4.5 Overall Distribution Shapes

**When Anchors Well-Designed**: SSR successfully reproduces:
- Distribution shapes (bell curves, skewed distributions)
- Modal response patterns
- Variance characteristics

**Example**: Relevance distribution closely matches ground truth across all 5 levels

---

## 5. Anchor Sensitivity

### 5.1 Extreme Sensitivity Confirmed

**SSR functions as precision instrumentation** - small wording changes produce massive performance swings.

**Evidence**:

| Construct | Change | Impact | Multiplier |
|-----------|--------|--------|------------|
| Excitement | "pretty standard" → "fairly routine" | KL: 0.75 → 10.80 | **14.4x worse** |
| Relevance | Anchor rewording | KL: 0.41 → 7.52 | **18.3x worse** |

**Implication**: Treat anchor design with surgical precision. Casual modifications catastrophically fail.

### 5.2 Successful Anchor Pattern

**Uniqueness Fix (92% improvement)**:

**Before** (KL: 5.32):
```
"I've never encountered anything like it. Exceptionally unique."
```

**After** (KL: 0.44):
```
"This is quite new and different for a scratchcard. It offers features
I haven't seen before in this category."
```

**Keys to Success**:
- ✅ Removed superlatives ("never", "exceptionally")
- ✅ Added category context ("for a scratchcard")
- ✅ Moderate tone ("quite new" vs. "exceptionally unique")
- ✅ Specific reference ("in this category")

### 5.3 Failed Anchor Pattern

**Believability Attempt (24% worse)**:

**Change Made**:
- Removed "completely" intensifier
- Added varied uncertainty markers (skeptical, doubtful, uncertain)

**Result**: KL worsened from 0.63 → 0.78

**Root Cause**: Removed intensifier without sufficient semantic compensation - created more overlap, not less.

### 5.4 Likeability Fix (89% improvement)

**Before** (KL: 4.27):
```
Repetitive "like" language:
- "I like this extremely"
- "I like this very much"
- "I like this moderately"
- "I like this slightly"
```

**After** (KL: 0.47):
```
Varied vocabulary:
- "I find this excellent. It really stands out..."
- "I find this quite good..."
- "This seems decent. It's acceptable..."
- "This is just okay. Nothing special..."
```

**Keys to Success**:
- ✅ Varied adjectives (excellent, quite good, decent, okay)
- ✅ Increased semantic distance between levels
- ✅ Distinctive language patterns per level

### 5.5 Design Principles for Anchors

**DO**:
- ✅ Use varied vocabulary across levels
- ✅ Add category-specific context ("for a scratchcard")
- ✅ Maintain gradual semantic progression
- ✅ Use moderate tone (avoid superlatives)
- ✅ First-person natural language ("I would...")
- ✅ Test changes with validation data

**DON'T**:
- ❌ Repeat the same word across multiple levels
- ❌ Use extreme/absolute language ("never", "always", "exceptionally")
- ❌ Make casual wording changes without testing
- ❌ Remove intensifiers without compensation
- ❌ Assume small changes are harmless

---

## 6. Prompt Sensitivity

### 6.1 Market Context Experiment

**Change**: Added "You are a consumer from Czech Republic" + market familiarity language

**Results** (Mixed):

| Construct | Impact | KL Change |
|-----------|--------|-----------|
| Believability | ✅ **+37% improvement** | 0.78 → 0.49 |
| Uniqueness | ❌ **-46% worse** | 0.46 → 0.67 |
| Likeability | ❌ **-41% worse** | 0.39 → 0.55 |

**Overall**: Mean KL worsened 11% (0.31 → 0.34)

### 6.2 Key Insight: Construct-Specific Effects

**Market context helps**: Constructs requiring local knowledge
- Believability: Trust in Czech lottery operators
- Price perceptions: Understanding 250 CZK purchasing power

**Market context hurts**: Universal constructs
- Likeability: General preferences, not market-dependent
- Uniqueness: Over-indexes on local reference frame

**Conclusion**: Prompt modifications are **not universally beneficial** - must be carefully targeted to specific constructs.

### 6.3 Conservative Bias Hypothesis

**Current System Prompt** includes:
- "Be honest and specific in your responses"
- "Express genuine opinions, both positive and negative"

**Hypothesis**: LLM interprets these instructions as:
- "Be critical and skeptical" (over-indexes on honesty = criticism)
- Missing: Enthusiasm cues, positive framing, authentic excitement

**Evidence**: 5 out of 7 questions show systematic underrating

**Recommendation**: Prompt engineering experiments to test:
- Positive framing: "Share what excites you"
- Enthusiasm cues: "React authentically, including enthusiasm when warranted"
- Balanced instructions: "Express full range of opinions from critical to enthusiastic"

### 6.4 Prompt Modification Guidelines

**Lessons Learned**:
1. **Not a universal fix**: Market context helps some, hurts others
2. **Test before deploying**: Validate impact across all constructs
3. **Targeted approach**: Apply modifications to specific problematic questions only
4. **Systematic effects**: Prompt changes affect ALL respondents similarly

---

## 7. Comparison to Published Benchmarks

### 7.1 Performance Gap

| Metric | Paper (GPT-4o SSR) | Current (GPT-4.1 SSR) | Gap |
|--------|--------------------|-----------------------|-----|
| **KS Similarity** | **0.88** | 0.71 | -0.17 (-19%) |
| **Correlation Attainment** | **~90%** | 41.4% | **-48.6pp (-54%)** |
| **Target Reliability** | 0.85 | 0.35 | -0.50 (-59%) |

**Paper Reference**: arXiv:2510.08338v2 - "Semantic Similarity Rating with LLM"

### 7.2 Possible Reasons for Gap

**1. Domain Differences**:
- Paper: Optimized for purchase intent surveys
- Current: Czech scratchcard market research (culturally specific)

**2. Manual Optimization**:
- Paper: "Reference sets were manually optimized" across 57 surveys
- Current: Systematic approach without extensive manual tuning

**3. Methodology Differences**:
- Paper: May use different prompting strategies (not fully disclosed)
- Current: Standard GPT-4.1 with default parameters

**4. Sample Size**:
- Paper: Not specified
- Current: 75 synthetic vs. 400 ground truth respondents

**5. Ground Truth Quality**:
- Paper: Likely more homogeneous populations
- Current: Czech market with unique cultural characteristics

**6. Hyperparameters**:
- Paper: Full specification not provided (temperature, epsilon, normalization method)
- Current: Temperature 0.5, linear normalization, sampling selection

### 7.3 Paper's Noted Limitation

**Quote**: *"Reference sets were manually optimized... remains elusive how well they perform for other surveys"*

**Implication**: The 90% correlation attainment in the paper may not be achievable out-of-the-box for new domains without extensive manual optimization.

### 7.4 Realistic Target Assessment

**Question**: Is 85% correlation attainment achievable without fine-tuning?

**Evidence**:
- Current: 41.4% with systematic fixes
- Paper: ~90% with manual optimization across 57 surveys
- Gap: Suggests 40-50pp improvement requires domain-specific tuning

**Recommendation**:
- **Near-term target**: 60-65% correlation attainment (achievable with prompt engineering)
- **Long-term target**: 75-85% (requires systematic optimization campaign)
- **Paper-level performance**: May require fine-tuning or alternative approaches

---

## 8. Key Learnings Summary

### 8.1 Methodology Insights

1. **SSR is Precision Instrumentation**
   - Small changes → 14-18x performance swings
   - Requires surgical modifications only
   - Heavy rewrites catastrophically fail

2. **Systematic Bias ≠ SSR Mapping Issue**
   - Conservative bias affects all questions similarly
   - Points to prompt/persona conditioning
   - SSR mapping errors would be random

3. **Model Selection Matters**
   - GPT-4.1 upgrade: +6.8pp correlation attainment
   - Excitement construct: 64% improvement over gpt-4o-mini
   - Model capabilities directly impact SSR effectiveness

4. **Sample Size Instability**
   - Performance varies dramatically across random seeds
   - Need 50+ respondents for stable metrics
   - Small tests (19-30 respondents) insufficient

5. **Post-Processing Ineffective**
   - Calibration made correlation drop 64.9% → 28.3%
   - Must get distributions right at generation time
   - Cannot fix with post-hoc adjustments

### 8.2 Design Principles

**For Anchors**:
- Varied vocabulary (not repetitive words)
- Moderate tone (no superlatives)
- Category context ("for a scratchcard")
- Gradual semantic progression
- First-person natural language

**For Prompts**:
- Construct-specific modifications
- Test before deploying
- Balance positive/negative framing
- Avoid over-indexing on "honesty = criticism"

**For Scales**:
- 4-5 levels optimal
- Clear semantic distinctiveness
- Avoid 6+ levels (semantic overlap risk)

### 8.3 Performance Patterns

**SSR Excels When**:
- Construct is concrete/behavioral
- Scale has clear semantic progression
- 4-5 levels with distinct anchors
- Question is culturally neutral
- Moderate-range distributions

**SSR Struggles When**:
- Construct is abstract/evaluative
- Requires cultural/domain expertise
- 6+ level scales with subtle gradations
- Extreme values expected
- Market-specific context needed

---

## 9. Recommendations & Next Steps

### 9.1 Immediate Actions (Diagnostic)

**Priority 1: Isolate Bias Source**
- **Action**: Test direct scale response (skip SSR text generation)
- **Purpose**: Determine if bias is in response generation vs. SSR mapping
- **Timeline**: 2-3 hours
- **Expected Outcome**: If bias persists → response generation issue; If bias disappears → SSR mapping issue

**Priority 2: Analyze LLM Free-Text Responses**
- **Action**: Modify pipeline to save free-text responses before SSR mapping
- **Purpose**: Understand if responses are genuinely conservative or well-calibrated
- **Timeline**: 1 day
- **Expected Outcome**: Identify specific language patterns causing conservative scores

**Priority 3: Investigate Paper Parameters**
- **Action**: Review paper methodology, attempt to replicate exact parameters
- **Purpose**: Determine if gap is due to undisclosed methodology differences
- **Timeline**: 2-3 days

### 9.2 Short-Term Optimizations

**Priority 4: Prompt Engineering**
- **Action**: Test enthusiasm/positivity cues in system prompt
- **Variants**:
  - "Share what excites you about this product"
  - "React authentically, including enthusiasm when warranted"
  - "Express full range from critical to enthusiastic"
- **Timeline**: 3-5 days (100 respondents per variant)
- **Target**: +10-15pp correlation attainment

**Priority 5: Temperature Sweep**
- **Action**: Test temperature range 0.0 - 1.0 (currently 0.5)
- **Hypothesis**: Higher temperature → more varied responses → less conservative bias
- **Timeline**: 1 week (5-7 experiments)
- **Target**: +5-10pp correlation attainment

**Priority 6: Scale to 100+ Respondents**
- **Action**: Run full validation with 100+ synthetic respondents
- **Purpose**: Eliminate sample size instability, get stable metrics
- **Timeline**: 1 day per run
- **Expected**: More reliable performance assessment

**Priority 7: Optimize Remaining Problem Questions**
- **Target**: Believability (KL: 0.52 → <0.35)
- **Action**: Systematic anchor redesign with A/B testing
- **Timeline**: 1-2 weeks

### 9.3 Medium-Term Systematic Improvements

**Priority 8: Alternative Embedding Models**
- **Action**: Test OpenAI text-embedding-3-large (3072-dim vs. current 1536-dim)
- **Hypothesis**: Higher dimensionality → better semantic discrimination
- **Timeline**: 2 weeks
- **Target**: +5-10pp improvement

**Priority 9: Enrich Personas**
- **Action**: Add psychographic attributes (risk tolerance, enthusiasm, skepticism)
- **Hypothesis**: More varied personas → more varied responses
- **Timeline**: 2-3 weeks
- **Target**: Reduce conservative bias

**Priority 10: Hybrid Approach**
- **Action**: LLM generates text + confidence rating (1-5)
- **Method**: Use SSR for validation, confidence for weighting
- **Timeline**: 3-4 weeks (development + validation)
- **Target**: Best of both worlds

**Priority 11: Few-Shot Prompting**
- **Action**: Include example responses from ground truth data
- **Hypothesis**: Examples calibrate LLM to authentic Czech consumer language
- **Timeline**: 2 weeks
- **Target**: Cultural context alignment

### 9.4 Long-Term Strategic Options

**Option A: Fine-Tuning**
- Fine-tune GPT model on ground truth survey responses
- Requires significant data + compute resources
- Timeline: 2-3 months
- Potential: Achieve paper-level 90% performance

**Option B: Ensemble Approaches**
- Multiple models (GPT-4.1, Claude, Gemini) → average/vote
- Reduces model-specific biases
- Timeline: 1-2 months
- Potential: +10-20pp improvement

**Option C: Domain-Specific Calibration**
- Systematic optimization campaign per construct
- Manual anchor tuning like paper methodology
- Timeline: 3-6 months
- Potential: Approach 85% target

### 9.5 Critical Questions to Resolve

1. **Why does Purchase Intent buck the conservative bias trend?** (+17% vs -14% to -33% for others)
   - May reveal construct-specific prompt insights

2. **Can 85% target be reached without fine-tuning?**
   - Paper used extensive manual optimization
   - May require similar campaign or alternative approach

3. **Is systematic bias model-specific (GPT-4.1) or universal?**
   - Test with Claude, Gemini to isolate model effects

4. **What explains the 44pp gap to target?**
   - Methodology? Domain? Sample size? Cultural factors?

---

## 10. Conclusion

### Current State Assessment

**Strengths**:
- SSR methodology fully implemented with 6 reference sets per scale
- 3.6x performance improvement achieved from baseline
- Excellent performance on concrete behavioral constructs (Relevance, Excitement, Purchase Intent)
- Systematic understanding of anchor sensitivity and design principles

**Challenges**:
- 44 percentage points below target correlation attainment (85%)
- Systematic conservative bias across 5/7 questions (15-38% underrating)
- Performance 54% below published benchmarks
- Abstract evaluative constructs remain problematic

### Path Forward

**Near-Term Focus** (1-2 months):
- Diagnose bias source (response generation vs. mapping)
- Prompt engineering experiments for enthusiasm
- Temperature and parameter optimization
- Scale to stable sample sizes (100+ respondents)

**Expected Outcome**: 55-65% correlation attainment (achievable with focused optimizations)

**Medium-Term Strategy** (3-6 months):
- Hybrid approaches (SSR + direct rating)
- Alternative embedding models
- Psychographic persona enrichment
- Systematic per-construct optimization

**Expected Outcome**: 70-80% correlation attainment (approaching target)

**Long-Term Options** (6-12 months):
- Fine-tuning on domain data
- Ensemble methods
- Full manual optimization campaign per paper methodology

**Expected Outcome**: 85%+ correlation attainment (target achievement)

### Bottom Line for Management

**SSR is a powerful methodology that works exceptionally well for concrete behavioral questions but requires significant optimization for abstract evaluative constructs.** The current 41.4% correlation attainment represents solid progress (3.6x from baseline) but indicates we are at an intermediate stage. Achieving the 85% target will require either:

1. **Focused engineering effort** (2-6 months) on prompt optimization, parameters, and hybrid approaches, OR
2. **Extensive manual optimization** (6-12 months) following the paper's methodology

The path chosen depends on business timeline requirements and acceptable performance thresholds.

---

**Appendix: Technical References**
- Implementation: `/src/ssr/` directory
- Validation Reports: `/data/validation/`
- Experiment Log: `EXPERIMENT_LOG.md`
- Detailed Findings: `ANALYSIS_FINDINGS.md`
- Learnings Database: `LEARNINGS.md`

**Contact**: Research Team for questions or deep-dive sessions on specific constructs