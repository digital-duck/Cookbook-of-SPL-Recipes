# ch03-2: Tree of Thought

Explores three independent reasoning paths in parallel, scores each, selects the best, refines it, and verifies the result. Falls back to synthesizing all paths if verification fails.

## Pattern

```
approach_1/2/3(problem)
  └─► develop each path
        └─► evaluate_path (score A/B/C)
              └─► select_best → refine_solution → verify
                    ├─ sound      → COMMIT complete
                    └─ unsound    → synthesize_all → COMMIT synthesized
```

## Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `problem` | TEXT | *(required)* | The problem or decision to explore |

## Usage

```bash
# Local Ollama
spl run src/recipes/ch03-2-tree-of-thought/tree_of_thought.spl --adapter ollama \
    problem="Should we rewrite the legacy system or incrementally refactor?"

spl run src/recipes/ch03-2-tree-of-thought/tree_of_thought.spl --adapter ollama \
    problem="Design a caching strategy for a high-traffic API"

spl run src/recipes/ch03-2-tree-of-thought/tree_of_thought.spl --adapter ollama -m llama3.2 \
    problem="How should a startup prioritize between growth and profitability?"

# Momagrid
spl run src/recipes/ch03-2-tree-of-thought/tree_of_thought.spl --adapter momagrid \
    problem="Should we rewrite the legacy system or incrementally refactor?"

spl run src/recipes/ch03-2-tree-of-thought/tree_of_thought.spl --adapter momagrid \
    problem="Design a caching strategy for a high-traffic API"

spl run src/recipes/ch03-2-tree-of-thought/tree_of_thought.spl --adapter momagrid -m llama3.2 \
    problem="How should a startup prioritize between growth and profitability?"
```

## Output status

| Status | Meaning |
|---|---|
| `complete` | Best path verified as sound |
| `synthesized` | Verification failed; all paths merged |
| `budget_limit` | Budget exceeded; best scored path returned |
