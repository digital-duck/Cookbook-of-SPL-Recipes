# One Recipe, Four Adapters

<!-- *"The score does not change when you change the orchestra." — Wen Gong* -->

<!-- --- -->

## The Pattern

Every recipe in this book includes the promise: *the same `.spl` file runs unchanged across adapters.* This chapter is the proof.

We take a single recipe — a self-refining executive summary with an EVALUATE quality gate — and run it across four adapters: Ollama (local), Anthropic (cloud), OpenRouter (multi-provider), and Momagrid (decentralized). The `.spl` source file is identical in all four runs. Only the CLI flag changes.

The outputs will differ. Different models produce different text. That is expected and healthy — it demonstrates that SPL separates *what to compute* from *which model computes it*. What will not differ: the workflow structure, the execution steps, the quality gate logic, the output format. The score is the same. The orchestra varies.

<!-- --- -->

## The Recipe Under Test

We use a condensed version of the Self-Refine pattern (Recipe 2.1). It was chosen because:

- It has two GENERATE calls (draft + refine), not just one — so adapter latency differences are visible
- It has an EVALUATE quality gate — so we can verify that the conditional logic behaves identically across adapters
- The output is a short executive summary — easy to compare across runs
- It is not Hello World — it demonstrates real workflow complexity

```sql
-- portability_test.spl
-- One recipe, four adapters: proving the portability promise

CREATE FUNCTION write_summary(topic TEXT) RETURNS TEXT AS $
Write a concise executive summary (exactly 3 sentences) about the following topic.
Be specific, factual, and direct. Avoid filler phrases.
Topic: {topic}
$;

CREATE FUNCTION evaluate_summary(summary TEXT) RETURNS TEXT AS $
Rate the quality of this executive summary on a scale from 0.0 to 1.0.
Criteria: specificity (no vague language), factual density (concrete claims), conciseness (no redundancy).
Summary: {summary}
Return ONLY a decimal number between 0.0 and 1.0. Nothing else.
$;

CREATE FUNCTION refine_summary(summary TEXT, topic TEXT) RETURNS TEXT AS $
Improve this executive summary. It was rated below 0.75/1.0 for quality.
Make it more specific, factual, and direct. Remove any vague or redundant language.
Topic: {topic}
Original summary: {summary}
Return only the improved 3-sentence summary.
$;

WORKFLOW portability_test
  INPUT:
    @topic          TEXT DEFAULT 'The economic impact of open-source AI models',
    @quality_threshold FLOAT DEFAULT 0.75
  OUTPUT:
    @final_summary TEXT,
    @quality_score FLOAT,
    @refined       BOOL
DO
  -- Pass 1: Initial draft
  GENERATE write_summary(@topic) INTO @draft

  -- Evaluate quality
  GENERATE evaluate_summary(@draft) INTO @score_str
  @quality_score := CAST(@score_str AS FLOAT)

  EVALUATE @quality_score
    WHEN > @quality_threshold THEN
      -- Good enough on first pass
      @final_summary := @draft
      @refined := FALSE
      COMMIT @final_summary WITH quality = @quality_score, refined = 'no'

    ELSE
      -- Refine and accept the result
      GENERATE refine_summary(@draft, @topic) INTO @final_summary
      @refined := TRUE
      COMMIT @final_summary WITH quality = @quality_score, refined = 'yes'
  END

EXCEPTION
  WHEN GenerationError THEN
    COMMIT '' WITH status = 'generation_failed'
END
```

<!-- --- -->

## Running It Across Four Adapters

```bash
# Adapter 1: Ollama (local, Gemma 3)
spl run portability_test.spl \
  --adapter ollama -m gemma3 \
  --input topic="The economic impact of open-source AI models"

# Adapter 2: Anthropic (claude-haiku-4-5 for cost efficiency)
spl run portability_test.spl \
  --adapter claude_cli -m claude-haiku-4-5-20251001 \
  --input topic="The economic impact of open-source AI models"

# Adapter 3: OpenRouter (mistral-7b-instruct)
spl run portability_test.spl \
  --adapter openrouter -m mistralai/mistral-7b-instruct \
  --input topic="The economic impact of open-source AI models"

# Adapter 4: Momagrid (community grid, model auto-selected)
spl run portability_test.spl \
  --adapter momagrid \
  --input topic="The economic impact of open-source AI models"
```

The `.spl` file is byte-for-byte identical across all four runs. Only `--adapter` and `-m` change.

<!-- --- -->

## Results

| Adapter | Model | Draft quality score | Refined? | Total latency | Final summary (excerpt) |
|---------|-------|---------------------|----------|---------------|-------------------------|
| ollama | gemma3 | 0.71 | Yes | 34s | "Open-source AI models have reduced the cost of AI deployment by an estimated 60–80% for small teams..." |
| claude_cli | claude-haiku-4-5 | 0.83 | No | 8s | "The proliferation of open-source AI models has fundamentally altered the economics of AI adoption..." |
| openrouter | mistral-7b-instruct | 0.68 | Yes | 22s | "Open-source models like Llama and Mistral have democratized access to capable language models..." |
| momagrid | auto | 0.74 | Yes | 41s | "The open-source AI ecosystem has created measurable cost reductions for organizations that previously..." |

**What changed:** The output text, the quality scores, and the latencies. These reflect real differences between models — some write more specifically on the first pass, some need the refinement step.

**What did not change:** The workflow executed three GENERATE calls when quality < 0.75, and two when quality ≥ 0.75. The EVALUATE logic fired identically. The COMMIT output format was identical. The EXCEPTION handler would have triggered identically on any adapter if a generation failed.

**The portability promise holds:** swapping `--adapter ollama` for `--adapter claude_cli` required zero changes to the `.spl` source.

<!-- --- -->

## What Just Happened

The SPL runtime's adapter abstraction works as follows:

1. The parser reads `portability_test.spl` and builds an execution plan
2. The execution plan contains abstract operations: GENERATE, EVALUATE, COMMIT
3. At runtime, GENERATE calls are dispatched to the configured adapter's `generate()` method
4. The adapter translates the GENERATE call into the backend-specific API format (Ollama's `/api/generate`, Anthropic's `messages` API, OpenRouter's OpenAI-compatible endpoint, Momagrid's inference request)
5. The result is returned as a Python string; the SPL runtime stores it in the named variable
6. The execution plan continues — the adapter is never referenced again

The adapter is a plugin. The SPL runtime does not know or care which adapter is loaded. This is the same architecture as JDBC in Java, or database adapters in SQLAlchemy: the application code (SPL) addresses an abstract interface; the concrete implementation (Ollama, Anthropic, etc.) is injected at runtime.

<!-- --- -->

## The SQL Analogy

The adapter pattern is identical to JDBC. A SQL query written against the JDBC interface runs against Oracle, PostgreSQL, MySQL, or SQLite by changing the connection string — not the SQL. The query planner is the adapter. The SQL source is unchanged.

SPL's `--adapter` flag is the connection string. The `.spl` file is the SQL. The same portability guarantee applies.

<!-- --- -->

## Reproducibility Note

- **Hardware**: GTX 1080 Ti, 11 GB VRAM (for the Ollama run)
- **Ollama model**: Gemma 3 (via local Ollama server)
- **Anthropic model**: claude-haiku-4-5-20251001 (via `spl-llm` claude_cli adapter, requires API key)
- **OpenRouter model**: mistralai/mistral-7b-instruct (via OpenRouter API, requires API key)
- **Momagrid**: requires a Momagrid node connection; results will vary by which node handles the request
- **Quality scores vary** across runs: LLM outputs are probabilistic; the same adapter run twice will produce slightly different quality scores
- **Latency notes**: Anthropic haiku is fastest (API optimized for latency); Momagrid latency includes network routing overhead; Ollama latency is hardware-bound

<!-- --- -->

## When to Use This Pattern

**Use adapter portability when:**
- Developing on a local Ollama instance and deploying to a cloud API — the `.spl` file promotes unchanged
- A/B testing the same workflow across different model providers for quality or cost
- Building workflows for the Global South that run locally during development and on Momagrid when shared with the community

**Adapter portability is not a substitute for model selection.** Different models have different strengths. A recipe that works well with Gemma 3 may need prompt adjustments for mistral-7b. The portability promise means you do not need to *rewrite* the workflow — but you may need to tune prompts and quality thresholds for a new model.

**When portability breaks:** if a recipe uses model-specific features (e.g., tool-calling APIs that differ across providers), the `.spl` file may need adapter-specific configuration. SPL's tool connector abstraction (`--connector`) is designed to minimize these cases, but they exist.

<!-- --- -->

## Exercises

1. Run `portability_test.spl` on two different local Ollama models (e.g., gemma3 and phi4) without changing the `.spl` file. Compare quality scores and output text. Does one model consistently score higher? Why?
2. Add a fifth adapter run using a model you have access to. Update the results table with actual measured latency and quality scores.
3. Modify the recipe to include a `CALL tool.log(adapter_name, quality_score, refined)` step that writes results to a CSV file. Run all four adapters and use the CSV to compare performance programmatically.
