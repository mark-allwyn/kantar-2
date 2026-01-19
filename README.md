# S.A.G.E – Synthetic Audience Generation Engine

A production-ready Python system for generating synthetic survey respondents using **Semantic Similarity Rating (SSR)** methodology, designed for market research survey formats.

> **S.A.G.E** uses LLMs combined with semantic similarity to generate statistically realistic survey responses that match real human data distributions.

## Overview

This system creates high-quality synthetic survey data that statistically matches real human responses by:

1. **Extracting concepts** from Kantar PPTX presentations
2. **Sampling demographics** from ground truth distributions
3. **Generating personas** with realistic demographic profiles
4. **Using LLMs** to generate free-text responses conditioned on persona + concept
5. **Mapping responses** to rating scales using semantic similarity to anchor statements
6. **Validating output** against ground truth using KL divergence and KS statistics

### Key Results (January 2026)

| Metric | Target | Achieved |
|--------|--------|----------|
| KS Similarity (Demographics) | >85% | **90-98%** |
| KS Similarity (Full Survey) | >85% | 75-82% |
| Question Coverage | 100% | 100% |
| Multi-market Support | Yes | US, UK, CZ, AT, GR |

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install CLI tool
pip install -e .

# Set up OpenAI API key
export OPENAI_API_KEY="your-api-key-here"
```

### 2. List Available Studies

```bash
python3 -m src.cli.main study list --complete-only
```

### 3. Generate Synthetic Data

```bash
# Generate 50 respondents for a study/market
python3 -m src.cli.main generate study 61405445-01 US -n 50

# With checkpointing (resume if interrupted)
python3 -m src.cli.main generate study 61405445-01 US -n 50 --checkpoint-every 10

# Resume interrupted generation
python3 -m src.cli.main generate study 61405445-01 US -n 50 --resume
```

### 4. Validate Results

```bash
# Validate against ground truth
python3 -m src.cli.main validate study 61405445-01 US

# Generate HTML report
python3 -m src.cli.main validate study 61405445-01 US --report
```

### 5. View Output

```bash
# Synthetic data (Kantar Excel format)
ls data/synthetic/kantar/61405445-01/US/*.xlsx

# Validation results (JSON)
ls data/synthetic/kantar/61405445-01/US/validation_*.json
```

## Project Structure

```
sage/
├── src/                          # Source code
│   ├── cli/                      # Command-line interface
│   ├── kantar/                   # Kantar-specific modules
│   │   ├── survey_runner.py      # Main generation entry point
│   │   ├── validation_runner.py  # Validation against ground truth
│   │   ├── study_catalog.py      # Study/market discovery
│   │   ├── concept_extractor.py  # PPTX concept extraction
│   │   ├── excel_formatter.py    # Kantar Excel formatting
│   │   └── checkpoint_manager.py # Resume capability
│   ├── ssr/                      # Semantic Similarity Rating engine
│   ├── llm/                      # LLM client and prompts
│   ├── persona/                  # Persona generation
│   ├── scales/                   # Scale definitions and anchors
│   ├── survey/                   # Survey engine
│   └── validation/               # Validation metrics
├── data/
│   ├── kantar-survey-source/     # Ground truth data (not in repo)
│   └── synthetic/kantar/         # Generated synthetic data
├── docs/                         # Documentation
│   ├── technical/                # System specs and tuning
│   ├── validation/               # Validation reports
│   └── reference/                # Question reference
├── notebooks/                    # Jupyter notebooks
├── scripts/                      # Utility scripts
├── reports/                      # Generated reports
├── tests/                        # Test files
└── config/                       # Configuration files
```

## CLI Reference

### Study Management

```bash
# List all studies
python3 -m src.cli.main study list

# List only complete studies
python3 -m src.cli.main study list --complete-only

# Show study details
python3 -m src.cli.main study info 61405445-01

# Verify study structure
python3 -m src.cli.main study verify 61405445-01 --verbose
```

### Generation

```bash
# Generate from existing study
python3 -m src.cli.main generate study STUDY_ID MARKET -n RESPONDENTS

# Options:
#   -n, --respondents     Number of respondents (required)
#   --use-gt-demographics Sample demographics from ground truth (default: True)
#   --model              LLM model (default: gpt-4o-mini)
#   --checkpoint-every   Save checkpoint every N respondents (default: 10)
#   --resume             Resume from checkpoint if available

# Generate from custom concepts (no ground truth)
python3 -m src.cli.main generate custom concepts.json -n 100 --profile US_gaming
```

### Validation

```bash
# Validate study
python3 -m src.cli.main validate study STUDY_ID MARKET

# Options:
#   --synthetic    Path to synthetic file (auto-detect if omitted)
#   --report       Generate HTML validation report
#   --report-format  html or json (default: html)
```

### Market Profiles

```bash
# List available profiles
python3 -m src.cli.main profile list
```

Available profiles: `US_gaming`, `UK_lottery`, `EU_general`, `generic`

## Methodology

### Semantic Similarity Rating (SSR)

The system implements SSR methodology from *"LLMs Reproduce Human Purchase Intent via Semantic Similarity Elicitation of Likert Ratings"* (arXiv:2510.08338v2).

**How it works:**

1. **Generate Response**: LLM generates natural language answer to survey question
2. **Embed**: Response embedded using `text-embedding-3-small`
3. **Compare**: Cosine similarity computed against anchor texts for each scale level
4. **Normalize**: Similarities converted to probability distribution
5. **Average**: Process repeated with 6 reference sets, PMFs averaged
6. **Select**: Final rating selected via sampling

**Configuration:**
- Normalization: Linear (per paper Equation 8)
- Temperature: 1.0
- Selection: Sample (preserves variance)
- Reference Sets: 6

### Ground Truth Demographics Sampling

When validating, the system samples synthetic persona demographics from the ground truth distribution. This ensures:

- Identical demographic profile to real respondents
- Fair comparison for attitudinal questions
- High demographic similarity scores (95-100%)

The true test of the system is performance on attitudinal questions (Purchase Intent, Likeability, etc.) where the LLM must generate realistic responses.

## Validation Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **KL Divergence** | Distribution similarity (lower = better) | < 0.20 |
| **KS Statistic** | Maximum CDF difference (lower = better) | < 0.15 |
| **KS Similarity** | 1 - KS Statistic (higher = better) | > 85% |

## Validated Studies

| Study ID | Name | Markets | Status |
|----------|------|---------|--------|
| 61405445-01 | iGaming Concept Evaluate | US, UK, AT, CZ, GR | Validated |
| 61407017 | 24 Ideas Screening | US, UK, CZ | Validated |
| 61407069 | Tech-Enabled ScratchCards | US, AT, CZ, GR | Validated |
| 61407185 | Innovation Concepts 2025 | US, UK, CZ | Validated |
| 61407240 | Thunderball Concept | UK, AT, CZ, GR | Validated |

## Question Types Supported

- **Purchase Intent** (UNPURINT) - 5-point Likert
- **Uniqueness** (UNIQNESS) - 5-point Likert
- **Price Comparison** (UNPRICEP) - 5-point Likert
- **Likeability** (LIKBILTY) - 6-point Likert
- **Relevance** (RELVANCE) - 5-point Likert
- **Excitement** (EXCITMENT) - 4-point Likert
- **Believability** (BELVBLTY) - 4-point Likert
- **Likes/Dislikes** (LIKES_STD) - Open text
- Plus: Incrementality, Playfulness, Gift questions, Barriers, Occasions

## API Costs

| Component | Model | Cost per 50 Respondents |
|-----------|-------|------------------------|
| Response Generation | GPT-4o-mini | ~$1.50 |
| Embeddings | text-embedding-3-small | ~$0.10 |
| Concept Extraction | GPT-4o | ~$0.50 (one-time) |
| **Total** | | **~$2.10** |

## Performance

- **Generation Speed**: ~100-130 seconds per respondent
- **50 Respondents**: ~1.5 hours
- **Checkpoint Frequency**: Every 10 respondents (configurable)
- **Resume Capability**: Automatic

## Documentation

- **[docs/technical/](docs/technical/)** - System specifications, tuning guide
- **[docs/validation/](docs/validation/)** - Validation reports and templates
- **[docs/reference/](docs/reference/)** - Question reference, cost models
- **[notebooks/](notebooks/)** - Interactive Jupyter notebooks
- **[reports/](reports/)** - Generated analysis reports

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Project Dependencies

See `requirements.txt` for full list. Key dependencies:
- `openai` - LLM API
- `pandas` - Data manipulation
- `openpyxl` - Excel file handling
- `numpy` - Numerical operations
- `click` - CLI framework
- `tqdm` - Progress bars

## License

Internal project for Kantar market research.

## Contact

For questions or issues, contact the project maintainer.
