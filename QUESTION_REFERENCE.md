# Question Reference Guide

Complete reference of all survey questions, options, and conditional logic.

---

## Screening Questions (Section S)

### S1: Gender
**Question:** "What is your gender?"

**Type:** Single-coded

**Options:**
1. Male
2. Female

**Conditions:** Always show

---

### S2: Age
**Question:** "What is your age?"

**Type:** Single-coded (derived into age bands)

**Age Bands:**
- S2_1: 18-35 years
- S2_2: 36-55 years
- S2_3: 56-75 years

**Conditions:** Always show

**Screening:** Age must be 18-75 inclusive

---

### S3: Occupation Screener
**Question:** "What is your occupation?"

**Type:** Single-coded

**Options:**
1. Advertising/PR
2. Marketing/Market Research
3. Lottery sales/distribution
4. Tobacco shop salesperson
5. Other

**Conditions:** Always show

**Screening:** If occupation is any of options 1-4, screen out

---

### S4: Category Buyer (Products/Services Bought)
**Question:** "Which of the following products or services have you bought in the last 6 months?"

**Type:** Multi-select (minimum 1 selection required)

**Options:**
1. Lottery played in-store/person
2. Lottery played online/app
3. Paper scratchcards bought in person
4. None of the above

**Conditions:** Always show

**Screening (Compound Rule):**
- If age band is 56-75 (S2_3=2,3) AND S4 does not contain option 3 (Paper scratchcards bought in person) → Screen out

---

### S5: Category Non Rejector (Would Never Spend Money On)
**Question:** "Which of the following would you NEVER spend money on?"

**Type:** Multi-select (maximum 3 selections)

**Options:**
1. Lottery played in-store/person
2. Lottery played online/app
3. Paper scratchcards bought in person
4. None of the above

**Conditions:** Always show

**Screening:**
- If S5 contains option 3 (Paper scratchcards bought in person) → Screen out

---

### S7: Target Group
**Question:** DERIVED FIELD (not asked directly)

**Type:** Derived from S2 (age) and S4 (category buyer)

**Options:**
1. Young nonrejectors 18-35 (players or nonplayers)
   - Logic: S2_1=1 (age 18-35) AND (S4=3 OR S5≠3)
   - Meaning: Age 18-35 AND (buys paper scratchcards OR doesn't reject paper scratchcards)

2. Current SC players 36-75
   - Logic: S2_3=2,3 (age 36-75) AND S4=3
   - Meaning: Age 36-75 AND buys paper scratchcards

**Conditions:** Always derived

---

### S8: SC Player Type
**Question:** DERIVED FIELD (not asked directly)

**Type:** Derived from S4 (category buyer)

**Options:**
1. SC Players
   - Logic: If S4 contains option 3 (Paper scratchcards bought in person)

2. SC Non Players
   - Logic: If S4 does not contain option 3

**Conditions:** Always derived

---

### S9: Brand Buyers (Brands Bought)
**Question:** "Which of the following lottery brands have you bought in the last 6 months?"

**Type:** Multi-select (minimum 1 selection required)

**Options:**
1. Zlatá rybka
2. Černá perla
3. Vánoční losy
4. Rentiér
5. Sázka na 6
6. Sportka
7. EuroJackpot
8. EuroMillions
9. Šťastných 10
10. Kasička
11. Loterie
12. Other

**Conditions:** Always show

---

## Concept Test Questions (Section B)

All Section B questions are asked per concept tested. Each respondent sees multiple concepts in randomized order.

---

### B2: Priced Purchase Intent
**Question:** "How likely would you be to buy this product at the stated price?"

**Type:** Single-coded (5-point Likert)

**Options:**
1. Definitely will buy
2. Probably will buy
3. Might or might not buy
4. Probably won't buy
5. Definitely won't buy

**Conditions:** Always show

**Note:** This is a key branching question - responses determine if B21 and B22 are asked

---

### B21: Barriers to Purchase
**Question:** "Why wouldn't you buy this product?"

**Type:** Multi-select (minimum 1 selection required, random order)

**Options:**
1. I don't play board games
2. The game mechanics didn't appeal to me
3. The rules are too complicated
4. The game's theme is not appealing to me
5. The ticket price is too high
6. The main prize is too low
7. Other reason, please specify

**Conditions:** Only show if B2=4,5 (low purchase intent)

**Logic:** Only ask about barriers when respondent has low purchase intent

---

### B3: Uniqueness
**Question:** "How unique is this product compared to other products on the market?"

**Type:** Single-coded (5-point Likert)

**Options:**
1. Very unique
2. Somewhat unique
3. Neither unique nor common
4. Somewhat common
5. Very common

**Conditions:** Always show

---

### B4: Value for Money
**Question:** "Do you think this product offers good value for money at [PRICE]?"

**Type:** Single-coded (5-point Likert)

**Options:**
1. Excellent value
2. Good value
3. Fair value
4. Poor value
5. Very poor value

**Conditions:** Always show

**Note:** Price is dynamically inserted from concept

---

### B6: Likeability
**Question:** "How much do you like this product overall?"

**Type:** Single-coded (6-point Likert)

**Options:**
1. Like it very much
2. Like it quite a bit
3. Like it somewhat
4. Dislike it somewhat
5. Dislike it quite a bit
6. Dislike it very much

**Conditions:** Always show

---

### B7: Increment (Buy Instead if Not Available)
**Question:** "If this product was not available, would you buy a different scratchcard instead?"

**Type:** Binary (Yes/No)

**Options:**
1. Yes - I would buy a different scratchcard
2. No - I would not buy any scratchcard

**Conditions:** Always show

**Note:** This is a branching question - if B7=1, then B8 is asked (though B8 not in current implementation)

---

### B11: Relevance
**Question:** "How relevant is this product to you personally?"

**Type:** Single-coded (5-point Likert)

**Options:**
1. Very relevant
2. Somewhat relevant
3. Neither relevant nor irrelevant
4. Somewhat irrelevant
5. Very irrelevant

**Conditions:** Always show

---

### B11a: Playfulness
**Question:** "How playful and fun does this product seem?"

**Type:** Single-coded (5-point Likert)

**Options:**
1. Very playful
2. Somewhat playful
3. Neither playful nor serious
4. Somewhat serious
5. Very serious

**Conditions:** Always show

---

### B12: Excitement
**Question:** "How exciting is this product?"

**Type:** Single-coded (4-point Likert)

**Options:**
1. Very exciting
2. Somewhat exciting
3. Not very exciting
4. Not at all exciting

**Conditions:** Always show

---

### B13: Understanding (Other Category)
**Question:** "How well do you understand what this product is about?"

**Type:** Slider (9-point scale)

**Options:**
- Scale: 1-9
- 1 = Don't understand at all
- 9 = Understand completely

**Conditions:** Always show

---

### B14: Believability
**Question:** "How believable is the product concept?"

**Type:** Single-coded (4-point Likert)

**Options:**
1. Very believable
2. Somewhat believable
3. Not very believable
4. Not at all believable

**Conditions:** Always show

---

### B15: Likes (Open-ended)
**Question:** "What do you like most about this product?"

**Type:** Open text

**Options:**
- Free-text response
- OR "Nothing" / blank response (respondent has nothing to like)

**Conditions:** Always show

**Note:** Respondents can leave blank or indicate "nothing" if they have no positive feedback

---

### B16: Dislikes (Open-ended)
**Question:** "What do you like least about this product?"

**Type:** Open text

**Options:**
- Free-text response
- OR "Nothing" / blank response (respondent has no dislikes)

**Conditions:** Always show

**Note:** Respondents can leave blank or indicate "nothing" if they have no negative feedback

---

### B22: Would Buy as Gift
**Question:** "Would you consider buying this product as a gift?"

**Type:** Single-coded (5-point Likert)

**Options:**
1. Definitely would buy as gift
2. Probably would buy as gift
3. Might or might not buy as gift
4. Probably wouldn't buy as gift
5. Definitely wouldn't buy as gift

**Conditions:** Only show if B2=1,2,3 (any positive purchase intent)

**Logic:** Only ask about gift intent when respondent has some purchase intent

**Note:** This is a branching question - responses determine if B23 is asked

---

### B23: Gift Occasions
**Question:** "For what occasions do you think this scratch card / board game is suitable?"

**Type:** Multi-select (minimum 1 selection required, random order)

**Options:**
1. To play at home with family or a partner
2. For a party with friends
3. For a cottage stay, weekend getaway, or vacation
4. For another occasion, please specify

**Conditions:** Only show if B22=1,2,3 (any positive gift intent)

**Logic:** Only ask about occasions when respondent would consider buying as gift

---

### B24: Pleased with Gift
**Question:** "How pleased would you be to receive this product as a gift?"

**Type:** Single-coded (5-point Likert)

**Options:**
1. Very pleased
2. Somewhat pleased
3. Neither pleased nor displeased
4. Somewhat displeased
5. Very displeased

**Conditions:** ALWAYS SHOW (no conditions)

**Note:** This question has no conditional logic - it is asked regardless of B22 response

---

## Conditional Logic Summary

### Screening Flow
1. **S3 (Occupation)** → If excluded occupation → Screen out
2. **S2 (Age)** → If outside 18-75 → Screen out
3. **S4 (Category Buyer)** + **S2 (Age)** → If age 56-75 AND doesn't buy paper scratchcards → Screen out
4. **S5 (Category Non Rejector)** → If would never spend on paper scratchcards → Screen out

### Question Flow (Per Concept)
1. **B2** → Always show (BRANCHING POINT)
   - If B2=4,5 → Show **B21** (Barriers)
   - If B2=1,2,3 → Show **B22** (Gift Intent)

2. **B3-B16** → Always show

3. **B22** → Only if B2=1,2,3 (BRANCHING POINT)
   - If B22=1,2,3 → Show **B23** (Occasions)

4. **B24** → Always show

### Questions NOT Implemented

The following questions from the source questionnaire are **NOT implemented** in this system:

- **B1: Concept Intro**
  - Type: Informational text (not a question)
  - Reason: Not a measurable question, just concept presentation text

- **B8: Portfolio Incrementality**
  - Condition: Only if B7=1 (would buy different scratchcard)
  - Reason: Not present in ground truth data

- **B17: Highlighter Drivers**
  - Type: Visual/image-based question
  - Reason: Not present in ground truth data, requires visual interaction

- **B18: Highlighter Barriers**
  - Type: Visual/image-based question
  - Reason: Not present in ground truth data, requires visual interaction

- **B20: Imagery**
  - Type: Imagery attributes question
  - Reason: Not present in ground truth data

**Why not implemented:** These questions are either non-questions (B1), visual/interactive questions not suitable for synthetic generation (B17, B18), or not present in the ground truth dataset used for validation (B8, B17, B18, B20).

---

## Question Order

### Screening Section (S)
1. S1 - Gender
2. S2 - Age
3. S3 - Occupation (SCREENER)
4. S4 - Category Buyer (SCREENER with compound rule)
5. S5 - Category Non Rejector (SCREENER)
6. S7 - Target Group (DERIVED)
7. S8 - SC Player Type (DERIVED)
8. S9 - Brand Buyers

### Concept Test Section (B) - Per Concept
1. B2 - Purchase Intent
2. B21 - Barriers (conditional)
3. B3 - Uniqueness
4. B4 - Value for Money
5. B6 - Likeability
6. B7 - Increment
7. B11 - Relevance
8. B11a - Playfulness
9. B12 - Excitement
10. B13 - Understanding
11. B14 - Believability
12. B15 - Likes (open)
13. B16 - Dislikes (open)
14. B22 - Would Buy as Gift (conditional)
15. B23 - Gift Occasions (conditional)
16. B24 - Pleased with Gift

---

## Scale Types Used

- **LIKERT_4:** 4-point Likert scale (B12, B14)
- **LIKERT_5:** 5-point Likert scale (B2, B3, B4, B11, B11a, B22, B24)
- **LIKERT_6:** 6-point Likert scale (B6)
- **SLIDER_9:** 9-point slider scale (B13)
- **BINARY:** Yes/No question (B7)
- **MULTI_SELECT:** Multiple selection questions (S4, S5, S9, B21, B23)
- **OPEN_TEXT:** Free-text response (B15, B16)

---

## Important Notes

1. **Text Labels vs Codes:** The system uses text labels (e.g., "Definitely will buy") not numeric codes (996, 998)

2. **Open-Text Questions (B15, B16) - FULLY IMPLEMENTED:**
   - **B15** uses specific prompt: "What do you like most about this product?"
   - **B16** uses specific prompt: "What do you like least about this product?"
   - Both prompts explicitly encourage honest responses including "Nothing"
   - System detects "nothing" variants and converts to blank strings
   - Blank responses are valid and expected for some personas/concepts
   - Implementation includes post-processing to handle minimal responses

3. **Random Order:** Multi-select questions B21 and B23 randomize option order

4. **Minimum Selections:** Multi-select questions require minimum 1 selection (except S5 which allows 0 for "None")

5. **Derived Fields:** S7 and S8 are calculated, not asked

6. **Conditional Chains:**
   - B2 → B21 (if low intent)
   - B2 → B22 (if positive intent) → B23 (if positive gift intent)

7. **Price Dynamic:** B4 includes concept price dynamically

8. **Ground Truth Alignment:** All questions match exactly to source questionnaire document

9. **Questions Not Implemented:** B1, B8, B17, B18, B20 are not implemented (see "Questions NOT Implemented" section above)

---

**Generated:** December 12, 2024
**Source:** Board games_questionnaire EN MASTER.docx
**Implementation:** S.A.G.E Test System
