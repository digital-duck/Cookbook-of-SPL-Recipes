# ch03-1: Chain of Thought

Multi-step reasoning pipeline: Research → Analyze → Summarize. Each step feeds its output into the next, building progressively refined understanding.

## Pattern

```
research(topic) → @research
  └─► analyze(@research) → @analysis
        └─► summarize(@analysis) → @summary
```

## Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `topic` | TEXT | *(required)* | The topic to research, analyze, and summarize |

## Usage

```bash
# Local Ollama
spl run src/recipes/ch03-1-chain-of-thought/chain.spl --adapter ollama \
    topic="distributed AI inference"

spl run src/recipes/ch03-1-chain-of-thought/chain.spl --adapter ollama -m llama3.2 \
    topic="quantum computing"

spl run src/recipes/ch03-1-chain-of-thought/chain.spl --adapter ollama \
    topic="the history of the microprocessor" \
    2>&1 | tee src/recipes/ch03-1-chain-of-thought/out/09_chain_of_thought-$(date +%Y%m%d_%H%M%S).md

# Momagrid
spl run src/recipes/ch03-1-chain-of-thought/chain.spl --adapter momagrid \
    topic="distributed AI inference"

spl run src/recipes/ch03-1-chain-of-thought/chain.spl --adapter momagrid -m llama3.2 \
    topic="quantum computing"

spl run src/recipes/ch03-1-chain-of-thought/chain.spl --adapter momagrid \
    topic="the history of the microprocessor" \
    2>&1 | tee src/recipes/ch03-1-chain-of-thought/out/09_chain_of_thought-momagrid-$(date +%Y%m%d_%H%M%S).md
```
