# Kantar Question Type Reference & Performance Analysis

This document provides detailed definitions of each Kantar question type and summarizes system performance for each.

---

## Question Type Taxonomy

### Core Performance Metrics

These questions measure fundamental concept performance and are typically the most critical for decision-making.

#### 1. Purchase Intent (UNPURINT, PRPURINT)

**Question Code:** `(UNPURINT)` - Unpriced Purchase Intent, `(PRPURINT)` - Priced Purchase Intent

**Question Text (typical):**
- "Based on this description alone, how likely would you be to purchase [concept]?"
- "At a price of [X], how likely would you be to purchase [concept]?"

**Scale:** 5-point Likert
- 5 = Definitely would purchase
- 4 = Probably would purchase
- 3 = Might or might not purchase
- 2 = Probably would not purchase
- 1 = Definitely would not purchase

**What it Measures:**
- Core purchase likelihood
- Primary metric for concept viability
- Most directly linked to commercial success

**Business Importance:** ⭐⭐⭐⭐⭐ (Critical)
- Top-2-Box (4+5) is key metric for go/no-go decisions
- Often weighted most heavily in concept evaluation
- Price sensitivity measured via UNPURINT vs PRPURINT comparison

**System Performance:** [TBD after validation]
- Mean KL Divergence: [TBD]
- Mean KS Similarity: [TBD]
- Pass Rate: [TBD]% of questions meet targets
- Assessment: [EXCELLENT | GOOD | MODERATE | POOR]

**Known Challenges:**
- Price anchoring effects (PRPURINT may differ from UNPURINT)
- Cultural differences in purchase intent expression
- Context-dependent interpretation

---

#### 2. Uniqueness (UNIQNESS)

**Question Code:** `(UNIQNESS)`

**Question Text (typical):**
"How unique or different does this [concept] seem to you?"

**Scale:** 5-point Likert
- 5 = Extremely unique/different
- 4 = Very unique/different
- 3 = Somewhat unique/different
- 2 = Slightly unique/different
- 1 = Not at all unique/different

**What it Measures:**
- Perceived differentiation from existing offerings
- Point of difference strength
- Ability to stand out in market

**Business Importance:** ⭐⭐⭐⭐ (High)
- Key indicator of competitive advantage
- Correlates with price premium potential
- Predicts ability to attract attention

**System Performance:** [TBD after validation]
- Mean KL Divergence: [TBD]
- Mean KS Similarity: [TBD]
- Pass Rate: [TBD]%
- Assessment: [EXCELLENT | GOOD | MODERATE | POOR]

**Known Challenges:**
- Requires understanding of category context
- Can be influenced by description length/detail
- May vary by respondent category familiarity

---

#### 3. Price Perception (UNPRICEP)

**Question Code:** `(UNPRICEP)`

**Question Text (typical):**
"Compared to other similar products/services, do you think [concept] would be..."

**Scale:** 5-point scale
- 5 = Much more expensive
- 4 = Somewhat more expensive
- 3 = About the same
- 2 = Somewhat less expensive
- 1 = Much less expensive

**What it Measures:**
- Perceived value positioning
- Price expectations vs category norms
- Premium vs value positioning

**Business Importance:** ⭐⭐⭐⭐ (High)
- Critical for pricing strategy
- Indicates value perception
- Can reveal over/under-pricing risks

**System Performance:** [TBD after validation]
- Mean KL Divergence: [TBD]
- Mean KS Similarity: [TBD]
- Pass Rate: [TBD]%
- Assessment: [EXCELLENT | GOOD | MODERATE | POOR]

**Known Challenges:**
- Requires implicit category price knowledge
- May be influenced by concept features description
- Scale direction can be counterintuitive (higher = more expensive, not better)

---

#### 4. Likeability (LIKBILTY)

**Question Code:** `(LIKBILTY)`

**Question Text (typical):**
"Overall, how much do you like or dislike this [concept]?"

**Scale:** 5-point Likert
- 5 = Like it extremely
- 4 = Like it very much
- 3 = Neither like nor dislike it
- 2 = Dislike it somewhat
- 1 = Dislike it extremely

**What it Measures:**
- Emotional response to concept
- Overall appeal and attractiveness
- Gut-level reaction before deeper analysis

**Business Importance:** ⭐⭐⭐⭐ (High)
- Strong predictor of purchase intent
- Captures emotional connection
- Often correlates with word-of-mouth potential

**System Performance:** [TBD after validation]
- Mean KL Divergence: [TBD]
- Mean KS Similarity: [TBD]
- Pass Rate: [TBD]%
- Assessment: [EXCELLENT | GOOD | MODERATE | POOR]

**Known Challenges:**
- Highly subjective and persona-dependent
- May be influenced by description framing
- Can be less discriminating than other metrics (most concepts get mid-high scores)

---

### Diagnostic Metrics

These questions help understand *why* concepts perform the way they do and identify strengths/weaknesses.

#### 5. Relevance (RELVANCE)

**Question Code:** `(RELVANCE)`

**Question Text (typical):**
"How relevant is this [concept] to you personally?"

**Scale:** 5-point Likert
- 5 = Extremely relevant
- 4 = Very relevant
- 3 = Somewhat relevant
- 2 = Slightly relevant
- 1 = Not at all relevant

**What it Measures:**
- Personal applicability and need fit
- Target audience alignment
- "Is this for me?" perception

**Business Importance:** ⭐⭐⭐ (Medium-High)
- Identifies target audience mismatches
- Predicts engagement and consideration
- Helps segment responders

**System Performance:** [TBD after validation]
- Mean KL Divergence: [TBD]
- Mean KS Similarity: [TBD]
- Pass Rate: [TBD]%
- Assessment: [EXCELLENT | GOOD | MODERATE | POOR]

**Known Challenges:**
- Highly persona-dependent (demographics critical)
- May be influenced by life stage/circumstances
- Can be low even for good concepts if wrong audience

---

#### 6. Excitement (EXCITMENT)

**Question Code:** `(EXCITMENT)`

**Question Text (typical):**
"How exciting does this [concept] seem to you?"

**Scale:** 5-point Likert
- 5 = Extremely exciting
- 4 = Very exciting
- 3 = Somewhat exciting
- 2 = Slightly exciting
- 1 = Not at all exciting

**What it Measures:**
- Emotional arousal and enthusiasm
- Innovation perception
- Ability to generate buzz

**Business Importance:** ⭐⭐⭐ (Medium-High)
- Predicts trial and early adoption
- Indicates viral/word-of-mouth potential
- Correlates with launch momentum

**System Performance:** [TBD after validation]
- Mean KL Divergence: [TBD]
- Mean KS Similarity: [TBD]
- Pass Rate: [TBD]%
- Assessment: [EXCELLENT | GOOD | MODERATE | POOR]

**Known Challenges:**
- Category-dependent (some categories naturally less exciting)
- May be influenced by novelty vs practical value trade-off
- Can be high even for concepts that won't succeed

---

#### 7. Believability (BELVBLTY)

**Question Code:** `(BELVBLTY)`

**Question Text (typical):**
"How believable is this [concept]? Could it actually deliver what it promises?"

**Scale:** 5-point Likert
- 5 = Extremely believable
- 4 = Very believable
- 3 = Somewhat believable
- 2 = Slightly believable
- 1 = Not at all believable

**What it Measures:**
- Credibility and feasibility perception
- Trust in concept delivery
- "Too good to be true" detection

**Business Importance:** ⭐⭐⭐⭐ (High)
- Gate-keeper metric (low believability kills concepts)
- Predicts conversion from interest to purchase
- Identifies execution risk perception

**System Performance:** [TBD after validation]
- Mean KL Divergence: [TBD]
- Mean KS Similarity: [TBD]
- Pass Rate: [TBD]%
- Assessment: [EXCELLENT | GOOD | MODERATE | POOR]

**Known Challenges:**
- Requires category knowledge and technical understanding
- May be influenced by brand reputation (not captured in concept alone)
- Can be low for innovative concepts even if technically feasible

---

#### 8. Incrementality (INCREMNT)

**Question Code:** `(INCREMNT)`

**Question Text (typical):**
"Would this [concept] replace something you currently use, or would it be something completely new/additional?"

**Scale:** Typically categorical or 5-point scale
- Measures whether concept is incremental to category or substitutional

**What it Measures:**
- Market expansion vs cannibalization potential
- Whether concept grows category or shifts share
- New vs existing need satisfaction

**Business Importance:** ⭐⭐⭐⭐ (High)
- Critical for revenue forecasting
- Identifies cannibalization risks
- Helps size market opportunity

**System Performance:** [TBD after validation]
- Mean KL Divergence: [TBD]
- Mean KS Similarity: [TBD]
- Pass Rate: [TBD]%
- Assessment: [EXCELLENT | GOOD | MODERATE | POOR]

**Known Challenges:**
- Requires understanding of current usage patterns
- May be difficult for personas to assess without deep category knowledge
- Can be influenced by question framing

---

#### 9. Playfulness (PLAYFLNS)

**Question Code:** `(PLAYFLNS)`

**Question Text (typical):**
"How playful or fun does this [concept] seem to you?"

**Scale:** 5-point Likert
- 5 = Extremely playful/fun
- 4 = Very playful/fun
- 3 = Somewhat playful/fun
- 2 = Slightly playful/fun
- 1 = Not at all playful/fun

**What it Measures:**
- Entertainment value perception
- Emotional engagement through enjoyment
- Gamification or fun factor

**Business Importance:** ⭐⭐⭐ (Medium)
- Category-dependent (critical for gaming, less so for utilities)
- Predicts engagement and retention
- Correlates with brand affinity

**System Performance:** [TBD after validation]
- Mean KL Divergence: [TBD]
- Mean KS Similarity: [TBD]
- Pass Rate: [TBD]%
- Assessment: [EXCELLENT | GOOD | MODERATE | POOR]

**Known Challenges:**
- Not present in all studies (category-specific)
- May be influenced by cultural differences in play perception
- Can be low priority relative to functional benefits

---

### Open-Ended Questions

These questions collect free-text responses for qualitative insights.

#### 10. Likes (LIKES_STD, LIKES)

**Question Code:** `(LIKES_STD)`, `(LIKES)`

**Question Text (typical):**
"What, if anything, did you like about this [concept]?"

**Response Format:** Free text (can select from pre-coded categories or open field)

**What it Measures:**
- Positive attributes and benefits
- Key strengths and appeal factors
- What resonates with audience

**Business Importance:** ⭐⭐⭐⭐ (High)
- Identifies concept strengths for messaging
- Reveals unexpected benefits
- Provides quotable consumer language

**System Performance:** [TBD after validation]
- **Note:** Free-text responses evaluated qualitatively, not quantitatively
- Validation focuses on coded categories (if present)
- Raw text requires human review

**Known Challenges:**
- LLM-generated text may be more articulate than real responses
- May lack authentic "voice" of real consumers
- Difficult to validate statistically (qualitative nature)

---

#### 11. Dislikes (DISLIKES_STD, DISLIKES)

**Question Code:** `(DISLIKES_STD)`, `(DISLIKES)`

**Question Text (typical):**
"What, if anything, did you dislike about this [concept]?"

**Response Format:** Free text (can select from pre-coded categories or open field)

**What it Measures:**
- Negative attributes and barriers
- Key weaknesses and concerns
- What turns audience off

**Business Importance:** ⭐⭐⭐⭐⭐ (Critical)
- Identifies deal-breakers and barriers
- Reveals risks and concerns to address
- More actionable than likes (tells you what to fix)

**System Performance:** [TBD after validation]
- **Note:** Free-text responses evaluated qualitatively
- May be harder than "Likes" (requires critical thinking)
- Validation focuses on coded categories

**Known Challenges:**
- LLMs may be overly diplomatic (not critical enough)
- May miss subtle real-world concerns
- Requires persona conditioning for authentic concerns

---

### Behavioral Questions

These questions capture usage patterns, occasions, and context.

#### 12. Occasions (OCCASIONS, OCCSN)

**Question Code:** `(OCCASIONS)`, `(OCCSN)`

**Question Text (typical):**
"When or on what occasions would you use this [concept]?"

**Response Format:** Multiple choice (select all that apply) or free text

**What it Measures:**
- Usage context and situations
- Frequency implications
- Consumption patterns

**Business Importance:** ⭐⭐⭐ (Medium-High)
- Informs marketing and positioning
- Helps size opportunity (daily vs occasional)
- Identifies unexpected use cases

**System Performance:** [TBD after validation]
- Mean KL Divergence: [TBD] (if coded categories)
- Mean KS Similarity: [TBD]
- Pass Rate: [TBD]%
- Assessment: [EXCELLENT | GOOD | MODERATE | POOR]

**Known Challenges:**
- Requires imagination of future behavior
- May be influenced by description framing
- Can miss spontaneous or context-dependent usage

---

#### 13. Barriers (BARRIERS)

**Question Code:** `(BARRIERS)`

**Question Text (typical):**
"What, if anything, would prevent you from purchasing this [concept]?"

**Response Format:** Multiple choice (select all that apply) or free text

**What it Measures:**
- Purchase barriers and objections
- Risk perceptions
- Obstacles to conversion

**Business Importance:** ⭐⭐⭐⭐⭐ (Critical)
- Identifies what needs to be addressed for success
- Reveals hidden risks
- More actionable than many positive metrics

**System Performance:** [TBD after validation]
- Mean KL Divergence: [TBD]
- Mean KS Similarity: [TBD]
- Pass Rate: [TBD]%
- Assessment: [EXCELLENT | GOOD | MODERATE | POOR]

**Known Challenges:**
- May not surface unarticulated barriers
- Can be influenced by social desirability bias
- May miss financial or circumstantial barriers

---

#### 14. Gift Questions (GIFT, GIFTFOR)

**Question Code:** `(GIFT)`, `(GIFTFOR)`

**Question Text (typical):**
- "Would you consider giving this [concept] as a gift?"
- "Who would you give this to?"

**Response Format:** Yes/No or multiple choice

**What it Measures:**
- Gift-giving potential
- Extended audience beyond personal use
- Viral/word-of-mouth potential

**Business Importance:** ⭐⭐⭐ (Medium)
- Expands addressable market
- Indicates social acceptability
- Predicts certain seasonal sales patterns

**System Performance:** [TBD after validation]
- Mean KL Divergence: [TBD]
- Mean KS Similarity: [TBD]
- Pass Rate: [TBD]%
- Assessment: [EXCELLENT | GOOD | MODERATE | POOR]

**Known Challenges:**
- Category-dependent (not all products are gifts)
- May be influenced by price perception
- Cultural differences in gift-giving norms

---

## Question Type Performance Summary

### Expected Performance by Category

Based on SSR methodology and LLM capabilities, we expect:

**Strong Performance (Likely PASS):**
- ✅ Purchase Intent (UNPURINT, PRPURINT) - Clear semantic anchors, well-understood concept
- ✅ Likeability (LIKBILTY) - Direct emotional response, strong SSR mapping
- ✅ Uniqueness (UNIQNESS) - Comparative judgment, concept can assess
- ✅ Relevance (RELVANCE) - Personal fit, persona-conditioned

**Moderate Performance (Likely PASS with some variance):**
- ⚠️ Excitement (EXCITMENT) - Emotional arousal may vary by persona
- ⚠️ Believability (BELVBLTY) - Requires technical/category knowledge
- ⚠️ Price Perception (UNPRICEP) - Requires implicit price anchors

**Variable Performance (May WARN or need calibration):**
- ⚠️ Incrementality (INCREMNT) - Complex category knowledge required
- ⚠️ Playfulness (PLAYFLNS) - Subjective and category-dependent
- ⚠️ Occasions (OCCASIONS) - Requires imagination of future behavior
- ⚠️ Barriers (BARRIERS) - May miss unarticulated concerns

**Qualitative Only (Not statistically validated):**
- 📝 Likes (free-text) - Requires human review
- 📝 Dislikes (free-text) - Requires human review

---

## Actual Performance Results

**[TO BE POPULATED AFTER VALIDATION]**

### By Question Type

| Question Type | N Questions | Mean KL | Mean KS Sim | Pass Rate | Assessment |
|---------------|-------------|---------|-------------|-----------|------------|
| Purchase Intent (UNPURINT) | [TBD] | [TBD] | [TBD] | [TBD]% | [TBD] |
| Purchase Intent (PRPURINT) | [TBD] | [TBD] | [TBD] | [TBD]% | [TBD] |
| Uniqueness (UNIQNESS) | [TBD] | [TBD] | [TBD] | [TBD]% | [TBD] |
| Price Perception (UNPRICEP) | [TBD] | [TBD] | [TBD] | [TBD]% | [TBD] |
| Likeability (LIKBILTY) | [TBD] | [TBD] | [TBD] | [TBD]% | [TBD] |
| Relevance (RELVANCE) | [TBD] | [TBD] | [TBD] | [TBD]% | [TBD] |
| Excitement (EXCITMENT) | [TBD] | [TBD] | [TBD] | [TBD]% | [TBD] |
| Believability (BELVBLTY) | [TBD] | [TBD] | [TBD] | [TBD]% | [TBD] |
| Incrementality (INCREMNT) | [TBD] | [TBD] | [TBD] | [TBD]% | [TBD] |
| Playfulness (PLAYFLNS) | [TBD] | [TBD] | [TBD] | [TBD]% | [TBD] |
| Occasions | [TBD] | [TBD] | [TBD] | [TBD]% | [TBD] |
| Barriers | [TBD] | [TBD] | [TBD] | [TBD]% | [TBD] |
| Gift Questions | [TBD] | [TBD] | [TBD] | [TBD]% | [TBD] |

### Overall Findings

**Best Performing Question Types:**
1. [TBD] - [Reason]
2. [TBD] - [Reason]
3. [TBD] - [Reason]

**Question Types Needing Attention:**
1. [TBD] - [Issue identified]
2. [TBD] - [Issue identified]

**Systematic Patterns:**
- [Any patterns across question types]
- [Any systematic biases]
- [Any category-specific findings]

---

## Recommendations by Question Type

**[TO BE POPULATED AFTER VALIDATION]**

### Questions Ready for Use
[List question types that consistently PASS and can be used with confidence]

### Questions Requiring Expert Review
[List question types that WARN and need human oversight]

### Questions Needing Calibration
[List question types that FAIL and require methodology adjustment]

---

## Scale Anchor Statements

For reference, here are the anchor statements used in SSR for each scale level.

### Purchase Intent Scale Anchors

**Level 5 (Definitely would purchase):**
- "I would definitely buy this"
- "I would purchase this for sure"
- "I'm certain I would buy this product"
- "This is exactly what I've been looking for, I'd buy it immediately"
- "I would absolutely purchase this without hesitation"

**Level 4 (Probably would purchase):**
- "I would probably buy this"
- "I'm likely to purchase this"
- "There's a good chance I would buy this"
- "I would most likely purchase this product"
- "I'd be inclined to buy this"

**Level 3 (Might or might not purchase):**
- "I might buy this, I'm not sure"
- "I'm uncertain whether I would purchase this"
- "I could go either way on buying this"
- "Maybe I would purchase this, maybe not"
- "I'm on the fence about this"

**Level 2 (Probably would not purchase):**
- "I probably wouldn't buy this"
- "I'm unlikely to purchase this"
- "There's not much chance I would buy this"
- "I don't think I would purchase this"
- "I'd be hesitant to buy this"

**Level 1 (Definitely would not purchase):**
- "I definitely would not buy this"
- "I would never purchase this"
- "There's no chance I would buy this product"
- "I'm certain I would not purchase this"
- "I would absolutely not buy this"

[Similar anchor sets exist for each question type - see `src/scales/registry.py` for complete definitions]

---

## Technical Notes

### Question Column Identification

Questions are identified in Kantar Excel files by pattern:
```
(QUESTION_CODE) QUESTION_NAME - CONCEPT_NAME
```

Example: `(UNPURINT) UNPRICED PURCHASE INTENT - US Pulse Play`

### Validation Approach

For each question:
1. Extract GT and Synthetic distributions
2. Calculate KL divergence, KS statistic, TVD, etc.
3. Compare to thresholds (KL < 0.20, KS > 0.85)
4. Assess PASS/WARN/FAIL
5. Aggregate to question type level

### Free-Text Handling

Free-text responses (Likes, Dislikes) are:
- Generated by LLM based on concept and persona
- Can be validated on coded categories (if present)
- Require qualitative review for tone/authenticity
- Not included in statistical validation metrics

---

**Document will be updated with actual performance data after validation completes.**
