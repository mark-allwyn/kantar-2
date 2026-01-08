# Kantar Integration Status

## Completed Modules ✅

### 1. Study Catalog (`src/kantar/study_catalog.py`)
- **Status**: Complete and tested
- **Functionality**:
  - Scans `data/kantar-survey-source/` for studies and markets
  - Indexes 7 studies with 20 complete markets total
  - Provides API for accessing study/market files
- **Usage**:
  ```python
  from src.kantar.study_catalog import StudyCatalog
  catalog = StudyCatalog()
  study = catalog.get_study('61405445-01')  # iGaming study
  market = study.get_market('US')
  pptx_path = catalog.get_concept_presentation_path('61405445-01', 'US')
  excel_path = catalog.get_ground_truth_path('61405445-01', 'US')
  ```

### 2. Data Loader (`src/kantar/data_loader.py`)
- **Status**: Complete and tested
- **Functionality**:
  - Loads ground truth Excel files
  - Analyzes column structure (demographics, questions, metadata)
  - Extracts concept names from columns
  - Detects scale types from response values
- **Key Findings**:
  - iGaming US: 250 respondents, 10 concepts, 75 question columns
  - Column format: `"(UNPURINT) UNPRICED PURCHASE INTENT - US Pulse Play  "`
  - 5-point Likert scales with format: `"(4) Probably would"`
- **Usage**:
  ```python
  from src.kantar.data_loader import GroundTruthLoader
  loader = GroundTruthLoader()
  data = loader.load(excel_path)
  print(f"Concepts: {data.concept_names}")
  print(f"Respondents: {data.respondent_count}")
  ```

### 3. Concept Extractor (`src/kantar/concept_extractor.py`)
- **Status**: Complete and tested
- **Functionality**:
  - LLM-based extraction from PPTX presentations
  - Extracts: name, description, features, price, occasion
  - Caches results as JSON for reuse
  - Uses GPT-4o with structured prompts
- **Test Results**:
  - iGaming US: Extracted 5 concepts successfully
  - Cached to: `data/kantar-survey-source/.../concepts.json`
- **Usage**:
  ```python
  from src.kantar.concept_extractor import ConceptExtractor
  extractor = ConceptExtractor()
  concepts = extractor.extract_from_pptx(pptx_path)
  # First run: calls LLM
  # Subsequent runs: loads from cache
  ```

### 4. Column Mapper (`src/kantar/column_mapper.py`)
- **Status**: Complete and tested
- **Functionality**:
  - Maps system question IDs to Kantar format
  - Builds Kantar-format column names
  - Matches extracted concepts to ground truth names
  - Handles variations (e.g., "Pulse Play" -> "US Pulse Play")
- **Usage**:
  ```python
  from src.kantar.column_mapper import ColumnMapper
  mapper = ColumnMapper()
  col_name = mapper.build_kantar_column_name('UNPURINT', 'US Pulse Play')
  # Returns: "(UNPURINT) UNPRICED PURCHASE INTENT - US Pulse Play  "

  concept_map = mapper.match_concept_names(extracted_concepts, gt_concepts)
  # Returns: {'Pulse Play': 'US Pulse Play', ...}
  ```

---

## Remaining Work 🚧

### 5. Excel Formatter Enhancement
**File**: `src/output/excel_formatter.py` (update existing)
**Goal**: Add `KantarExcelFormatter` class that:
- Accepts ground truth Excel as template
- Matches exact column order and naming
- Preserves metadata columns
- Uses `ColumnMapper` to generate correct names

**Key Methods**:
```python
class KantarExcelFormatter:
    def __init__(self, template_path: Path, concept_mapping: Dict[str, str]):
        # Load template structure
        # Store concept mapping from extractor

    def format_respondent_data(self, respondents: List[RespondentData]) -> pd.DataFrame:
        # Convert to DataFrame matching template
        # Use column_mapper for naming

    def save_to_excel(self, output_path: Path):
        # Write with exact template format
```

### 6. Survey Runner
**File**: `src/kantar/survey_runner.py`
**Goal**: Orchestrate survey generation for Kantar markets

**Key Functions**:
```python
def generate_for_market(
    study_id: str,
    market_code: str,
    num_respondents: Optional[int] = None,
    model: str = "gpt-4o-mini"
) -> Path:
    """
    Generate synthetic data for a specific market.

    Steps:
    1. Load concepts from PPTX (via concept_extractor)
    2. Load ground truth for demographics (via data_loader)
    3. Match concept names (via column_mapper)
    4. Generate respondents (via existing survey_engine)
    5. Format output (via KantarExcelFormatter)
    6. Save to data/synthetic/kantar/{study}/{market}/

    Returns: Path to generated Excel file
    """

def generate_for_study(study_id: str) -> Dict[str, Path]:
    """Generate for all markets in parallel"""
```

### 7. Validation Runner
**File**: `src/kantar/validation_runner.py`
**Goal**: Run validation for markets/studies

**Key Functions**:
```python
def validate_market(
    study_id: str,
    market_code: str,
    synthetic_path: Path,
    ground_truth_path: Path
) -> Dict:
    """
    Validate one market.

    Returns metrics dict:
    {
        'market': 'US',
        'kl_divergence': 0.15,
        'ks_similarity': 0.87,
        'correlation_attainment': 0.92,
        'question_metrics': {...},
        'concept_metrics': {...}
    }
    """

def validate_study(study_id: str) -> Dict:
    """
    Validate all markets in study.

    Returns aggregated metrics:
    {
        'study_id': '61405445-01',
        'markets': {...},
        'aggregate': {
            'mean_kl': 0.16,
            'mean_ks': 0.86,
            ...
        }
    }
    """
```

### 8. Market Report Generator
**File**: `src/kantar/reports/market_report.py`
**Goal**: Generate HTML report for single market

**Content**:
- Header: Study, market, respondent count
- Summary metrics: KL, KS, correlation
- Question breakdown table
- Distribution plots (plotly)
- Concept analysis
- Export as HTML + JSON

### 9. Study Report Generator
**File**: `src/kantar/reports/study_report.py`
**Goal**: Generate aggregated study report

**Content**:
- Cross-market comparison table
- Aggregate metrics
- Best/worst markets
- Question performance heatmap
- Trends and insights

### 10. Dashboard Generator
**File**: `src/kantar/reports/dashboard_generator.py`
**Goal**: Interactive HTML dashboard

**Features**:
- Study selector
- Market drill-down
- Question comparison across markets
- Interactive plotly charts
- Export/download functionality

### 11. CLI Entry Point
**File**: `run_kantar_pipeline.py`
**Goal**: Command-line interface

**Usage**:
```bash
# Generate synthetic data for one market
python run_kantar_pipeline.py generate --study 61405445-01 --market US

# Generate for all markets
python run_kantar_pipeline.py generate --study 61405445-01 --all-markets

# Validate (assumes synthetic data exists)
python run_kantar_pipeline.py validate --study 61405445-01 --market US

# Generate + validate + report
python run_kantar_pipeline.py run --study 61405445-01 --all-markets

# Generate report only from cached metrics
python run_kantar_pipeline.py report --study 61405445-01
```

**Arguments**:
- `--study`: Study ID (e.g., '61405445-01')
- `--market`: Market code (e.g., 'US') or --all-markets
- `--model`: LLM model (default: gpt-4o-mini)
- `--num-respondents`: Override respondent count
- `--output-dir`: Custom output directory
- `--report-only`: Skip generation/validation, just generate reports

---

## Implementation Priority

### Phase 1: Core Pipeline (Essential)
1. **KantarExcelFormatter** - Required for output
2. **SurveyRunner** - Required for generation
3. **ValidationRunner** - Required for validation
4. **CLI Entry Point** - Required for usability

### Phase 2: Reporting (Important)
5. **MarketReport** - Individual market results
6. **StudyReport** - Aggregated results
7. **Dashboard** - Interactive exploration

### Test with Pilot:
- Study: 61405445-01 (iGaming)
- Market: US (250 respondents, 5 concepts)
- Expected: Generate synthetic data matching ground truth format

---

## Key Design Decisions

### 1. Questions are Shared
- **Implication**: Reuse existing question handlers and scale mappings
- **Benefit**: No need for dynamic schema detection
- **Only varies**: Concept names and their count per study

### 2. LLM-Based Concept Extraction
- **Benefit**: Handles varying PPTX formats
- **Cost**: ~$0.01 per market (cached after first run)
- **Alternative**: Manual JSON creation if budget constrained

### 3. Template-Based Output
- **Benefit**: Exact format match with ground truth
- **Implementation**: Load template, map columns, fill data

### 4. Reports Structure
```
reports/kantar/
└── {study_id}/
    ├── index.html              # Dashboard
    ├── study_metrics.json
    └── markets/
        ├── {market}/
        │   ├── report.html
        │   ├── metrics.json
        │   └── plots/
        └── ...
```

---

## Next Steps

1. **Implement Excel Formatter**:
   - Create `KantarExcelFormatter` class
   - Test with dummy data
   - Verify column matching

2. **Implement Survey Runner**:
   - Integrate: catalog + extractor + loader + formatter
   - Test single market generation
   - Verify output format matches template

3. **Implement Validation Runner**:
   - Reuse existing validation metrics
   - Add market/study aggregation
   - Generate metrics JSON

4. **Create CLI**:
   - argparse for commands
   - Progress logging
   - Error handling

5. **Test Pilot** (iGaming US):
   ```bash
   python run_kantar_pipeline.py run --study 61405445-01 --market US
   ```
   - Expected: Synthetic Excel + validation report

6. **Scale to Full Study**:
   ```bash
   python run_kantar_pipeline.py run --study 61405445-01 --all-markets
   ```
   - Expected: 5 markets validated with study dashboard

7. **Reporting**:
   - Implement market reports
   - Implement study aggregation
   - Implement interactive dashboard

---

## Success Metrics

- ✅ Catalog discovers 7 studies, 20 complete markets
- ✅ Concepts extracted from PPTX (5 from iGaming US)
- ✅ Ground truth loaded (250 respondents, 10 concepts, 75 questions)
- ✅ Column mapping works (matched 3/3 test concepts)
- 🚧 Synthetic data generated in exact Kantar format
- 🚧 Validation metrics: KL < 0.20, KS > 0.85
- 🚧 Individual market reports generated
- 🚧 Study-level dashboard created
- 🚧 CLI runs end-to-end for pilot study

---

## Current File Structure

```
src/kantar/
├── __init__.py                     ✅
├── study_catalog.py                ✅ Complete
├── data_loader.py                  ✅ Complete
├── concept_extractor.py            ✅ Complete
├── column_mapper.py                ✅ Complete
├── survey_runner.py                🚧 TODO
├── validation_runner.py            🚧 TODO
└── reports/
    ├── __init__.py                 ✅
    ├── market_report.py            🚧 TODO
    ├── study_report.py             🚧 TODO
    └── dashboard_generator.py      🚧 TODO

run_kantar_pipeline.py              🚧 TODO
```

---

## Testing Commands

```bash
# Test existing modules
python src/kantar/study_catalog.py
python -m src.kantar.data_loader
python -m src.kantar.concept_extractor
python -m src.kantar.column_mapper

# Future testing
python run_kantar_pipeline.py generate --study 61405445-01 --market US
python run_kantar_pipeline.py validate --study 61405445-01 --market US
python run_kantar_pipeline.py run --study 61405445-01 --all-markets
```
