# Start to Finish Guide - Synthetic Survey System

## Complete Walkthrough: From Setup to Analysis

This guide walks you through running the entire synthetic survey system from scratch.

---

## Prerequisites

### 1. Files You Need

Ensure these files are in the `source docs/` folder:
- ✅ `Board games_questionnaire EN MASTER.docx` - Survey questions
- ✅ `Tech_Enabled_CZ_Concepts_EN.pptx` - 8 concepts to test
- ✅ `KAP400232611_Respondent_Data_Tech Enabled CZ.xlsx` - Ground truth data

### 2. Environment Setup

**Option A: If you haven't set up yet:**
```bash
# Install dependencies
uv pip install numpy pandas scipy python-docx python-pptx openpyxl matplotlib seaborn scikit-learn openai tqdm pydantic pyyaml python-dotenv

# Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

**Option B: If already set up:**
```bash
# Just verify .env has your API key
cat .env
# Should show: OPENAI_API_KEY=sk-...
```

---

## Quick Start (5 minutes)

If you just want to generate data immediately:

```bash
# Generate 10 synthetic respondents (takes ~3-5 minutes)
python run_full_pipeline.py -n 10

# Output will be in: data/synthetic/synthetic_data_10resp_TIMESTAMP.xlsx
```

**That's it!** The system will:
1. Parse your documents (auto-loads from `data/parsed/`)
2. Generate 10 personas
3. Each persona evaluates 3 random concepts
4. Answers all questions using GPT-4o + SSR
5. Exports to Excel matching ground truth format

---

## Step-by-Step Walkthrough

### Step 1: Parse Your Documents

**What it does:** Extracts concepts, questions, and data structure from your source files.

**Option A: Using Jupyter Notebook (Recommended for first time)**
```bash
# Start Jupyter
jupyter notebook

# Open and run: notebooks/01_data_extraction.ipynb
# This will create JSON files in data/parsed/
```

**Option B: Quick parse from command line**
```bash
# Parse concepts only (needed for pipeline)
python -c "
from src.parsers.concept_parser import ConceptParser
import json

parser = ConceptParser('source docs/Tech_Enabled_CZ_Concepts_EN.pptx')
concepts = parser.parse()

# Save to JSON
with open('data/parsed/concepts.json', 'w') as f:
    json.dump([{
        'id': c.id,
        'name': c.name,
        'description': c.description,
        'full_text': c.full_text,
        'price': c.price,
        'occasion': c.occasion,
        'features': c.features
    } for c in concepts], f, indent=2)

print(f'✓ Parsed {len(concepts)} concepts')
"
```

**Expected output:**
```
✓ Parsed 8 concepts
```

---

### Step 2: Test the SSR System (Optional but Recommended)

**What it does:** Verifies LLM and embedding service work correctly.

```bash
# Open and run: notebooks/02_ssr_demo.ipynb
jupyter notebook notebooks/02_ssr_demo.ipynb
```

This notebook will:
- Test OpenAI API connection
- Show how SSR converts text to ratings
- Display example persona responses

**Expected result:** You'll see example responses being converted to Likert ratings.

---

### Step 3: Generate Small Test Dataset

**What it does:** Creates a small dataset to verify everything works.

```bash
# Generate 5 respondents with just 3 questions (fast test)
python run_full_pipeline.py -n 5 --questions B2 B3 B6
```

**What happens:**
1. ✓ Loads 8 concepts from `data/parsed/concepts.json`
2. ✓ Generates 5 personas (random demographics)
3. ✓ Each persona evaluates 3 random concepts
4. ✓ Answers 3 questions per concept using GPT-4o
5. ✓ Converts responses to ratings using SSR
6. ✓ Exports to Excel

**Time:** ~2-3 minutes

**Output:**
```
data/synthetic/synthetic_data_5resp_TIMESTAMP.xlsx
data/synthetic/metadata_synthetic_data_5resp_TIMESTAMP.json
```

**Verification:**
```bash
# Check the output
python -c "
import pandas as pd
df = pd.read_excel('data/synthetic/synthetic_data_5resp_*.xlsx')
print(f'Rows: {len(df)}')
print(f'Columns: {len(df.columns)}')
print(f'Sample columns: {list(df.columns[:10])}')
"
```

---

### Step 4: Generate Full Dataset

**What it does:** Creates dataset matching your ground truth size.

```bash
# Generate 50 respondents with all questions
python run_full_pipeline.py -n 50

# OR match ground truth size (400 respondents)
python run_full_pipeline.py -n 400
```

**Time estimates:**
- 50 respondents: ~15-20 minutes
- 100 respondents: ~30-40 minutes
- 200 respondents: ~60-80 minutes
- 400 respondents: ~2-3 hours

**Cost estimates (with GPT-4o):**
- 50 respondents: ~$10
- 100 respondents: ~$20
- 200 respondents: ~$40
- 400 respondents: ~$80

**Progress tracking:**
```
Running survey:  67%|██████▋ | 33/50 [12:45<06:22, 22.48s/it]
```

**Output:**
```
data/synthetic/synthetic_data_50resp_TIMESTAMP.xlsx
data/synthetic/metadata_synthetic_data_50resp_TIMESTAMP.json
```

---

### Step 5: Validate Against Ground Truth

**What it does:** Compares synthetic vs. real data using statistical metrics.

```bash
# Open validation notebook
jupyter notebook notebooks/07_validation_and_comparison.ipynb
```

**What you'll see:**

1. **Distribution Comparisons**
   - Side-by-side bar charts for each question
   - Synthetic vs. ground truth distributions

2. **KL Divergence Metrics**
   - Lower = better (target: <0.10)
   - Heatmap showing per-question quality

3. **Correlation Metrics**
   - Target: >0.85 (human test-retest reliability)
   - Correlation attainment percentage

4. **Statistical Tests**
   - KS statistic (distribution similarity)
   - Chi-square tests

**Good results:**
```
Average KL Divergence: 0.08  ✅ (target: <0.10)
Correlation: 0.87  ✅ (target: >0.85)
Correlation Attainment: 92%  ✅ (paper benchmark: ~90%)
```

**If results are poor:**
- Review anchor statements in `src/scales/registry.py`
- Refine anchors for poorly performing questions
- Re-generate and validate

---

### Step 6: Iterate and Refine (If Needed)

If validation shows some questions performing poorly:

**Option A: Refine specific anchors**
```bash
# Edit anchor statements
nano src/scales/registry.py

# Find the scale with poor KL divergence
# Example: likert5_purchase_intent_v1
# Refine the anchor texts to be more discriminative

# Re-run with new anchors
python run_full_pipeline.py -n 50
```

**Option B: Test specific questions**
```bash
# Focus on problematic questions
python run_full_pipeline.py -n 30 --questions B2 B7 B12

# Validate just those
jupyter notebook notebooks/07_validation_and_comparison.ipynb
```

---

## Common Command Options

### Basic Generation
```bash
# Default: 50 respondents, all questions, 3 concepts each
python run_full_pipeline.py
```

### Custom Respondent Count
```bash
python run_full_pipeline.py -n 100
```

### Specific Questions Only
```bash
python run_full_pipeline.py -n 50 --questions B2 B3 B6 B7
```

### Custom Concepts Per Respondent
```bash
# Test all 8 concepts per respondent (not recommended - doesn't match ground truth)
python run_full_pipeline.py -n 50 --concepts-per-resp 8

# Monadic testing (1 concept per respondent)
python run_full_pipeline.py -n 400 --concepts-per-resp 1
```

### Custom Random Seed (for reproducibility)
```bash
python run_full_pipeline.py -n 50 --seed 123
```

### Custom Output Path
```bash
python run_full_pipeline.py -n 50 -o my_data.xlsx
```

### Combine Options
```bash
python run_full_pipeline.py \
  -n 100 \
  --questions B2 B3 B6 B7 B11 \
  --concepts-per-resp 3 \
  --seed 42 \
  -o data/test_run.xlsx
```

---

## Understanding the Output

### Excel File Structure

**Columns:**
```
SERIAL          - Respondent ID (P00001, P00002, etc.)
DATE            - Generation timestamp
Gender          - Male/Female
(SEX) SEX       - Gender code
AGE             - Numeric age
(AGEQUOTA)      - Age band (18-35, 36-55, 56-75)
(OCCUPATION)    - Occupation category

For each concept answered (3 concepts × N questions):
Concept 1: (PRPURINT) PRICED PURCHASE INTENT
Concept 1: (UNIQNESS) UNIQUENESS
Concept 1: (LIKBILTY) LIKEABILITY
... etc ...

Concept 2: (PRPURINT) PRICED PURCHASE INTENT
... etc ...
```

**Response format:**
```
(1) Definitely would not
(2) Probably would not
(3) Might or might not
(4) Probably would
(5) Definitely would
```

### Metadata JSON

**Contains:**
```json
{
  "generation_timestamp": "2024-12-10T12:52:43",
  "n_respondents": 50,
  "n_concepts": 8,
  "concepts_per_respondent": 3,
  "questions_asked": ["B2", "B3", "B6"],
  "random_seed": 42,
  "valid_respondents": 50,
  "screened_respondents": 0,
  "models": {
    "llm": "gpt-4o",
    "embedding": "text-embedding-3-small",
    "temperature": 0.5
  }
}
```

---

## Recommended Workflow for Production

### Phase 1: Validation (Day 1)
```bash
# 1. Small test
python run_full_pipeline.py -n 10 --questions B2 B3 B6

# 2. Medium validation run
python run_full_pipeline.py -n 50

# 3. Check metrics
jupyter notebook notebooks/07_validation_and_comparison.ipynb
```

### Phase 2: Refinement (Day 1-2)
```bash
# 4. Identify poor-performing questions from validation

# 5. Refine anchors in src/scales/registry.py

# 6. Re-validate with small sample
python run_full_pipeline.py -n 30

# 7. Check improved metrics
jupyter notebook notebooks/07_validation_and_comparison.ipynb
```

### Phase 3: Production (Day 2-3)
```bash
# 8. Full generation (match ground truth N=400)
python run_full_pipeline.py -n 400

# 9. Final validation
jupyter notebook notebooks/07_validation_and_comparison.ipynb

# 10. Document results and metrics
```

**Total time:** 2-3 days including iteration

---

## Troubleshooting

### Error: "No module named..."
```bash
# Reinstall dependencies
uv pip install -r requirements.txt
```

### Error: "OpenAI API key not found"
```bash
# Check .env file exists
cat .env

# Should show: OPENAI_API_KEY=sk-...
# If not, create it:
echo "OPENAI_API_KEY=sk-your-actual-key" > .env
```

### Error: "Concepts file not found"
```bash
# Parse concepts first
python -c "
from src.parsers.concept_parser import ConceptParser
import json
from pathlib import Path

Path('data/parsed').mkdir(parents=True, exist_ok=True)

parser = ConceptParser('source docs/Tech_Enabled_CZ_Concepts_EN.pptx')
concepts = parser.parse()

with open('data/parsed/concepts.json', 'w') as f:
    json.dump([{
        'id': c.id, 'name': c.name, 'description': c.description,
        'full_text': c.full_text, 'price': c.price,
        'occasion': c.occasion, 'features': c.features
    } for c in concepts], f, indent=2)

print('✓ Concepts parsed')
"
```

### Error: "Rate limit exceeded"
```bash
# OpenAI rate limit hit - wait a few minutes and retry
# Or reduce batch size:
python run_full_pipeline.py -n 10  # Instead of 100
```

### Synthetic data looks wrong
```bash
# Check a few rows manually
python -c "
import pandas as pd
df = pd.read_excel('data/synthetic/synthetic_data_*.xlsx')
print(df.head())
print(df.columns.tolist())
"
```

---

## Quick Reference Card

| Task | Command |
|------|---------|
| **Parse concepts** | `python -c "from src.parsers.concept_parser import ConceptParser; ..."` |
| **Quick test (10 resp)** | `python run_full_pipeline.py -n 10` |
| **Validation run (50)** | `python run_full_pipeline.py -n 50` |
| **Production (400)** | `python run_full_pipeline.py -n 400` |
| **Specific questions** | `python run_full_pipeline.py -n 50 --questions B2 B3 B6` |
| **Validate results** | `jupyter notebook notebooks/07_validation_and_comparison.ipynb` |
| **Check output** | `python -c "import pandas as pd; df = pd.read_excel('data/synthetic/synthetic_data_*.xlsx'); print(len(df))"` |

---

## Expected Timeline

### Quick Demo (1 hour)
1. Parse concepts (5 min)
2. Generate n=10 (3 min)
3. Review output (2 min)

### Validation Run (Half day)
1. Parse all docs (30 min)
2. Generate n=50 (20 min)
3. Run validation (1 hour)
4. Review metrics (1 hour)

### Production Ready (2-3 days)
1. Day 1: Parse docs, validation run (n=50), identify issues
2. Day 2: Refine anchors, re-validate (n=50), improve metrics
3. Day 3: Production run (n=400), final validation, documentation

---

## Next Steps After Generation

Once you have synthetic data:

1. **Compare distributions** (notebook 07)
2. **Run statistical tests** (KL divergence, correlation)
3. **Identify outliers** (questions with poor match)
4. **Refine anchors** for poorly performing questions
5. **Re-generate** with improved anchors
6. **Final validation** with full dataset
7. **Use synthetic data** for analysis, modeling, testing

---

**Need help?** Check these files:
- `README.md` - System overview
- `QUICKSTART.md` - 5-minute guide
- `TESTING_STATUS.md` - What's been tested
- `CONCEPT_SELECTION_FIX.md` - Recent fixes
- `SYSTEM_VALIDATED.md` - Validation results

**Ready to start?**
```bash
python run_full_pipeline.py -n 10
```
