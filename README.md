# Kantar Synthetic Survey Data Generator

A production-ready Python system for generating synthetic survey respondents using **Semantic Similarity Rating (SSR)** methodology, specifically designed for Kantar survey formats.

## Overview

This system creates high-quality synthetic survey data that mimics real human responses by:
1. Extracting concepts from Kantar PPTX presentations
2. Generating personas with realistic demographics (optionally sampled from ground truth)
3. Using LLMs to generate free-text responses conditioned on persona + concept
4. Mapping responses to rating scales using semantic similarity to anchor statements
5. Formatting output to match exact Kantar Excel template structure
6. Validating synthetic data against ground truth

## Key Features

- **Fully Generalized**: Works with all Kantar survey formats (tested on 5 complete studies)
- **Template-Based**: Automatically matches ground truth Excel column structure
- **Concept Extraction**: Uses GPT-4o to extract concepts from PPTX files
- **Two Generation Modes**: Ground truth mode (with PPTX/Excel) or no-ground-truth mode (test new concepts)
- **Ground Truth Demographics**: Optional flag to sample demographics from real data
- **Market Profiles**: Pre-built demographic profiles (US_gaming, UK_lottery, EU_general, generic)
- **Comprehensive Reporting**: HTML reports with validation metrics and visualizations
- **Robust Matching**: Handles concept name variations across studies (2-24 concepts)
- **Production Ready**: 100% compliance rate across all testable Kantar studies

## Project Structure

```
kantar-replica/
├── src/
│   ├── kantar/              # Kantar-specific modules
│   │   ├── survey_runner.py      # Main entry point for generation
│   │   ├── validation_runner.py  # Validation against ground truth
│   │   ├── study_catalog.py      # Study/market discovery
│   │   ├── concept_extractor.py  # PPTX concept extraction
│   │   ├── data_loader.py        # Ground truth data loading
│   │   ├── column_mapper.py      # Concept-to-column mapping
│   │   └── excel_formatter.py    # Kantar Excel formatting
│   ├── persona/             # Persona generation
│   ├── survey/              # Survey engine
│   ├── ssr/                 # Semantic Similarity Rating
│   ├── llm/                 # LLM client
│   ├── scales/              # Scale registry
│   ├── output/              # Base Excel formatter
│   ├── parsers/             # Document parsers
│   ├── logic/               # Conditional logic
│   └── validation/          # Validation metrics
├── data/
│   ├── kantar-survey-source/  # Ground truth data
│   └── synthetic/kantar/       # Generated synthetic data
├── notebooks/               # Jupyter notebooks (interactive front-end)
│   ├── 01_quick_start.ipynb
│   ├── 02_synthetic_data_generation.ipynb
│   └── 03_validation_and_reporting.ipynb
├── tests/                   # Test files
└── .archive/                # Archived old experiments
```

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up OpenAI API key:**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. **Place Kantar study data** in `data/kantar-survey-source/` with structure:
   ```
   data/kantar-survey-source/
   ├── STUDY_ID/
   │   ├── MARKET_CODE/
   │   │   ├── *.pptx         # Concept presentations
   │   │   └── *.xlsx         # Ground truth data
   ```

## Usage

### Two Modes of Operation

The system supports two modes:
1. **Ground Truth Mode**: Generate data for existing studies with PPTX/Excel files
2. **No Ground Truth Mode**: Test new concepts without any historical data

### Mode 1: Generate from Existing Studies (Ground Truth)

**Basic generation (generic demographics):**
```bash
python -m src.kantar.survey_runner \
  --study 61405445-01 \
  --market US \
  --num-respondents 50 \
  --model gpt-4o-mini
```

**With ground truth demographics:**
```bash
python -m src.kantar.survey_runner \
  --study 61405445-01 \
  --market US \
  --num-respondents 50 \
  --model gpt-4o-mini \
  --use-gt-demographics
```

**Generate for all markets in a study:**
```bash
python -m src.kantar.survey_runner \
  --study 61405445-01 \
  --all-markets \
  --num-respondents 50 \
  --model gpt-4o-mini
```

### Mode 2: Generate from Custom Concepts (No Ground Truth)

Test brand new concepts without needing PPTX files or historical data.

**Step 1: Create a concepts JSON file** (`my_concepts.json`):
```json
[
  {
    "id": "Concept1",
    "name": "Premium Lottery Experience",
    "description": "A new lottery game with enhanced odds and exclusive prizes",
    "price": "$5 per ticket",
    "features": [
      "Enhanced winning odds",
      "Exclusive prize tiers",
      "VIP member benefits"
    ],
    "occasion": "Regular play"
  },
  {
    "id": "Concept2",
    "name": "Quick Pick Plus",
    "description": "Instant lottery with AI-powered number selection",
    "price": "$2 per ticket",
    "features": [
      "AI number selection",
      "Instant results",
      "Mobile-first experience"
    ]
  }
]
```

**Step 2: Generate survey data:**
```bash
python -m src.kantar.survey_runner \
  --concepts-file my_concepts.json \
  --num-respondents 100 \
  --market-profile US_gaming \
  --model gpt-4o-mini
```

**List available market profiles:**
```bash
python -m src.kantar.survey_runner --list-profiles
```

Available profiles:
- `US_gaming` - United States iGaming market
- `UK_lottery` - United Kingdom National Lottery market
- `EU_general` - General European Union market
- `generic` - Default profile (works for any market)

### Validate and Generate Reports

**Run validation:**
```bash
python -m src.kantar.validation_runner \
  --study 61405445-01 \
  --market US \
  --synthetic data/synthetic/kantar/61405445-01/US/synthetic_US_50resp_*.xlsx
```

**Validation with HTML report:**
```bash
python -m src.kantar.validation_runner \
  --study 61405445-01 \
  --market US \
  --synthetic data/synthetic/*.xlsx \
  --generate-report
```

The report includes:
- Quality scores and status (PASS/WARNING/FAIL)
- Validation metrics (KL divergence, KS similarity, correlation)
- Top issues requiring attention
- Visualization dashboards
- Question-level details

### Interactive Notebooks (Recommended for Getting Started)

For a more interactive experience, use the Jupyter notebooks:

```bash
# Install Jupyter (if not already installed)
pip install jupyter

# Launch Jupyter
jupyter notebook

# Open notebooks in order:
# 1. notebooks/01_quick_start.ipynb
# 2. notebooks/02_synthetic_data_generation.ipynb
# 3. notebooks/03_validation_and_reporting.ipynb
```

**Notebooks include:**
- 📓 **Quick Start**: Introduction, environment setup, small test generation
- 📓 **Generation**: Both ground truth and no-ground-truth modes with examples
- 📓 **Validation**: Run validation, generate reports, analyze metrics

See `notebooks/README.md` for detailed notebook documentation.

### Python API

**Ground Truth Mode:**
```python
from src.kantar.survey_runner import KantarSurveyRunner

# Initialize runner
runner = KantarSurveyRunner(model="gpt-4o-mini")

# Generate for a specific market
output_file = runner.generate_for_market(
    study_id="61405445-01",
    market_code="US",
    num_respondents=50,
    use_ground_truth_demographics=True
)

print(f"Generated: {output_file}")
```

**No Ground Truth Mode:**
```python
from src.kantar.survey_runner import KantarSurveyRunner
from pathlib import Path

# Define new concepts
concepts = [
    {
        'id': 'NewConcept1',
        'name': 'Revolutionary Product',
        'description': 'A brand new concept without any historical data',
        'price': '$15',
        'features': ['Feature A', 'Feature B', 'Feature C'],
        'occasion': 'Special occasions'
    },
    {
        'id': 'NewConcept2',
        'name': 'Premium Service',
        'description': 'Enhanced lottery experience for VIP members',
        'price': '$25',
        'features': ['VIP access', 'Better odds', 'Exclusive prizes']
    }
]

# Initialize runner
runner = KantarSurveyRunner(model="gpt-4o-mini")

# Generate survey data
output_file = runner.generate_from_concepts(
    concepts=concepts,
    num_respondents=100,
    market_profile='US_gaming',  # or 'UK_lottery', 'EU_general', 'generic'
    output_dir=Path('output/my_concepts')
)

print(f"Generated: {output_file}")
```

## System Capabilities

### Tested Studies (100% Compliance)

| Study ID | Name | Markets | Concepts | Status |
|----------|------|---------|----------|--------|
| 61405445-01 | iGaming Concept Evaluate | 5 | 5 | ✅ COMPLIANT |
| 61407017 | 24 Ideas Screening | 3 | 24 | ✅ COMPLIANT |
| 61407069 | Tech-Enabled ScratchCards | 4 | 8 | ✅ COMPLIANT |
| 61407185 | Innovation Concepts | 3 | 8 | ✅ COMPLIANT |
| 61407240 | Thunderball Concept | 5 | 2 | ✅ COMPLIANT |

**Total Coverage:**
- 5/5 testable studies = **100% compliance**
- 20 complete markets tested
- Handles 2-24 concepts per study
- Adapts to 71-227 column templates

### Question Types Supported

All Kantar standard questions work out of the box:
- Purchase Intent (UNPURINT, PRPURINT)
- Uniqueness (UNIQNESS)
- Price Comparison (UNPRICEP)
- Likeability (LIKBILTY)
- Incrementality (INCREMNT)
- Relevance (RELVANCE)
- Playfulness (PLAYFLNS)
- Excitement (EXCITMENT)
- Believability (BELVBLTY)
- Likes/Dislikes
- Barriers, Occasions, Gift questions

## Semantic Similarity Rating (SSR)

The core methodology:
1. **Free-text elicitation**: LLM generates natural language response
2. **Anchor statements**: 5-9 canonical statements per scale level
3. **Embedding**: Convert response + anchors to vectors (text-embedding-3-small)
4. **Similarity**: Compute cosine similarity
5. **Normalization**: Softmax to probability distribution
6. **Selection**: Choose level with highest probability

### Why SSR?

- Achieves 90% correlation attainment vs human test-retest reliability
- Outperforms direct Likert rating from LLMs
- Captures nuanced opinions that map to scales
- More realistic than forced scale selection

## Validation Metrics

The system validates synthetic data against ground truth using:
- **KL Divergence**: Distribution similarity (lower = better)
- **KS Statistic**: Kolmogorov-Smirnov test
- **Correlation**: Pearson correlation on question means
- **MAE**: Mean absolute error
- **Chi-square**: Categorical distribution tests

## Configuration Options

### Demographics Modes

1. **Generic (default)**: Uses predefined demographic distributions
2. **Ground Truth (--use-gt-demographics)**: Samples from actual survey demographics
   - Gender distribution from GT
   - Age distribution from GT
   - Occupation distribution from GT
   - Category/brand buyers from GT

### Model Options

- **gpt-4o-mini**: Fast, cost-effective (recommended for large-scale)
- **gpt-4o**: Higher quality, slower
- **gpt-4-turbo**: Balance of speed and quality

### Output

Generated files:
- `synthetic_MARKET_Nresp_TIMESTAMP.xlsx` - Synthetic data in Kantar format
- `metadata_MARKET_TIMESTAMP.json` - Generation metadata

## Architecture

### Key Design Decisions

1. **Template-Based Formatting**: System loads ground truth Excel as template, ensuring exact column order/naming
2. **Concept Filtering**: Automatically filters "Codes -" prefix to match question columns
3. **Dynamic Column Detection**: Handles varying column counts (71-227) across studies
4. **Reusable Questions**: Same question logic across all studies (only concepts vary)
5. **Cached Concept Extraction**: Concepts cached per market to avoid re-extraction

### Data Flow

```
PPTX → Concept Extraction (GPT-4o) → Cached JSON
   ↓
Ground Truth Excel → Demographics + Template
   ↓
Persona Generation (with optional GT demographics)
   ↓
Survey Engine → Question Handler → LLM + SSR
   ↓
Kantar Excel Formatter → Exact GT column structure
   ↓
Validation Runner → Metrics vs Ground Truth
```

## Documentation

- **README.md**: This file - complete system overview
- **notebooks/README.md**: Jupyter notebooks documentation
- **KANTAR_SYSTEM_COMPLIANCE.md**: Detailed compliance testing results
- **QUESTION_REFERENCE.md**: Question ID to Kantar mapping

## Development Status

### ✅ Completed (Production Ready)
- Full Kantar integration for all 7 survey formats
- Two generation modes: ground truth + no-ground-truth
- Market demographic profiles (US_gaming, UK_lottery, EU_general, generic)
- Concept extraction from PPTX (GPT-4o)
- Ground truth data loading and analysis
- Concept-to-column name matching (handles variations)
- Template-based Excel formatting
- All question types implemented
- Persona generation (generic + GT demographics)
- SSR engine with all scales
- Validation metrics (KL divergence, KS statistic, correlation)
- HTML reporting with visualizations
- Interactive Jupyter notebooks
- CLI tools for generation and validation
- Python API

### 🎯 Future Enhancements
- Response distribution sampling from GT (beyond demographics)
- Market-specific psychographic patterns
- Multi-language support
- Batch processing optimization
- Web UI for generation
- PDF report generation

## Methodology Reference

Based on research: "Using LLMs for Market Research"
- SSR achieves 90% correlation attainment
- Demographic conditioning critical
- Validated across multiple question types

## License

Internal project for Kantar market research.

## Contact

For questions or issues, contact the project maintainer.
