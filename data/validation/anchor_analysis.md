# Anchor Statement Analysis for Poorly Performing Questions

## Issue Summary

The validation shows significant performance gaps between synthetic and ground truth data, particularly for:
1. **UNIQNESS** (KL Divergence: 5.20) - CRITICAL ISSUE
2. **LIKBILTY** (KL Divergence: 0.64) - Moderate issue

## 1. UNIQNESS Analysis (B3)

### The Problem
- **KL Divergence:** 5.20 (CRITICAL - should be < 0.20)
- **Mean Difference:** -1.36 (GT: 3.64, Synthetic: 2.28)
- **Distribution Mismatch:** Severe

#### Ground Truth Distribution:
- Level 1 (Not at all new): 2.8%
- Level 2 (Slightly new): 10.2%
- Level 3 (Somewhat new): 30.8%
- Level 4 (Very new): 32.9%
- Level 5 (Extremely new): 23.4%
- **Modal response: Level 4 (32.9%)**
- **Mean: 3.64** (between "Somewhat" and "Very" new)

#### Synthetic Distribution:
- Level 1: 28.1% ⚠️ (GT: 2.8%)
- Level 2: 28.7% ⚠️ (GT: 10.2%)
- Level 3: 30.4% ✓ (GT: 30.8%)
- Level 4: 12.9% ⚠️ (GT: 32.9%)
- Level 5: 0.0% ❌ (GT: 23.4%)
- **Modal response: Level 3 (30.4%)**
- **Mean: 2.28** (closer to "Slightly" new)

### Root Cause: Label Polarity Reversal

**The scale labels are REVERSED from typical Likert scales:**

```
Level 1 = "Extremely new and different" (HIGHEST positivity)
Level 2 = "Very new and different"
Level 3 = "Somewhat new and different"
Level 4 = "Slightly new and different"
Level 5 = "Not at all new and different" (LOWEST positivity)
```

**Current anchor statements in `registry.py` (lines 188-194):**
```python
anchor_texts=[
    "This is extremely new and different. I've never seen anything like this before - it's completely unique and innovative.",  # Level 1
    "This is very new and different. It's quite novel and stands out from other scratchcards I've seen.",  # Level 2
    "This is somewhat new and different. It has some unique elements but also feels somewhat familiar.",  # Level 3
    "This is only slightly new and different. Most of it feels pretty standard with just a few small novel touches.",  # Level 4
    "This is not at all new and different. It feels like the same old thing I've seen many times before."  # Level 5
]
```

**The anchors are CORRECT** - they match the label definitions.

### The Real Problem: Semantic Mismatch

The LLM appears to be interpreting the **question semantically** rather than following the **scale structure**.

When asked "How new and different is this?", the LLM naturally responds:
- "This is extremely new" → Expects to map to highest value (5)
- But the scale has: Level 1 = "Extremely new" = value 1

**The synthetic data shows:**
- Heavy concentration at levels 1-2 (56.8% combined)
- Almost no level 5 responses (0%)
- Missing the high uniqueness perception (levels 4-5 in GT = 56.3%)

**Ground truth shows:**
- People perceive these concepts as quite unique (56.3% at levels 4-5)
- Few people think they're "not new at all" (2.8% at level 1)

### Recommended Fix

**Option 1: Rewrite anchors to emphasize the reversed polarity**

```python
anchor_texts=[
    # Level 1 - MOST unique (but LOWEST numerical value in some contexts)
    "This concept strikes me as extremely new and different - I've never seen anything like this before. It's completely unique and highly innovative. If I had to rate it, this represents the HIGHEST level of uniqueness.",

    # Level 2
    "This concept is very new and different - it's quite novel and clearly stands out. It shows strong uniqueness with many innovative elements.",

    # Level 3
    "This concept is somewhat new and different - it has some unique elements but also some familiar aspects. It's moderately innovative.",

    # Level 4
    "This concept is only slightly new and different - most of it feels pretty standard with just a few small novel touches. Limited uniqueness.",

    # Level 5 - LEAST unique
    "This concept is not at all new and different - it feels like the same old thing I've seen many times before. It lacks uniqueness entirely."
]
```

**Option 2: Reverse the scale mapping (if possible)**

If the scale can be remapped, consider:
- Level 5 = "Extremely new and different" = most unique
- Level 1 = "Not at all new and different" = least unique

This would align with natural semantic interpretation.

**Option 3: Add explicit numerical guidance to anchors**

```python
anchor_texts=[
    "On a scale where 1 is the MOST unique: This is extremely new and different. I've never seen anything like this before - it's completely unique and innovative.",
    # etc.
]
```

---

## 2. LIKBILTY Analysis (B6)

### The Problem
- **KL Divergence:** 0.64 (Needs improvement - should be < 0.20)
- **Mean Difference:** -0.83 (GT: 3.71, Synthetic: 2.88)

#### Ground Truth Distribution:
- Level 1 (Like extremely): 8.6%
- Level 2 (Like very much): 11.6%
- Level 3 (Like moderately): 16.2%
- Level 4 (Like slightly): 35.0% ⭐
- Level 5 (Neither): 20.7%
- Level 6 (Do not like): 7.9%
- **Mean: 3.71**

#### Synthetic Distribution:
- Level 1: 17.5% ⚠️ (GT: 8.6%)
- Level 2: 25.1% ⚠️ (GT: 11.6%)
- Level 3: 23.4% ⚠️ (GT: 16.2%)
- Level 4: 26.3% ⚠️ (GT: 35.0%)
- Level 5: 0.6% ❌ (GT: 20.7%)
- Level 6: 7.0% ✓ (GT: 7.9%)
- **Mean: 2.88**

### Root Cause: Over-positive bias

The synthetic data shows:
- Too many "extremely" and "very much" responses (42.6% vs 20.2% in GT)
- Too few neutral responses (0.6% vs 20.7% in GT)
- The modal response should be level 4 ("Like slightly") but synthetic has it more spread

### Current Anchors (lines 500-507):

```python
anchor_texts=[
    "I like this extremely. It's absolutely fantastic and I love everything about it.",  # Level 1
    "I like this very much. It's really appealing and I'm quite positive about it.",  # Level 2
    "I like this moderately. It's pretty good overall with a fair amount of appeal.",  # Level 3
    "I like this slightly. It's okay and has some positive aspects but nothing special.",  # Level 4
    "I neither like nor dislike this. I feel completely neutral - it's just there.",  # Level 5
    "I do not like this at all. I have negative feelings about it and find it unappealing."  # Level 6
]
```

### Issue

The anchors may be **too enthusiastic** at the positive end. The LLM is generating responses that match "like extremely" and "like very much" more often than real respondents do.

### Recommended Fix

**Tone down the enthusiasm and make distinctions clearer:**

```python
anchor_texts=[
    # Level 1 - Reduce superlatives
    "I like this extremely. It's excellent and stands out as something I really enjoy.",

    # Level 2 - More measured
    "I like this very much. It's quite appealing and I have a clearly positive view of it.",

    # Level 3 - Neutral-positive
    "I like this moderately. It's decent overall - I have a positive view but it's not strong.",

    # Level 4 - Emphasize this is still slightly positive
    "I like this slightly. It's okay with some mild positive aspects, but nothing particularly stands out.",

    # Level 5 - Strengthen the neutral position
    "I neither like nor dislike this. I'm completely neutral about it - no positive or negative feelings either way.",

    # Level 6 - Keep similar
    "I do not like this at all. I have negative feelings about it and find it unappealing."
]
```

---

## 3. Best Performing Question: PRPURINT (B2)

### Success Metrics
- **KL Divergence:** 0.06 (EXCELLENT - within "Good" range)
- **Mean Difference:** +0.35 (GT: 3.21, Synthetic: 3.56)

### Current Anchors (lines 112-117):
```python
anchor_texts=[
    "I would definitely buy this scratchcard. It looks perfect for me and I'm very interested in purchasing it.",
    "I would probably buy this scratchcard. It seems appealing and I'd likely purchase it if I saw it.",
    "I might or might not buy this scratchcard. I'm unsure and would need to think about it more before deciding.",
    "I probably would not buy this scratchcard. It doesn't really appeal to me and I'd likely pass on it.",
    "I would definitely not buy this scratchcard. It doesn't interest me at all and I have no intention of purchasing it."
]
```

### Why This Works

1. **Clear progression** from definitely would → probably would → might → probably not → definitely not
2. **Balanced tone** - not overly enthusiastic or negative
3. **Natural language** that matches how people actually express purchase intent
4. **No semantic polarity issues** - the scale flows naturally from positive to negative

---

## Summary of Recommendations

### Immediate Actions Required:

1. **UNIQNESS (CRITICAL):**
   - Rewrite anchors to emphasize the reversed scale structure
   - Consider adding explicit numerical guidance
   - Test with a small sample to verify improvement

2. **LIKBILTY (Moderate):**
   - Tone down enthusiasm in positive anchors
   - Strengthen the neutral anchor (level 5)
   - Make the "slightly like" vs "moderately like" distinction clearer

3. **Validation Approach:**
   - After fixing anchors, regenerate 75-100 respondents
   - Focus validation on UNIQNESS and LIKBILTY specifically
   - Target: KL divergence < 0.20 for both questions

### Scale Design Principle

The PRPURINT success demonstrates that anchors work best when:
- Natural semantic interpretation aligns with scale direction
- Tone is measured and balanced
- Progression between levels is clear and gradual
- Language matches natural speech patterns
