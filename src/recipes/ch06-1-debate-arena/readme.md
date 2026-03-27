# ch06-1: Debate Arena

Two LLM personas argue opposing sides of a topic over multiple rebuttal rounds, then a judge picks the winner. Demonstrates adversarial generation and semantic evaluation.

## Pattern

```
pro_argument(topic, opening)  ──┐
con_argument(topic, opening)  ──┘
    └─► rebuttal rounds (x3)
          └─► judge_debate(topic, pro_history, con_history) → verdict
```

## Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `topic` | TEXT | *(required)* | The debate motion (e.g. "AI should be open-sourced") |
| `max_rounds` | INTEGER | `3` | Number of rebuttal rounds before the judge rules |

## Usage

```bash
# Local Ollama
spl run src/recipes/ch06-1-debate-arena/debate.spl --adapter ollama \
    topic="AI should be open-sourced"

spl run src/recipes/ch06-1-debate-arena/debate.spl --adapter ollama -m llama3.2 \
    topic="Remote work is better than office work"

spl run src/recipes/ch06-1-debate-arena/debate.spl --adapter ollama \
    topic="Tabs are better than spaces"

# Momagrid
spl run src/recipes/ch06-1-debate-arena/debate.spl --adapter momagrid \
    topic="AI should be open-sourced"

spl run src/recipes/ch06-1-debate-arena/debate.spl --adapter momagrid -m llama3.2 \
    topic="Remote work is better than office work"

spl run src/recipes/ch06-1-debate-arena/debate.spl --adapter momagrid \
    topic="Tabs are better than spaces"
```

## Output status

| Status | Meaning |
|---|---|
| `complete` | All rounds completed, verdict rendered |
| `partial` | Max iterations hit; judge called early |
| `budget_limit` | Token budget exceeded; pro history returned |
