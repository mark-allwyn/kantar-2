# Synthetic Survey Respondent System

A Python system for generating synthetic survey respondents using **Semantic Similarity Rating (SSR)** methodology based on the research paper "Using LLMs for Market Research".

## Overview

This system creates synthetic respondents that mimic real human survey responses by:
1. Generating personas with realistic demographic and psychographic attributes
2. Using GPT-4o to generate free-text responses conditioned on persona characteristics
3. Mapping responses to rating scales using semantic similarity to anchor statements
4. Validating synthetic data against ground truth using KL divergence, KS statistics, and correlation metrics

## Project Structure

```
kantar-test/
├── src/                    # Python backend modules
│   ├── parsers/           # Document parsing (DOCX, PPTX, Excel)
│   ├── logic/             # Conditional logic engine
│   ├── scales/            # Scale registry and SSR scales
│   ├── ssr/               # Semantic Similarity Rating engine
│   ├── persona/           # Persona generation
│   ├── llm/               # LLM client and prompts
│   ├── survey/            # Survey orchestration (to be implemented)
│   ├── output/            # Excel formatting (to be implemented)
│   ├── validation/        # Validation metrics
│   └── visualization/     # Comparison plots
├── notebooks/             # Jupyter notebooks for interactive use
├── data/                  # Data storage
│   ├── parsed/           # Parsed questionnaire/concept data
│   ├── synthetic/        # Generated synthetic datasets
│   └── validation/       # Validation results
├── config/               # Configuration files
├── source docs/          # Original survey documents
├── requirements.txt      # Python dependencies
└── README.md
```

## Installation

1. **Clone or navigate to the project directory**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up OpenAI API key:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

4. **Copy configuration:**
   ```bash
   cp config/config.example.yaml config/config.yaml
   # Edit config.yaml as needed
   ```

## Usage

### Jupyter Notebooks (Recommended for Development)

The system is designed to be used interactively through Jupyter notebooks:

1. **01_data_extraction.ipynb** - Parse questionnaire, concepts, and analyze ground truth data
2. **02_scale_and_anchor_setup.ipynb** - Define scales and test SSR with sample responses
3. **03_persona_testing.ipynb** - Test persona generation and validate demographics
4. **04_single_response_testing.ipynb** - Test LLM + SSR pipeline on single question
5. **05_conditional_logic_testing.ipynb** - Test survey flow and skip patterns
6. **06_full_generation.ipynb** - Generate complete synthetic dataset
7. **07_validation_and_comparison.ipynb** - Validate and visualize results

### Python API

You can also use the modules programmatically:

```python
from src.persona.generator import PersonaGenerator
from src.llm.client import LLMClient
from src.llm.prompts import PromptBuilder
from src.ssr.embeddings import EmbeddingService
from src.ssr.rating_engine import RatingEngine
from src.scales.registry import create_default_scales

# Create components
persona_gen = PersonaGenerator(random_seed=42)
llm_client = LLMClient(model="gpt-4o", temperature=0.5)
embedding_service = EmbeddingService(model_id="text-embedding-3-small")
scale_registry = create_default_scales()
rating_engine = RatingEngine(scale_registry, embedding_service)

# Generate persona
persona = persona_gen.generate_persona()

# Generate response
system_prompt = PromptBuilder.build_system_prompt(persona)
user_prompt = PromptBuilder.build_purchase_intent_prompt(concept_description)
response_text = llm_client.generate_response(system_prompt, user_prompt)

# Rate using SSR
result = rating_engine.rate_answer(
    response_text,
    scale_id="likert5_purchase_intent_v1",
    temperature=0.5
)

print(f"Rating: {result.to_formatted_response()}")
print(f"Probabilities: {result.probabilities}")
```

## Key Components

### Semantic Similarity Rating (SSR)

The core methodology:
- **Free-text elicitation**: LLM generates natural language response
- **Anchor statements**: 5-9 canonical statements per scale level
- **Embedding**: Convert response + anchors to vectors
- **Similarity**: Compute cosine similarity
- **Normalization**: Convert to probability distribution via softmax
- **Selection**: Choose level with highest probability

### Scales Defined

- **5-point Likert**: Purchase Intent, Uniqueness, Value, Relevance, Playfulness, Gift Intent, Gift Satisfaction
- **6-point Likert**: Likeability
- **4-point Likert**: Excitement, Believability
- **9-point Slider**: Understanding
- **7-point Slider**: Inertia
- **Binary**: Incrementality

### Validation Metrics

- **KL Divergence**: Measures distribution difference (lower = better, 0 = identical)
- **JS Divergence**: Symmetric version of KL
- **KS Statistic**: Kolmogorov-Smirnov test
- **Correlation**: Pearson correlation on means
- **Correlation Attainment**: % of human test-retest reliability (target: >85%)
- **MAE**: Mean absolute error on means
- **Chi-square**: Test for categorical distributions

## Configuration

Edit `config/config.yaml` to customize:
- Model selection (GPT-4o, embedding model)
- SSR parameters (temperature, normalization method)
- Persona generation settings
- File paths
- Questions to implement

## Data Sources

Place these files in `source docs/`:
- **Board games_questionnaire EN MASTER.docx** - Survey questionnaire
- **Tech_Enabled_CZ_Concepts_EN.pptx** - 8 product concepts
- **KAP400232611_Respondent_Data_Tech Enabled CZ.xlsx** - Ground truth data

## Methodology Reference

Based on the paper: "Using LLMs for Market Research"
- Achieves 90% correlation attainment vs human test-retest reliability
- Semantic similarity rating outperforms direct Likert rating
- Demographic conditioning critical for performance

## Development Status

### ✅ Completed
- Project structure and dependencies
- Document parsers (questionnaire, concepts, data analyzer)
- Conditional logic engine
- Scale registry with all question types
- SSR engine (embeddings, similarity, rating)
- Persona generator with demographics/psychographics
- LLM client and prompt templates
- Validation metrics (KL, KS, correlation, etc.)
- Comparison visualization

### 🚧 To Implement
- Question handlers for all question types
- Survey engine orchestration
- Excel output formatter
- Full end-to-end pipeline
- Jupyter notebooks (7 total)
- Multi-coded question handling
- Open-ended question processing

## License

Internal project for Kantar market research.

## Contact

For questions or issues, contact the project maintainer.
