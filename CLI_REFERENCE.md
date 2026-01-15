# Kantar Synthetic CLI Reference

Unified production command-line interface for synthetic survey data generation and validation.

## Installation

```bash
# Install in development mode
pip3 install -e .

# Verify installation
python3 -m src.cli.main --version
```

## Quick Start

```bash
# List available studies
python3 -m src.cli.main study list

# Verify a study before generation
python3 -m src.cli.main study verify 61405445-01

# Generate 50 respondents with defaults
python3 -m src.cli.main quick-gen 61405445-01 US

# Validate latest generation
python3 -m src.cli.main quick-validate 61405445-01 US
```

## Commands

### Generation Commands

#### Generate from Study (Ground Truth Mode)

```bash
python3 -m src.cli.main generate study STUDY_ID MARKET [OPTIONS]
```

**Options:**
- `-n, --respondents INTEGER` - Number of respondents (required)
- `--use-gt-demographics` - Sample demographics from ground truth (default: True)
- `--model TEXT` - LLM model to use (default: gpt-4o-mini)
- `--verify-first` - Verify study structure before generating
- `--checkpoint-every INTEGER` - Save checkpoint every N respondents (default: 10)
- `--output-dir PATH` - Custom output directory

**Examples:**
```bash
# Generate 50 respondents for study 61405445-01, US market
python3 -m src.cli.main generate study 61405445-01 US -n 50

# Generate 100 respondents with GPT-4
python3 -m src.cli.main generate study 61407017 UK -n 100 --model gpt-4o

# Verify first, then generate
python3 -m src.cli.main generate study 61407069 US -n 50 --verify-first
```

#### Generate from Custom Concepts (No Ground Truth)

```bash
python3 -m src.cli.main generate custom CONCEPTS_FILE [OPTIONS]
```

**Options:**
- `-n, --respondents INTEGER` - Number of respondents (required)
- `--profile TEXT` - Market profile (US_gaming, UK_lottery, EU_general, generic)
- `--model TEXT` - LLM model to use (default: gpt-4o-mini)
- `--output-dir PATH` - Custom output directory
- `--output-name TEXT` - Output file name prefix
- `--validate-concepts` - Validate concept schema before generating

**Examples:**
```bash
# Generate 100 respondents with US gaming profile
python3 -m src.cli.main generate custom concepts.json -n 100 --profile US_gaming

# Generate with validation and custom name
python3 -m src.cli.main generate custom my_concepts.json -n 50 \
  --validate-concepts --output-name test_run
```

#### Quick Generate (Simplified)

```bash
python3 -m src.cli.main quick-gen STUDY_ID [MARKET] [OPTIONS]
```

Generates 50 respondents using ground truth demographics and gpt-4o-mini.

**Options:**
- `-n, --respondents INTEGER` - Number of respondents (default: 50)
- `--verify-first` - Verify study structure first

**Examples:**
```bash
# Quick 50-respondent generation
python3 -m src.cli.main quick-gen 61405445-01 US

# Quick 100-respondent generation with verification
python3 -m src.cli.main quick-gen 61407017 UK --respondents 100 --verify-first
```

### Validation Commands

#### Validate Study

```bash
python3 -m src.cli.main validate study STUDY_ID MARKET [OPTIONS]
```

**Options:**
- `--synthetic PATH` - Path to synthetic Excel file (auto-detect if omitted)
- `--ground-truth PATH` - Path to ground truth Excel file (auto-discover if omitted)
- `--report` - Generate HTML validation report
- `--report-format [html|json]` - Report format (default: html)
- `--output-dir PATH` - Custom output directory for reports

**Examples:**
```bash
# Validate with auto-detection
python3 -m src.cli.main validate study 61405445-01 US

# Validate and generate HTML report
python3 -m src.cli.main validate study 61407017 UK --report

# Validate specific file
python3 -m src.cli.main validate study 61405445-01 US \
  --synthetic path/to/synthetic.xlsx
```

#### Quick Validate (Simplified)

```bash
python3 -m src.cli.main quick-validate STUDY_ID [MARKET] [OPTIONS]
```

Auto-detects latest synthetic file and runs validation.

**Options:**
- `--report` - Generate HTML report

**Examples:**
```bash
# Quick validation
python3 -m src.cli.main quick-validate 61405445-01 US

# Quick validation with report
python3 -m src.cli.main quick-validate 61407017 UK --report
```

### Study Management Commands

#### List Studies

```bash
python3 -m src.cli.main study list [OPTIONS]
```

**Options:**
- `--format [table|json|simple]` - Output format (default: table)
- `--complete-only` - Show only complete studies

**Examples:**
```bash
# List all studies in table format
python3 -m src.cli.main study list

# List only complete studies
python3 -m src.cli.main study list --complete-only

# List in JSON format
python3 -m src.cli.main study list --format json
```

#### Study Information

```bash
python3 -m src.cli.main study info STUDY_ID
```

Shows detailed information about a specific study including markets, file locations, and completion status.

**Example:**
```bash
python3 -m src.cli.main study info 61405445-01
```

#### Verify Study

```bash
python3 -m src.cli.main study verify STUDY_ID [OPTIONS]
```

**Options:**
- `-v, --verbose` - Show detailed verification output

Checks folder structure, file presence, and readiness for generation.

**Examples:**
```bash
# Basic verification
python3 -m src.cli.main study verify 61405445-01

# Detailed verification
python3 -m src.cli.main study verify 61407017 --verbose
```

### Profile Management Commands

#### List Profiles

```bash
python3 -m src.cli.main profile list [OPTIONS]
```

**Options:**
- `--format [table|simple]` - Output format (default: table)

Lists available market demographic profiles.

**Example:**
```bash
python3 -m src.cli.main profile list
```

#### Show Profile

```bash
python3 -m src.cli.main profile show PROFILE_NAME
```

Shows detailed information about a specific profile including demographics configuration.

**Example:**
```bash
python3 -m src.cli.main profile show US_gaming
```

## Adding a New Kantar Study

### Manual Process (Current)

1. **Create folder structure:**
```bash
data/kantar-survey-source/
└── STUDY_ID_QN_Study Name/
    ├── US/
    │   ├── concepts.pptx      # Concept presentation
    │   └── ground_truth.xlsx  # Ground truth data
    ├── UK/
    │   ├── concepts.pptx
    │   └── ground_truth.xlsx
    └── ...
```

2. **Verify structure:**
```bash
python3 -m src.cli.main study verify NEW_STUDY_ID --verbose
```

3. **Test with small sample:**
```bash
python3 -m src.cli.main quick-gen NEW_STUDY_ID US -n 5
```

4. **Full generation:**
```bash
python3 -m src.cli.main generate study NEW_STUDY_ID US -n 50
```

### Required File Structure

**PowerPoint File (.pptx):**
- Contains concept descriptions
- One concept per slide recommended
- System will extract concepts automatically using GPT-4o

**Excel File (.xlsx):**
- Ground truth survey responses
- Must contain demographic columns
- Must contain question columns with format: `(QUESTION_CODE) Question Name - Concept Name`

## Concept JSON Schema

For custom generation mode, concepts must follow this schema:

```json
[
  {
    "id": "C1",                     // Required: Unique identifier
    "name": "Concept Name",          // Required: Display name
    "description": "Full description", // Required: Detailed description
    "price": "$5.00",                // Optional: Price information
    "features": [                    // Optional: List of features
      "Feature 1",
      "Feature 2"
    ],
    "occasion": "Usage occasion",    // Optional: When/where to use
    "full_text": "Complete text"    // Optional: Full marketing copy
  }
]
```

**Validation:**
```bash
# Validate concepts before generation
python3 -m src.cli.main generate custom concepts.json -n 50 --validate-concepts
```

## Market Profiles

Available profiles for custom generation:

- **US_gaming** - US iGaming demographic distribution
- **UK_lottery** - UK lottery player demographics
- **EU_general** - General European market demographics
- **generic** - Generic/default demographics

View profile details:
```bash
python3 -m src.cli.main profile show US_gaming
```

## Common Workflows

### Workflow 1: Generate and Validate New Study

```bash
# 1. Verify study structure
python3 -m src.cli.main study verify 61405445-01 --verbose

# 2. Generate 50 respondents
python3 -m src.cli.main quick-gen 61405445-01 US

# 3. Validate results
python3 -m src.cli.main quick-validate 61405445-01 US --report
```

### Workflow 2: Custom Concept Testing

```bash
# 1. Create concepts.json file
cat > concepts.json << 'EOF'
[
  {
    "id": "C1",
    "name": "Premium Lottery",
    "description": "A lottery with enhanced odds and bigger prizes"
  }
]
EOF

# 2. Validate and generate
python3 -m src.cli.main generate custom concepts.json -n 100 \
  --profile US_gaming --validate-concepts
```

### Workflow 3: Batch Generation for All Markets

```bash
# Generate for each market
for market in US UK CZ; do
  python3 -m src.cli.main quick-gen 61405445-01 $market
done

# Validate all
for market in US UK CZ; do
  python3 -m src.cli.main quick-validate 61405445-01 $market
done
```

## Output Files

### Generation Output

**Synthetic Data:**
- Location: `data/synthetic/kantar/STUDY_ID/MARKET/`
- Format: `synthetic_MARKET_NNresp_TIMESTAMP.xlsx`
- Contains: All respondent data in Kantar format

**Metadata:**
- Location: Same directory as synthetic data
- Format: `metadata_MARKET_TIMESTAMP.json`
- Contains: Generation configuration, timestamps, concept info

### Validation Output

**Validation Results:**
- Location: Same directory as synthetic data
- Format: `validation_MARKET_TIMESTAMP.json`
- Contains: KL divergence, KS statistics, correlation metrics

**Reports (optional):**
- Format: HTML or JSON
- Contains: Visualizations, detailed metrics, success criteria

## Troubleshooting

### Common Issues

**Study Not Found:**
```
✗ Study not found: STUDY_ID
```
**Solution:** Check study folder exists in `data/kantar-survey-source/` with correct naming pattern.

**No Synthetic Files:**
```
✗ No synthetic Excel files found
```
**Solution:** Run generation first before validation.

**Module Not Found:**
```
ModuleNotFoundError: No module named 'src'
```
**Solution:** Run from project root directory: `python3 -m src.cli.main ...`

### Getting Help

```bash
# General help
python3 -m src.cli.main --help

# Command-specific help
python3 -m src.cli.main generate --help
python3 -m src.cli.main validate --help
python3 -m src.cli.main study --help
```

## Version Information

**CLI Version:** 1.0.0
**Python Required:** >=3.8
**Key Dependencies:** Click, tqdm, tabulate, pandas, openai

Check version:
```bash
python3 -m src.cli.main --version
```

## Future Enhancements

Planned features for future releases:

- **Cost Estimation** - Show estimated API costs before generation
- **Budget Controls** - Set spending limits
- **Progress Bars** - Real-time progress indicators with ETA
- **Checkpoint/Resume** - Resume failed generations
- **Study Scaffolding** - Automated study folder creation
- **Advanced Validation** - Custom thresholds, multiple report formats
- **Batch Operations** - Generate multiple studies in parallel

## Support

For issues or questions:
1. Check this CLI reference
2. Review example workflows above
3. Check `BASELINE_TRACKING.md` for configuration history
4. Review validation results in JSON output files
