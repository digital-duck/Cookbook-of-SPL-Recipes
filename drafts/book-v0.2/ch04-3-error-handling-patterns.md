# Error Handling Patterns

<!-- *"A workflow that cannot fail gracefully is not production-ready. It is a prototype with a production URL." — Wen Gong* -->

<!-- --- -->

## The Pattern

Every earlier recipe in this book either succeeded cleanly or was cut short by an exception. This chapter reverses that perspective: instead of treating exceptions as edge cases, it treats them as first-class design decisions. In production, the exception paths matter as much as the happy path.

SPL provides a structured exception system modelled on SQL's `BEGIN...EXCEPTION...END` (PL/SQL, PostgreSQL) and Python's `try...except`. But LLM workflows face failure modes that have no SQL analog: a model that refuses to answer, a context window that fills up mid-loop, a budget that runs out at step 4 of 6, a generation that produces plausible-sounding but invalid output. This recipe maps the full exception landscape and shows how to handle each type.

<!-- --- -->

## Who This Chapter Is For

**If you are a SQL practitioner:** you already understand transaction semantics — a failed constraint rolls back the INSERT, and you handle it explicitly. SPL exceptions are the same idea applied to LLM calls. The vocabulary differs but the principle is identical: name the failure, handle it specifically, commit a meaningful result even when the happy path fails.

**If you are building production workflows:** this chapter is the difference between a demo and a system. Every workflow you deploy should have an `EXCEPTION` block that specifies, for each likely failure type, what the system should do and what it should commit as evidence of the failure.

<!-- --- -->

## The SPL Exception System

Every `WORKFLOW` can include an `EXCEPTION` block following the `DO` body:

```spl
WORKFLOW my_workflow
    INPUT: @input TEXT
    OUTPUT: @result TEXT
DO
    -- happy path steps
    GENERATE process(@input) INTO @result
    COMMIT @result WITH status = 'complete'

EXCEPTION
    WHEN GenerationError THEN
        COMMIT 'Generation failed.' WITH status = 'error', input = @input
    WHEN MaxIterationsReached THEN
        COMMIT @result WITH status = 'partial'
    WHEN BudgetExceeded THEN
        COMMIT @result WITH status = 'budget_limit'
END
```

The `EXCEPTION` block catches named exception types and routes each to a specific recovery action. A `COMMIT` inside an exception handler is a partial commit: it records what was produced before the failure, along with diagnostic metadata. This is the most important pattern in this chapter — **always commit something meaningful from every exception handler**.

<!-- --- -->

## Exception Type Reference

| Exception Type | Trigger | Recommended Response |
|---|---|---|
| `GenerationError` | Model call failed (network, quota, refusal, malformed response) | Commit last valid state with `status = 'error'` |
| `MaxIterationsReached` | `WHILE` loop exceeded its iteration limit | Commit best-effort result with `status = 'partial'` |
| `BudgetExceeded` | Token budget exhausted mid-workflow | Commit what was generated so far; do not attempt more LLM calls |
| `ContextLengthExceeded` | Input to a GENERATE step exceeds the model's context window | Truncate and retry with a shorter context, or commit partial result |
| `HallucinationDetected` | LLM-as-judge flagged the output as containing hallucinated content | Retry with stricter instructions, or escalate with `status = 'flagged'` |
| `ValidationError` | A `CALL` to a validation tool returned a failure | Retry with corrected input, or commit with `status = 'invalid'` |
| `TimeoutError` | A GENERATE step exceeded the configured timeout | Commit partial result; log for investigation |

<!-- --- -->

## Pattern 1: Graceful Degradation

The most common production pattern: if the full workflow fails, return the best partial result with honest metadata.

```spl
CREATE FUNCTION summarize_doc(doc TEXT) RETURNS TEXT AS $$
Summarize the following document in 3-5 sentences:
{doc}
$$;

CREATE FUNCTION fallback_extract(doc TEXT) RETURNS TEXT AS $$
Extract the first paragraph of the following document as a fallback summary:
{doc}
$$;

WORKFLOW robust_summarizer
    INPUT:
        @document TEXT,
        @max_length INTEGER DEFAULT 500
    OUTPUT: @summary TEXT
DO
    GENERATE summarize_doc(@document) INTO @summary
    COMMIT @summary WITH status = 'complete'

EXCEPTION
    WHEN ContextLengthExceeded THEN
        -- Document too long for the model's context window.
        -- Fall back to extracting just the first paragraph.
        GENERATE fallback_extract(@document) INTO @summary
        COMMIT @summary WITH status = 'truncated', note = 'document exceeded context limit'

    WHEN GenerationError THEN
        -- Model call failed entirely.
        -- Commit an empty result with diagnostic information rather than crashing.
        COMMIT '' WITH status = 'error', document_length = @max_length

    WHEN BudgetExceeded THEN
        -- We ran out of tokens. Commit whatever we have.
        COMMIT @summary WITH status = 'budget_limit'
END
```

**Key principle:** Every exception handler commits a result. The consumer of the workflow always gets a committed output — even if that output is an empty string with `status = 'error'`. Silent failures are worse than honest failures.

<!-- --- -->

## Pattern 2: Retry with Backoff

For transient failures (network timeouts, rate limits), retry the failing step with progressively adjusted instructions.

```spl
CREATE FUNCTION generate_with_retry_hint(input TEXT, attempt TEXT) RETURNS TEXT AS $$
Attempt {attempt}: Process the following input.
If previous attempts failed due to output length, produce a shorter response.

Input: {input}
$$;

WORKFLOW retry_workflow
    INPUT: @input TEXT
    OUTPUT: @result TEXT
DO
    @attempt := 1
    @max_attempts := 3

    WHILE @attempt <= @max_attempts DO
        GENERATE generate_with_retry_hint(@input, @attempt) INTO @result

        EVALUATE @result
            WHEN 'error' THEN
                @attempt := @attempt + 1
            OTHERWISE
                COMMIT @result WITH status = 'complete', attempts = @attempt
        END
    END

    COMMIT @result WITH status = 'max_retries', attempts = @attempt

EXCEPTION
    WHEN GenerationError THEN
        COMMIT '' WITH status = 'generation_failed', attempts = @attempt
END
```

**Important limitation:** SPL does not provide automatic retry with exponential backoff — that is implemented at the adapter level for transient infrastructure failures. The pattern above is for *application-level* retry where you want to modify the prompt or reduce scope on each attempt.

<!-- --- -->

## Pattern 3: Multi-Step Error Isolation

In long workflows, a failure in step 3 should not discard the results of steps 1 and 2. Checkpoint intermediate results.

```spl
WORKFLOW pipeline_with_checkpoints
    INPUT:
        @topic TEXT,
        @output_dir TEXT DEFAULT ''
    OUTPUT: @report TEXT
DO
    -- Step 1: Research
    GENERATE research(@topic) INTO @research_notes
    CALL write_checkpoint(@output_dir, 'research.txt', @research_notes) INTO @_

    -- Step 2: Analysis (builds on research)
    GENERATE analyze(@topic, @research_notes) INTO @analysis
    CALL write_checkpoint(@output_dir, 'analysis.txt', @analysis) INTO @_

    -- Step 3: Report (builds on both)
    GENERATE write_report(@topic, @research_notes, @analysis) INTO @report
    COMMIT @report WITH status = 'complete'

EXCEPTION
    WHEN GenerationError THEN
        -- Commit whatever was last successfully generated.
        -- The checkpoint files preserve earlier steps for manual recovery.
        COMMIT @analysis WITH
            status = 'partial',
            completed_through = 'analysis',
            checkpoint_dir = @output_dir
END
```

The `write_checkpoint` CALL uses a tool function to persist intermediate state. If the workflow fails at step 3, steps 1 and 2 are preserved on disk. Manual recovery is possible without re-running the expensive early steps.

<!-- --- -->

## Pattern 4: LLM-as-Judge for Output Validation

Use a second LLM call to validate the output of the first, and escalate if it fails.

```spl
CREATE FUNCTION generate_content(task TEXT) RETURNS TEXT AS $$
Complete the following task:
{task}
$$;

CREATE FUNCTION validate_output(task TEXT, output TEXT) RETURNS TEXT AS $$
Does the following output correctly complete the task?

Task: {task}
Output: {output}

Reply with exactly one word: "valid" or "invalid".
$$;

WORKFLOW validated_generation
    INPUT:
        @task TEXT,
        @max_validation_attempts INTEGER DEFAULT 2
    OUTPUT: @output TEXT
DO
    @attempt := 0

    WHILE @attempt < @max_validation_attempts DO
        GENERATE generate_content(@task) INTO @output
        GENERATE validate_output(@task, @output) INTO @verdict

        EVALUATE @verdict
            WHEN 'valid' THEN
                COMMIT @output WITH status = 'complete', attempts = @attempt
            OTHERWISE
                @attempt := @attempt + 1
        END
    END

    -- Exceeded validation attempts — commit best effort
    COMMIT @output WITH status = 'unvalidated', attempts = @attempt

EXCEPTION
    WHEN MaxIterationsReached THEN
        COMMIT @output WITH status = 'max_retries'
    WHEN BudgetExceeded THEN
        COMMIT @output WITH status = 'budget_limit'
END
```

**Design note:** The validator here is an LLM call, which means it is probabilistic. A "valid"/"invalid" verdict from an LLM is not a guarantee. For applications where correctness is critical, supplement LLM validation with a deterministic `CALL` to a schema validator, unit test, or rule engine.

<!-- --- -->

## The SQL Analogy

| SQL mechanism | SPL equivalent | Purpose |
|---|---|---|
| `BEGIN...EXCEPTION...END` | `EXCEPTION` block | Catch named failures |
| `ROLLBACK TO SAVEPOINT` | `COMMIT partial WITH status = 'partial'` | Preserve progress up to the failure |
| `CONSTRAINT` / `CHECK` | `EVALUATE @verdict WHEN 'invalid'` | Validate output quality |
| `RETRY` (in some DBs) | `WHILE @attempt < @max DO ... @attempt + 1` | Retry on transient failure |
| Audit log | `COMMIT WITH status = 'error', metadata` | Record the failure for investigation |

<!-- --- -->

## Running It

```bash
# Safe generation with all exception types visible
spl run cookbook/07_safe_generation/safe_generation.spl \
    --adapter ollama -m gemma3 \
    topic="Explain quantum entanglement in simple terms"

# Force a budget limit to see the BudgetExceeded handler
spl run cookbook/07_safe_generation/safe_generation.spl \
    --adapter ollama -m gemma3 \
    --budget 50 \
    topic="Write a 5000-word essay on the history of computing"
```

<!-- --- -->

## Reproducibility Note

Exception handling paths are inherently harder to reproduce than happy paths, because they depend on failure conditions that may be intermittent (rate limits, network timeouts) or model-specific (refusals, context limits). Test exception handlers by simulating failure conditions explicitly: use `--budget` to trigger `BudgetExceeded`, use an extremely long document to trigger `ContextLengthExceeded`, or use a deliberately nonsensical prompt to observe `GenerationError` recovery.

<!-- --- -->

## When to Use These Patterns

Every workflow you deploy to production should have:

1. **A `GenerationError` handler** — network failures and model refusals are not rare.
2. **A `BudgetExceeded` handler** — token budgets are real in production; unexpected long documents happen.
3. **Meaningful committed output in every handler** — consumers of the workflow need to know what happened.

Add `MaxIterationsReached` and `ContextLengthExceeded` handlers for any workflow with a `WHILE` loop or that processes user-supplied document content.

The LLM-as-judge validation pattern (Pattern 4) should be added to any workflow where output quality is a hard requirement — not just a preference.

<!-- --- -->

## Exercises

1. **Add exception handling to an existing recipe.** Pick any recipe from Part 2 (Agentic Patterns) that does not have an `EXCEPTION` block. Add handlers for `GenerationError`, `MaxIterationsReached`, and `BudgetExceeded`. Decide what each handler should commit and why.

2. **Simulate a budget limit.** Run any multi-step recipe with `--budget 100` — a very small token budget. Observe what the `BudgetExceeded` handler commits. Is it useful? Would a real consumer of this workflow be able to recover from it?

3. **Write a validator.** For Recipe 2.3 (Plan and Execute), add a validation step using a second GENERATE call that checks whether the generated plan is well-formed (numbered steps, at least 3 steps, no duplicate step descriptions). Route `invalid` plans back to the planner for a retry, up to 2 retries.
