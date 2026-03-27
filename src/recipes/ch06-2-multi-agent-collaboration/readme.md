# ch06-2: Multi-Agent Collaboration

Three specialized agents collaborate via `CALL`: a Researcher gathers facts, an Analyst identifies trends and risks, a Writer produces the polished report.

## Pattern

```
CALL researcher(@topic)            → @research
  └─► CALL analyst(@research, @topic)  → @analysis
        └─► CALL writer(@research, @analysis, @topic) → @report
```

## Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `topic` | TEXT | *(required)* | The subject for the collaborative report |

## Usage

```bash
# Local Ollama
spl run src/recipes/ch06-2-multi-agent-collaboration/multi_agent.spl --adapter ollama \
    topic="Future of renewable energy" \
    2>&1 | tee src/recipes/ch06-2-multi-agent-collaboration/out/14_multi_agent-$(date +%Y%m%d_%H%M%S).md

spl run src/recipes/ch06-2-multi-agent-collaboration/multi_agent.spl --adapter ollama \
    topic="Impact of AI on healthcare"

spl run src/recipes/ch06-2-multi-agent-collaboration/multi_agent.spl --adapter ollama -m llama3.2 \
    topic="State of quantum computing in 2025"

# Momagrid
spl run src/recipes/ch06-2-multi-agent-collaboration/multi_agent.spl --adapter momagrid \
    topic="Future of renewable energy" \
    2>&1 | tee src/recipes/ch06-2-multi-agent-collaboration/out/14_multi_agent-momagrid-$(date +%Y%m%d_%H%M%S).md

spl run src/recipes/ch06-2-multi-agent-collaboration/multi_agent.spl --adapter momagrid \
    topic="Impact of AI on healthcare"

spl run src/recipes/ch06-2-multi-agent-collaboration/multi_agent.spl --adapter momagrid -m llama3.2 \
    topic="State of quantum computing in 2025"
```

## Output status

| Status | Meaning |
|---|---|
| `complete` | All three agents finished successfully |
| `partial_research_only` | Budget exceeded after research phase |
| `restarted` | Hallucination detected; retried at lower temperature |
