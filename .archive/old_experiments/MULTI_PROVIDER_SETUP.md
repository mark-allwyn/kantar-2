# Multi-Provider LLM Setup Guide

Your application now supports both **OpenAI** and **Google Gemini** as LLM providers!

## What's New

### 1. Configuration File (`config.yaml`)

A new YAML configuration file controls which provider and models to use:

```yaml
llm:
  provider: "openai"  # or "gemini"

  openai:
    model: "gpt-4o"
    embedding_model: "text-embedding-3-small"

  gemini:
    model: "gemini-2.0-flash"
    embedding_model: "text-embedding-004"
```

### 2. Updated Components

#### LLM Client (`src/llm/client.py`)
- Auto-detects provider from model name
- Supports both OpenAI and Gemini APIs
- Unified interface regardless of provider

#### Embedding Service (`src/ssr/embeddings.py`)
- Supports embeddings from both providers
- Auto-detects provider from model name
- Handles different embedding dimensions

#### Configuration Loader (`src/config.py`)
- Loads settings from `config.yaml`
- Provides easy access to all configuration

## Usage

### Option 1: Using Config File (Recommended)

1. Edit `config.yaml` to set your preferred provider:
   ```yaml
   llm:
     provider: "gemini"  # Switch to Gemini
   ```

2. Run the pipeline normally:
   ```bash
   python3 run_full_pipeline.py -n 50
   ```

### Option 2: Using Command-Line Arguments

Override config settings with CLI args:

```bash
# Use Gemini with specific model
python3 run_full_pipeline.py -n 50 --provider gemini --model gemini-2.5-pro

# Use OpenAI
python3 run_full_pipeline.py -n 50 --provider openai --model gpt-4o

# Auto-detect from model name
python3 run_full_pipeline.py -n 50 --model gemini-2.0-flash
```

### Option 3: Programmatic Usage

```python
from src.llm.client import LLMClient
from src.ssr.embeddings import EmbeddingService

# OpenAI
llm = LLMClient(model="gpt-4o", provider="openai")
embedder = EmbeddingService(model_id="text-embedding-3-small", provider="openai")

# Gemini
llm = LLMClient(model="gemini-2.0-flash", provider="gemini")
embedder = EmbeddingService(model_id="text-embedding-004", provider="gemini")

# Auto-detect (recommended)
llm = LLMClient(model="gemini-2.0-flash")  # Detects "gemini" provider
embedder = EmbeddingService(model_id="text-embedding-004")  # Detects "gemini" provider
```

## Environment Variables

Make sure your `.env` file contains both API keys:

```env
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
```

## Important Notes

### Gemini API Key Status
⚠️ **Your current Gemini API key was reported as leaked and needs to be replaced.**

To get a new key:
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Update `GEMINI_API_KEY` in your `.env` file

### Available Gemini Models

**Text Generation:**
- `gemini-2.5-pro` - Most capable model
- `gemini-2.0-flash` - Fast, balanced (recommended)
- `gemini-flash-latest` - Always points to latest flash model
- `gemini-pro-latest` - Always points to latest pro model

**Embeddings:**
- `text-embedding-004` - Latest embedding model (768 dimensions)

### Available OpenAI Models

**Text Generation:**
- `gpt-4o` - Most capable
- `gpt-4o-mini` - Fast and cost-effective
- `gpt-4-turbo` - Previous generation

**Embeddings:**
- `text-embedding-3-small` - 1536 dimensions (recommended)
- `text-embedding-3-large` - 3072 dimensions (higher quality)

## Testing

Test both providers:

```bash
python3 test_provider_integration.py
```

Expected output:
- ✓ OpenAI: PASSED
- Gemini: Requires valid API key

## Command-Line Options

```bash
python3 run_full_pipeline.py --help

Options:
  -n, --respondents N       Number of respondents (default: 50)
  --provider {openai,gemini} LLM provider (default: from config)
  --model MODEL             Model name (default: from config)
  --parallel N              Parallel workers (default: 5)
  --config PATH             Path to config.yaml
  --seed N                  Random seed
  --concepts-per-resp N     Concepts per respondent (default: 3)
```

## Architecture

The system maintains a unified interface while supporting multiple providers:

```
┌─────────────────┐
│  Config System  │ ← config.yaml
└────────┬────────┘
         │
         ├──→ LLMClient ──────┬──→ OpenAI API
         │                    └──→ Gemini API
         │
         └──→ EmbeddingService ┬──→ OpenAI Embeddings
                               └──→ Gemini Embeddings
```

## Backward Compatibility

All existing code continues to work:
- Default provider is OpenAI
- CLI args work as before
- No breaking changes

## Troubleshooting

### "API key reported as leaked"
- Get a new Gemini API key from Google AI Studio
- Update `.env` file

### "Model not found"
- Check available models with:
  ```python
  import google.generativeai as genai
  genai.configure(api_key="YOUR_KEY")
  for m in genai.list_models():
      print(m.name)
  ```

### Provider auto-detection issues
- Explicitly set `provider` parameter
- Or ensure model name starts with "gemini" for Gemini models

## Performance Notes

| Provider | Speed | Cost | Quality |
|----------|-------|------|---------|
| OpenAI gpt-4o | Medium | $$$ | Excellent |
| OpenAI gpt-4o-mini | Fast | $ | Very Good |
| Gemini 2.5-pro | Medium | $$ | Excellent |
| Gemini 2.0-flash | Very Fast | $ | Very Good |

For synthetic survey generation, `gemini-2.0-flash` or `gpt-4o-mini` are recommended for best speed/quality balance.
