# Survey Walkthrough Example - Synthetic Respondent Journey

This document shows exactly how the survey flows for a synthetic respondent, question by question, with all the logic and rules explained.

---

## Respondent Profile Generated

**ID:** P00042
**Demographics:**
- Gender: Female
- Age: 28 years old
- Age Band: 18-35
- Occupation: Technology

**Psychographics:**
- Category Buyer: Lottery played online/app, Paper scratchcards bought in person
- SC Players: SC Players (plays scratchcards)
- Inertia: 6 (likes to try new and different products)

**Persona Description for LLM:**
> "28 years old, female, works in Technology, buys lottery online and scratchcards, likes to try new and different products"

---

## Section A: Screening Questions

### Question S1: Age
**Question Type:** Numeric input
**Question Text:** "What is your age?"

**System Logic:**
- Already generated: 28
- **Screening Rule:** Age must be 18-75
- **Result:** ✅ PASS (28 is within range)

---

### Question S2: Gender
**Question Type:** Single choice
**Question Text:** "What is your gender?"

**Options:**
1. Male
2. Female
3. Non-binary or gender-fluid

**System Logic:**
- Already generated: Female
- **Screening Rule:** None (all genders accepted)
- **Result:** ✅ PASS

---

### Question S3: Occupation Screener
**Question Type:** Single choice
**Question Text:** "What is your current occupation category?"

**Options:**
1. Education
2. Healthcare
3. Technology ← **SELECTED**
4. Finance
5. Retail
6. Manufacturing
7. Hospitality
8. Transportation
9. Government
10. Marketing/Advertising ← **SCREENED OUT**
11. Market Research ← **SCREENED OUT**
12. Gaming/Lottery Industry ← **SCREENED OUT**
13. Other
14. Retired
15. Student
16. Unemployed

**System Logic:**
- Generated: Technology
- **Screening Rule:** Cannot work in Marketing/Advertising, Market Research, or Gaming/Lottery
- **Result:** ✅ PASS (Technology is allowed)
- **If FAILED:** Survey would terminate, respondent marked as "screened_out"

---

### Question S4: Category Buyer
**Question Type:** Multi-select
**Question Text:** "Which products/services have you bought?"

**Options:**
1. Lottery played in-store/person ← **SELECTED**
2. Lottery played online/app ← **SELECTED**
3. Paper scratchcards bought in person
4. None of the above

**System Logic:**
- Generated: Lottery played online/app, Paper scratchcards bought in person
- **Selection:** Multi-select, can choose 1-3 options
- **Result:** 2 options selected
- **Stored as:** `category_buyer` in psychographics

**Screening Rule (S4):**
- **Compound Rule:** If S2_3=2,3 (age band 56-75) AND S4 does not contain (3) → Screen Out
- **Meaning:** Respondents aged 56-75 who don't buy paper scratchcards are screened out
- **Logic:** Age 56-75 must include "Paper scratchcards bought in person" in their category_buyer selections
- **Implementation:** Checked after standard screening rules in `apply_screening()`

---

### Question S5: Category Non Rejector

**Question Type:** Multi-select
**Question Text:** "Which of the following would you NEVER spend money on?"
**Column Name:** `(CATNREJ) WOULD NEVER SPEND MONEY ON`

**Options:**
1. Lottery played in-store/person
2. Lottery played online/app
3. Paper scratchcards bought in person
4. None of the above ← **Most common**

**System Logic:**
- Generated: None of the above (75% of respondents)
- **Selection:** Multi-select, can choose 1-2 options
- **Weighted sampling:** Low probability of selecting paper scratchcards
- **Result:** Most select "None of the above" (won't reject anything)
- **Stored as:** `category_non_rejector` in psychographics

**Screening Rule (S5):**
- **Rule:** If S5 contains "Paper scratchcards bought in person" → Screen Out
- **Meaning:** If they would NEVER spend money on paper scratchcards → Screen out
- **Logic:** Excludes people who reject the core product category

**Example for P00001:**
- Would NEVER spend on: None of the above
- **Result:** ✅ PASS screening (doesn't reject anything)

---

### Question S7: Target Group

**Question Type:** Derived/Calculated (not asked directly)
**Column Name:** `(GROUPFMR) SAMPLE TYPE`

**Logic:** S7 is automatically determined based on age (S2) and category buyer (S4):

**Option 1: Young nonrejectors 18-35 (players or nonplayers)**
- **Rule:** `S2_3 = 1 and (S4=3 or S5<>3)`
- **Translation:** Age 18-35 AND (buys paper scratchcards OR is non-rejector)
- **Implementation:** Age 18-35 AND category_buyer is not "None of the above"

**Option 2: Current SC players 36-75**
- **Rule:** `S2_3 = 2,3 and S4=3`
- **Translation:** Age 36-75 AND buys paper scratchcards
- **Implementation:** Age 36-75 AND "Paper scratchcards bought in person" in category_buyer

**System Logic:**
- **Not asked:** Automatically calculated from S2 (age) and S4 (category buyer)
- **Stored as:** `target_group` in psychographics
- **Excel column:** `(GROUPFMR) SAMPLE TYPE`
- **Default:** "Main" (if neither condition is met)

**Example for P00001:**
- Age: 28 (age band 18-35)
- Category buyer: Lottery played online/app, Paper scratchcards bought in person
- **Result:** "Young nonrejectors 18-35 (players or nonplayers)"

---

### Question S8: SC Player Type

**Question Type:** Derived/Calculated (not asked directly)
**Column Name:** `(SCPLAYER) SC PLAYER TYPE`

**Logic:** S8 is automatically determined based on S4 (category buyer):

**Option 1: SC Players**
- **Rule:** S4=3 (has "Paper scratchcards bought in person")
- **Translation:** Buys paper scratchcards in person
- **Implementation:** "Paper scratchcards bought in person" in category_buyer

**Option 2: SC Non Players**
- **Rule:** S4<>3 (does NOT have "Paper scratchcards bought in person")
- **Translation:** Does not buy paper scratchcards in person
- **Implementation:** "Paper scratchcards bought in person" NOT in category_buyer

**System Logic:**
- **Not asked:** Automatically calculated from S4 (category buyer)
- **Stored as:** `sc_player_type` in psychographics
- **Excel column:** `(SCPLAYER) SC PLAYER TYPE`

**Example for P00001:**
- S4 Category buyer: Lottery played online/app, Paper scratchcards bought in person
- **Result:** "SC Players"

---

### Question S9: Brand Buyers

**Question Type:** Multi-select (minimum 1 selection)
**Question Text:** "Which of these scratch cards have you bought in the last 12 months, either for yourself or for someone else?"
**Column Name:** `(BRDBUY) BRANDS BOUGHT`

**Options:**
1. Zlatá rybka (Golden Fish)
2. Černá perla (Black Pearl)
3. Vánoční losy (Christmas Tickets)
4. Rentiér (Reindeer)
5. Mates
6. Zlatá podkova (Golden Horseshoe)
7. Zlatý měšec (Golden Purse)
8. Štístko (Lucky)
9. Maxa / Korunka
10. Fortuna
11. Other (open text)

**System Logic:**
- Generated: Černá perla, Vánoční losy, Rentiér
- **Selection:** Multi-select, can choose 1-5 brands
- **Weighted sampling:** Popular brands more likely
- **Result:** 3 brands selected
- **Stored as:** `brand_buyers` in psychographics
- **Excel format:** Comma-separated list (Černá perla,Vánoční losy,Rentiér)
- **"Other" option:** Included in brand list for open responses

---

## Concept Assignment

**Total Concepts Available:** 8
1. Christmas AR Message
2. Elf Yourself
3. AR Christmas Mini Game
4. Christmas Lip Sync
5. Christmas Duet
6. Christmas Cake Surprise
7. Birthday Message
8. Valentine Message

**System Logic:**
- **Rule:** Randomly select 3 concepts per respondent
- **Random Selection:** Uses `random.sample(range(8), 3)`
- **Selected Indices:** [2, 5, 7] (randomly chosen)

**Concepts This Respondent Will Evaluate:**
1. **Concept 3:** AR Christmas Mini Game (shown as position 1)
2. **Concept 6:** Christmas Cake Surprise (shown as position 2)
3. **Concept 8:** Valentine Message (shown as position 3)

**Note:** Order is randomized to reduce order bias

---

## Section B: Concept Testing

The system now loops through each of the 3 selected concepts and asks questions about each.

---

# CONCEPT 1: AR Christmas Mini Game

**Concept Description Shown to Respondent:**
> "Imagine being able to play a new AR mini-game on your scratch card!
>
> 🎁 This Christmas scratch card sells for 250 CZK and guarantees a win.
>
> After scanning the QR code, you can write a greeting and upload a photo or selfie. When the recipient scratches and scans the card, they'll enter a virtual winter scene with hills, snowballs, and walls.
>
> Your uploaded photo turns into a playful 3D avatar hiding behind obstacles and throwing virtual snowballs. The user can throw snowballs back to win the game.
>
> Available in stores and online."

---

### Question B2: Priced Purchase Intent
**Question Type:** Single-coded (Likert-5)
**Question Text:** "How likely would you be to buy this scratchcard at 250 CZK?"

**Scale Options:**
1. Definitely would
2. Probably would
3. Might or might not
4. Probably would not
5. Definitely would not

**System Processing:**

**Step 1: LLM Generates Free-Text Response**

*System Prompt:*
> "You are a consumer responding to a product concept survey. Your profile: You are 28 years old, female, works in Technology, buys lottery online and scratchcards, likes to try new and different products. Answer naturally and honestly as this person would."

*User Prompt:*
> "You are being shown this scratchcard concept: [concept description]
>
> Question: How likely would you be to buy this scratchcard at 250 CZK?
>
> Please explain your thoughts about purchasing this product."

*LLM Response (GPT-4o):*
> "This AR Christmas mini-game sounds really fun and interactive! I love trying new tech-enabled experiences, and the idea of turning a photo into a 3D avatar for a snowball fight is creative and different from regular scratchcards. At 250 CZK, it's a bit pricey for a scratchcard, but the guaranteed win and the unique AR experience make it feel like good value. I'd probably buy this to try it out, especially as a Christmas gift for someone who enjoys games."

**Step 2: SSR (Semantic Similarity Rating)**

*Anchor Embeddings (pre-computed):*
1. "I would definitely buy this scratchcard. It looks perfect for me and I'm very interested in purchasing it."
2. "I would probably buy this scratchcard. It seems appealing and I'd likely purchase it if I saw it."
3. "I might or might not buy this scratchcard. I'm unsure and would need to think about it more before deciding."
4. "I probably would not buy this scratchcard. It doesn't really appeal to me and I'd likely pass on it."
5. "I would definitely not buy this scratchcard. It doesn't interest me at all and I have no intention of purchasing it."

*Answer Embedding:* [1536-dimensional vector from text-embedding-3-small]

*Cosine Similarities:*
- Anchor 1: 0.78
- Anchor 2: **0.85** ← Highest
- Anchor 3: 0.62
- Anchor 4: 0.31
- Anchor 5: 0.19

*Softmax Normalization (T=0.5):*
- Level 1: 0.15
- Level 2: **0.58** ← Highest probability
- Level 3: 0.21
- Level 4: 0.04
- Level 5: 0.02

*Selection:* argmax → **Level 2**

**Response Recorded:**
```
(2) Probably would
```

**Conditional Logic Check:**
- **Rule:** If B2 = 4 or 5 (would not buy), ask B21 (barriers)
- **Result:** B2 = 2, so **SKIP B21**

---

### Question B21: Barriers (SKIPPED)
**Conditional Logic:** Only ask if B2 = "Probably would not" OR "Definitely would not"
**Status:** ❌ SKIPPED (B2 = "Probably would")

---

### Question B3: Uniqueness
**Question Type:** Single-coded (Likert-5)
**Question Text:** "How new and different is this concept?"

**Scale Options:**
1. Extremely new and different
2. Very new and different
3. Somewhat new and different
4. Slightly new and different
5. Not at all new and different

**System Processing:**

*LLM Response:*
> "This concept is very new and different. The AR mini-game element with the personalized 3D avatar is something I haven't seen on scratchcards before. Most scratchcards are just about revealing prizes, but this adds an interactive gaming layer that's quite innovative. It combines traditional lottery with modern AR technology in a fresh way."

*SSR Processing:*
- Closest anchor: "This is very new and different. It's quite novel and stands out from other scratchcards I've seen."
- Similarity: 0.91

**Response Recorded:**
```
(2) Very new and different
```

---

### Question B4: Value for Money
**Question Type:** Single-coded (Likert-5)
**Question Text:** "Compared to the price of 250 CZK, how much do you feel this scratchcard is worth?"

**Scale Options:**
1. Worth very much more
2. Worth somewhat more
3. Worth about the same
4. Worth somewhat less
5. Worth very much less

**System Processing:**

*LLM Response:*
> "At 250 CZK, I think this is worth about the same as the price. The guaranteed win means you'll definitely get something back, and the AR experience adds entertainment value beyond a regular scratchcard. It's not a huge bargain, but it feels fair for what you're getting - the prize plus the fun interactive element."

*SSR Processing:*
- Closest anchor: "This is worth about the same as the price. The value matches the cost - neither a bargain nor overpriced."
- Similarity: 0.88

**Response Recorded:**
```
(3) Worth about the same
```

---

### Question B6: Likeability
**Question Type:** Single-coded (Likert-6)
**Question Text:** "Overall, how much do you like or dislike this concept?"

**Scale Options:**
1. Like extremely
2. Like very much
3. Like moderately
4. Like slightly
5. Neither like nor dislike
6. Do not like at all

**System Processing:**

*LLM Response:*
> "I like this very much! The combination of AR technology with a traditional scratchcard is really clever. As someone who enjoys trying new tech products, this appeals to me. The snowball game sounds entertaining, and I appreciate that it's not just about winning money but also about having fun. It would make a great gift that people would remember."

*SSR Processing:*
- Closest anchor: "I like this very much. It's really appealing and I'm quite positive about it."
- Similarity: 0.93

**Response Recorded:**
```
(2) Like very much
```

---

### Question B7: Increment
**Question Type:** Single-coded (Binary)
**Question Text:** "If this scratchcard wasn't available, would you..."

**Options:**
1. Buy a different scratchcard
2. Not buy a scratchcard at all

**System Processing:**

*LLM Response:*
> "If this specific AR mini-game scratchcard wasn't available, I'd probably buy a different scratchcard instead. I already buy scratchcards occasionally, so I'd just choose another option that's available. This one is more appealing because of the AR feature, but I wouldn't skip buying scratchcards entirely if it wasn't there."

*SSR Processing:*
- Anchor 1: "If this wasn't available, I would buy a different scratchcard instead. I'd still purchase from the category."
- Anchor 2: "If this wasn't available, I wouldn't buy a scratchcard at all. I'd skip the purchase entirely."
- Closest: Anchor 1, Similarity: 0.89

**Response Recorded:**
```
(1) Would buy a different scratchcard
```

---

### Question B8: Portfolio Incrementality
**Question Type:** Open text
**Question Text:** "How does this compare to other scratchcards you've seen?"

**System Processing:**

*LLM Response:*
> "This stands out significantly from other scratchcards I've seen. Most scratchcards are purely about revealing a prize - you scratch, you see if you won, and that's it. This one adds a whole interactive gaming experience with AR technology. The personalization aspect where you can add your own photo is also unique. It transforms a scratchcard from a simple lottery ticket into an entertainment experience that you can share with others."

**Response Recorded:**
```
This stands out significantly from other scratchcards I've seen. Most scratchcards are purely about revealing a prize - you scratch, you see if you won, and that's it. This one adds a whole interactive gaming experience with AR technology. The personalization aspect where you can add your own photo is also unique. It transforms a scratchcard from a simple lottery ticket into an entertainment experience that you can share with others.
```

**Note:** Open text questions are stored as-is, no SSR rating needed

---

### Question B11: Relevance
**Question Type:** Single-coded (Likert-5)
**Question Text:** "How relevant is this concept to you personally?"

**Scale Options:**
1. Not at all relevant
2. Slightly relevant
3. Moderately relevant
4. Very relevant
5. Extremely relevant

**System Processing:**

*LLM Response:*
> "This is very relevant to me. I'm in tech, I like interactive experiences, I already buy scratchcards occasionally, and I enjoy trying innovative products. The AR gaming element particularly appeals to my interests. Plus, I could see myself buying this as a Christmas gift, which makes it even more relevant to my needs."

*SSR Processing:*
- Closest anchor: "This is very relevant to me. It aligns well with my interests and preferences."
- Similarity: 0.87

**Response Recorded:**
```
(4) Very relevant
```

---

### Question B12: Excitement
**Question Type:** Single-coded (Likert-4)
**Question Text:** "How exciting is this concept?"

**Scale Options:**
1. Very exciting
2. Somewhat exciting
3. Not very exciting
4. Not at all exciting

**System Processing:**

*LLM Response:*
> "This is very exciting! The AR mini-game aspect is genuinely innovative for a scratchcard. The idea of creating a personalized avatar that throws snowballs is fun and different. It's the kind of product that would make people say 'that's cool!' when they see it. It brings an element of surprise and entertainment that regular scratchcards don't have."

*SSR Processing:*
- Closest anchor: "This is very exciting. It really grabs my attention and generates enthusiasm."
- Similarity: 0.90

**Response Recorded:**
```
(1) Very exciting
```

---

### Question B13: Understanding
**Question Type:** Slider (9-point)
**Question Text:** "How well do you understand what to expect from this product?"

**Scale Options:**
1. Don't know what to expect at all
2. Don't know what to expect
3. Mostly don't know what to expect
4. Somewhat don't know what to expect
5. Neutral
6. Somewhat know what to expect
7. Mostly know what to expect
8. Know what to expect
9. Know exactly what to expect

**System Processing:**

*LLM Response:*
> "I have a pretty clear understanding of what to expect. You buy the card, scan a QR code, upload a photo and message, and the recipient gets to play an AR snowball game where your photo appears as an avatar. It's straightforward - a scratchcard plus an AR gaming experience. The concept is well explained and easy to visualize."

*SSR Processing:*
- Closest anchor: "I mostly know what to expect. It's quite clear with good understanding overall."
- Similarity: 0.86

**Response Recorded:**
```
(7) Mostly know what to expect
```

---

### Question B14: Believability
**Question Type:** Single-coded (Likert-4)
**Question Text:** "How believable is it that this product would work as described?"

**Scale Options:**
1. Very believable
2. Somewhat believable
3. Not very believable
4. Not at all believable

**System Processing:**

*LLM Response:*
> "This is very believable. AR technology is already widely used in apps and games, so applying it to a scratchcard makes sense. Scanning QR codes is standard, uploading photos is simple, and AR gaming is proven technology. I can easily see this working exactly as described - it's not asking for anything that doesn't already exist in other apps."

*SSR Processing:*
- Closest anchor: "This is very believable. It seems completely realistic and credible."
- Similarity: 0.91

**Response Recorded:**
```
(1) Very believable
```

---

### Question B15: Likes (Open)
**Question Type:** Open text
**Question Text:** "What do you like about this concept?"

**System Processing:**

*LLM Response:*
> "I like the innovative use of AR technology to make a scratchcard more than just a lottery ticket. The personalization with the photo upload is great - it makes it feel custom and special. The snowball game sounds genuinely fun, and the guaranteed win removes the risk. It's also shareable and would make a memorable gift. The combination of traditional lottery with modern gaming is clever."

**Response Recorded:**
```
I like the innovative use of AR technology to make a scratchcard more than just a lottery ticket. The personalization with the photo upload is great - it makes it feel custom and special. The snowball game sounds genuinely fun, and the guaranteed win removes the risk. It's also shareable and would make a memorable gift. The combination of traditional lottery with modern gaming is clever.
```

---

### Question B16: Dislikes (Open)
**Question Type:** Open text
**Question Text:** "What do you dislike about this concept?"

**System Processing:**

*LLM Response:*
> "The price of 250 CZK is a bit high for a scratchcard - that's about double what I'd normally spend. Also, it requires a smartphone with AR capabilities, which might exclude some people. I wonder if the AR experience would get old quickly, or if there's enough variety in the game to make it interesting beyond the first try. Technical issues could also be frustrating if the app doesn't work smoothly."

**Response Recorded:**
```
The price of 250 CZK is a bit high for a scratchcard - that's about double what I'd normally spend. Also, it requires a smartphone with AR capabilities, which might exclude some people. I wonder if the AR experience would get old quickly, or if there's enough variety in the game to make it interesting beyond the first try. Technical issues could also be frustrating if the app doesn't work smoothly.
```

---

### Question B17: Highlighter Drivers (SKIPPED)
**Question Type:** Visual highlighter
**Reason:** Visual questions not supported in text-based SSR system
**Status:** ❌ SKIPPED

---

### Question B18: Highlighter Barriers (SKIPPED)
**Question Type:** Visual highlighter
**Reason:** Visual questions not supported in text-based SSR system
**Status:** ❌ SKIPPED

---

### Question B20: Imagery
**Question Type:** Multi-coded (multiple selection)
**Question Text:** "What words would you use to describe this concept? (Select all that apply)"

**Options:**
1. Innovative
2. Fun
3. Expensive
4. Complicated
5. Exciting
6. Traditional
7. Unique
8. Confusing
9. Modern
10. Gimmicky

**System Processing:**

*LLM Response:*
> "I would describe this as innovative, fun, exciting, unique, and modern. The AR gaming element is definitely innovative and exciting. It's unique compared to regular scratchcards, and the whole concept feels modern with the tech integration. The snowball game aspect makes it fun. I wouldn't say it's expensive relative to the experience, traditional, complicated, confusing, or gimmicky."

*Parsing:* System extracts selected words from response
- Pattern matching: "innovative" → Found
- Pattern matching: "fun" → Found
- Pattern matching: "exciting" → Found
- Pattern matching: "unique" → Found
- Pattern matching: "modern" → Found

**Response Recorded:**
```
Innovative, Fun, Exciting, Unique, Modern
```

---

### Question B22: Gift Purchase Intent
**Question Type:** Single-coded (Likert-5)
**Question Text:** "How likely would you be to buy this as a gift?"

**Scale Options:**
1. Definitely would
2. Probably would
3. Might or might not
4. Probably would not
5. Definitely would not

**System Processing:**

*LLM Response:*
> "I would definitely buy this as a gift! The AR mini-game makes it special and memorable - it's not just giving someone money, you're giving them an experience. For Christmas especially, this would be a fun and unique gift. The personalization aspect where you can add a photo and message makes it more thoughtful than a regular scratchcard. It's perfect for someone who enjoys games and tech."

*SSR Processing:*
- Closest anchor: "I would definitely buy this as a gift. It would make a perfect present for someone."
- Similarity: 0.92

**Response Recorded:**
```
(1) Definitely would
```

---

### Question B23: Occasions
**Question Type:** Multi-select (minimum 1 selection)
**Question Text:** "For what occasions do you think this scratch card / board game is suitable?"
**Conditional Logic:** Only ask if B22 = 1, 2, or 3 (would buy as gift)

**Options:**
1. To play at home with family or a partner
2. For a party with friends
3. For a cottage stay, weekend getaway, or vacation
4. For another occasion, please specify (Open text - code 996)

**System Processing:**

*LLM Response:*
> "This scratch card board game would be suitable for playing at home with family or a partner - the AR gaming element is fun for casual home entertainment. It's also perfect for a party with friends, where the interactive game can add excitement. And I could see it being great for a cottage stay or weekend getaway, when you want something entertaining but not too serious."

*Parsing:* Extracts occasions mentioned
- To play at home with family or a partner → Found
- For a party with friends → Found
- For a cottage stay, weekend getaway, or vacation → Found

**Response Recorded:**
```
To play at home with family or a partner, For a party with friends, For a cottage stay, weekend getaway, or vacation
```

---

### Question B24: Pleased with Gift
**Question Type:** Single-coded (Likert-5)
**Question Text:** "If you received this as a gift, how pleased would you be?"
**Conditional Logic:** None (always shown)

**Scale Options:**
1. Extremely pleased
2. Very pleased
3. Moderately pleased
4. Slightly pleased
5. Not at all pleased

**System Processing:**

*LLM Response:*
> "I would be very pleased to receive this as a gift! It shows the person put thought into choosing something fun and different rather than just generic. The AR game would be entertaining to try, and the guaranteed win means I'd definitely get something out of it. Plus, I appreciate when people give me tech-related gifts that let me try new experiences. It's way more interesting than a regular scratchcard."

*SSR Processing:*
- Closest anchor: "I would be very pleased to receive this as a gift. I'd really appreciate getting this."
- Similarity: 0.90

**Response Recorded:**
```
(2) Very pleased
```

---

## ✅ Concept 1 Complete

**Summary of Responses for Concept 3 (AR Christmas Mini Game):**
- B2 Purchase Intent: (2) Probably would
- B3 Uniqueness: (2) Very new and different
- B4 Value: (3) Worth about the same
- B6 Likeability: (2) Like very much
- B7 Increment: (1) Would buy a different scratchcard
- B8 Portfolio: [Open text response]
- B11 Relevance: (4) Very relevant
- B12 Excitement: (1) Very exciting
- B13 Understanding: (7) Mostly know what to expect
- B14 Believability: (1) Very believable
- B15 Likes: [Open text response]
- B16 Dislikes: [Open text response]
- B20 Imagery: Innovative, Fun, Exciting, Unique, Modern
- B22 Gift Intent: (1) Definitely would
- B23 Occasions: To play at home with family or a partner, For a party with friends, For a cottage stay, weekend getaway, or vacation
- B24 Pleased: (2) Very pleased

---

# CONCEPT 2: Christmas Cake Surprise

**System Logic:** Same process repeats for Concept 6

**Concept Description:**
> "Imagine adding a personal surprise to your Christmas scratch card!
>
> 🎁 After scanning the QR code, you can upload a photo or selfie and choose a festive character (Santa, elf, reindeer).
>
> When the recipient scratches and scans, they'll get instructions to place a virtual cake using world tracking AR. As they approach, your character 'jumps out of the cake'!
>
> The recipient's reaction is recorded, and the whole scene is replayed as a shareable video with your holiday message.
>
> Available in stores and online."

**Process:** All questions B2-B24 are asked again for this concept
**Time:** ~20-25 seconds per question
**Result:** Another full set of responses

---

# CONCEPT 3: Valentine Message

**System Logic:** Same process repeats for Concept 8

**Concept Description:**
> "Imagine attaching a personal digital Valentine full of love to your scratch card.
>
> 🎁 After scanning the QR code, you can record a special Valentine message for your loved one.
>
> When they scratch and scan, your message will appear above the card, animated through augmented video — bringing your love message to life.
>
> Available in stores and online."

**Process:** All questions B2-B24 are asked again for this concept
**Time:** ~20-25 seconds per question
**Result:** Another full set of responses

---

## Survey Complete! 🎉

**Total Questions Asked for P00042:**
- Screening: 3 questions
- Concept 1: 16 questions (2 skipped: B21, B17, B18)
- Concept 2: 16 questions
- Concept 3: 16 questions
- **Total: 51 questions**

**Time Taken:** ~20-25 minutes
**API Calls:**
- LLM calls: 48 (16 questions × 3 concepts)
- Embedding calls: ~26 (scales cached, only answer embeddings needed)

---

## Excel Output Format

**Columns for this respondent:**

```
SERIAL: P00042
DATE: 2024-12-10
Gender: Female
(SEX) SEX: (2) Female
AGE: 28
(AGEQUOTA) AGEBANDS: (1) 18-35
(OCCUPATION_SCR) OCCUPATION SCREENER: (3) Technology

Concept 3: (PRPURINT) PRICED PURCHASE INTENT: (2) Probably would
Concept 3: (UNIQNESS) UNIQUENESS: (2) Very new and different
Concept 3: (PRVALMNY) VALUE FOR MONEY: (3) Worth about the same
Concept 3: (LIKBILTY) LIKEABILITY: (2) Like very much
...

Concept 6: (PRPURINT) PRICED PURCHASE INTENT: (1) Definitely would
Concept 6: (UNIQNESS) UNIQUENESS: (1) Extremely new and different
...

Concept 8: (PRPURINT) PRICED PURCHASE INTENT: (2) Probably would
...

[All other concept columns are empty/NaN for this respondent since they only saw 3 concepts]
```

---

## Key System Features Demonstrated

### 1. **Conditional Logic**
- B21 (Barriers) only asked if B2 = 4 or 5
- System evaluates conditions after each response

### 2. **Random Concept Assignment**
- 3 out of 8 concepts randomly selected
- Different respondents get different combinations
- Order randomized within the 3 selected

### 3. **Persona-Driven Responses**
- LLM considers age, gender, occupation, buying habits, inertia
- Responses are coherent with persona profile
- High inertia (6) → positive attitude toward innovation

### 4. **SSR Rating**
- Free-text converted to scale ratings
- Embedding similarity to anchors
- Probabilistic selection via softmax

### 5. **Multiple Question Types**
- Single-coded Likert (most common)
- Multi-coded (multiple selection)
- Open text (stored as-is)
- Binary (2 options)
- Sliders (9-point, 7-point)

### 6. **Screening**
- Age check
- Occupation screening (excludes competitors)
- Failed screening → survey terminates

---

## Validation Against Ground Truth

This synthetic respondent's data can now be compared to real respondents:
- **Distribution matching:** Do synthetic responses have similar distributions?
- **KL divergence:** How different are the probability distributions?
- **Correlation:** Do synthetic and real data correlate similarly?

**Next step:** Generate 50-400 respondents like this and validate!

---

**Generated:** December 10, 2024
**Example Respondent:** P00042
**Concepts Tested:** 3 of 8 (AR Christmas Mini Game, Christmas Cake Surprise, Valentine Message)
**Questions Answered:** 51 total
