# ch01-4: Few-Shot Prompting

Embed gold-standard examples in `SELECT` context to guide output format and style — no fine-tuning required.

## Key Feature

`CREATE FUNCTION` returns domain-specific examples as a `TEXT` value. The `SELECT` includes them as `examples` alongside the input, and `GENERATE` uses both to produce consistently formatted output.

## Usage

```bash
# General sentiment + summary
# Local Ollama
spl run src/recipes/ch01-4-few-shot-learning/few_shot.spl --adapter ollama -m gemma3 \
    text="The quarterly results exceeded all analyst forecasts by a significant margin"

# Momagrid
spl run src/recipes/ch01-4-few-shot-learning/few_shot.spl --adapter momagrid -m gemma3 \
    text="The quarterly results exceeded all analyst forecasts by a significant margin"

# Finance domain
# Local Ollama
spl run src/recipes/ch01-4-few-shot-learning/few_shot.spl --adapter ollama \
    text="Revenue grew 12% YoY despite headwinds in APAC" domain="finance"

# Momagrid
spl run src/recipes/ch01-4-few-shot-learning/few_shot.spl --adapter momagrid \
    text="Revenue grew 12% YoY despite headwinds in APAC" domain="finance"

# Ops/incident triage
# Local Ollama
spl run src/recipes/ch01-4-few-shot-learning/few_shot.spl --adapter ollama \
    text="System outage detected in EU-WEST-2 affecting 15% of users" domain="ops"

# Momagrid
spl run src/recipes/ch01-4-few-shot-learning/few_shot.spl --adapter momagrid \
    text="System outage detected in EU-WEST-2 affecting 15% of users" domain="ops"
```

## Why few-shot in SELECT

- Examples are version-controlled with the `.spl` file
- Domain parameter makes the example set swappable without touching the prompt logic
- Same pattern works for any output format: JSON, YAML, markdown tables, code
