# Temperature Sweep Experiments

## Overview

This directory contains experiments for optimizing the SSR (Semantic Similarity Rating) temperature parameter to improve distribution matching against ground truth data.

## Temperature Parameter

The **SSR temperature** (τ) controls how probabilities are normalized when rating free-text responses:

- **Lower values (0.5-0.8)**: Sharper, more concentrated distributions
  - Use when synthetic data is too spread out
  - Increases confidence in highest-similarity ratings

- **τ = 1.0**: Default value from research paper
  - Balanced normalization
  - Standard softmax behavior

- **Higher values (1.2-1.5)**: Flatter, more dispersed distributions
  - Use when synthetic data is too concentrated
  - Spreads probability mass more evenly

## Running Temperature Sweep

### Quick Start

```bash
# Run with 30 respondents per temperature (recommended for testing)
python3 experiments/temperature_sweep.py -n 30 --sequential

# Full experiment with 50 respondents per temperature
python3 experiments/temperature_sweep.py -n 50 --sequential
```

### Command Options

```bash
python3 experiments/temperature_sweep.py \
  -n 50 \                          # Respondents per experiment
  --model gpt-4o \                 # LLM model to use
  --parallel 5 \                   # Parallel workers per experiment
  --concepts-per-resp 3 \          # Concepts each respondent evaluates
  --sequential                     # Run experiments one at a time (recommended)
```

### What It Does

The script will:
1. Test 6 temperature values: `[0.5, 0.7, 0.8, 1.0, 1.2, 1.5]`
2. For each temperature:
   - Generate synthetic data with N respondents
   - Run validation against ground truth
   - Collect KL divergence, KS similarity, and correlation metrics
3. Save results to `experiments/results/temperature_sweep_TIMESTAMP.json`
4. Display summary table and recommendations

### Expected Runtime

- **30 respondents × 6 temperatures**: ~1-2 hours
- **50 respondents × 6 temperatures**: ~2-3 hours
- **75 respondents × 6 temperatures**: ~3-4 hours

(Times vary based on API speed and parallel workers)

## Interpreting Results

The sweep will report:

### Key Metrics

1. **Mean KL Divergence** (target: <0.20)
   - Lower is better
   - Measures how well distributions match ground truth
   - <0.05 = Excellent, 0.05-0.10 = Good, 0.10-0.20 = Acceptable

2. **KS Similarity** (target: >0.85)
   - Higher is better
   - 1 - KS Statistic
   - Paper benchmarks: GPT-4o=0.88, Gemini-2f=0.80

3. **Correlation Attainment** (target: >85%)
   - Percentage of human test-retest reliability
   - Paper achieved ~90%

### Example Output

```
Temperature  Success    Mean KL      KS Similarity   Correlation
----------------------------------------------------------------------
0.50         ✓          0.4201       0.6823          0.2145
0.70         ✓          0.3456       0.7312          0.2567
0.80         ✓          0.3201       0.7501          0.2834
1.00         ✓          0.3586       0.7185          0.2751
1.20         ✓          0.3912       0.6934          0.2512
1.50         ✓          0.4567       0.6523          0.2234

RECOMMENDATIONS
================================================================================

Best temperature for KL divergence: 0.8 (KL=0.3201)
Best temperature for KS similarity: 0.8 (KS=0.7501)

✓ Optimal temperature: 0.8
```

## Applying Results

Once you've identified the optimal temperature:

### Method 1: Update config.yaml (Recommended)

```yaml
# SSR (Semantic Similarity Rating) Parameters
ssr:
  temperature: 0.8  # Update this value
```

### Method 2: Use CLI argument

```bash
python3 run_full_pipeline.py -n 75 --temperature 0.8
```

### Method 3: Python API

```python
from src.config import Config

config = Config()
# Pass to QuestionHandler
question_handler = QuestionHandler(
    llm_client,
    rating_engine,
    ssr_temperature=0.8
)
```

## Results Storage

Results are saved in `experiments/results/`:

- `temperature_sweep_TIMESTAMP.json`: Full results with per-question metrics
- Each entry contains:
  - Temperature value
  - Success status
  - Output file path
  - Validation metrics (overall and per-question)

## Troubleshooting

### API Quota Errors

If you see `Error code: 429 - insufficient_quota`:
- Reduce parallel workers: `--parallel 3`
- Reduce respondents: `-n 20`
- Use `--sequential` flag to avoid overwhelming API
- Wait between experiments

### Validation Failures

If validation fails:
- Check that `data/synthetic/` contains output files
- Verify ground truth file exists: `source docs/KAP400232611_Respondent_Data_Tech Enabled CZ.xlsx`
- Run validation manually: `python3 run_validation.py`

## Next Steps After Optimization

1. **Validate with larger sample**:
   ```bash
   python3 run_full_pipeline.py -n 75 --temperature OPTIMAL_VALUE
   python3 run_validation.py
   ```

2. **If results still don't meet targets** (<0.20 KL, >0.85 KS):
   - Consider anchor statement optimization
   - Try context-aware anchors
   - Implement calibration framework
   - See `data/validation/improvement_strategies.md`

3. **Document findings**:
   - Update project README with optimal temperature
   - Note performance improvements
   - Share results with team

## References

- SSR Paper: `source docs/2510.08338v2.pdf`
- Improvement Strategies: `data/validation/improvement_strategies.md`
- Anchor Analysis: `data/validation/anchor_analysis.md`
