# Kantar Synthetic Survey Notebooks

Interactive Jupyter notebooks for using the Kantar synthetic survey system.

## Available Notebooks

### 01_quick_start.ipynb
**Quick introduction to the system**
- Environment setup and configuration
- Explore available studies and market profiles
- Generate a small test dataset (5 respondents)
- Preview generated data

**Use this when**: You're new to the system and want to understand the basics

---

### 02_synthetic_data_generation.ipynb
**Complete guide to data generation**
- **Mode 1: Ground Truth Generation** - Generate from existing studies with PPTX/Excel files
- **Mode 2: No-Ground-Truth Generation** - Test new concepts without historical data
- Configure demographics (GT sampling vs market profiles)
- Define custom concepts
- Generate production-scale datasets
- Save concepts for reuse

**Use this when**: You need to generate synthetic survey data for analysis

---

### 03_validation_and_reporting.ipynb
**Validation and quality assessment**
- Run validation against ground truth
- Generate HTML reports with visualizations
- Analyze question-level metrics (KL divergence, KS statistic, correlation)
- Interpret quality scores
- Compare multiple validation runs
- Track improvements over time

**Use this when**: You want to validate synthetic data quality and generate reports

---

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r ../requirements.txt
   pip install jupyter
   ```

2. **Set environment variables:**
   ```bash
   export OPENAI_API_KEY="your-api-key"
   ```

3. **Launch Jupyter:**
   ```bash
   jupyter notebook
   ```

4. **Start with notebook 01** - Quick Start

## Workflow

```
01_quick_start.ipynb
    ↓
    Understand system basics
    ↓
02_synthetic_data_generation.ipynb
    ↓
    Generate synthetic data (ground truth or new concepts)
    ↓
03_validation_and_reporting.ipynb
    ↓
    Validate quality and generate reports
```

## CLI Alternative

If you prefer command-line tools:

```bash
# Generate synthetic data
python -m src.kantar.survey_runner \
  --study 61405445-01 \
  --market US \
  --num-respondents 50 \
  --model gpt-4o-mini

# Validate and generate report
python -m src.kantar.validation_runner \
  --study 61405445-01 \
  --market US \
  --synthetic data/synthetic/*.xlsx \
  --generate-report
```

See main README.md for full CLI documentation.

## Archive

Old notebooks from previous system versions are in `.archive/` for reference. These are outdated and incompatible with the current system.

## Support

- Main documentation: `../README.md`
- System compliance: `../KANTAR_SYSTEM_COMPLIANCE.md`
- Question reference: `../QUESTION_REFERENCE.md`
