# Safe Generation

<!-- *"Trust, but verify. Then verify again." — Wen Gong* -->

<!-- --- -->

## The Pattern

In the early days of LLMs, we lived in a "Fire and Forget" world. You sent a prompt, got a response, and hoped for the best. If the model hallucinated, refused to answer, or produced low-quality prose, your application simply passed that failure onto the user. 

In a production environment, this is unacceptable. You need **Guardrails**. You need a way to catch errors *before* they reach the user and a way to handle the unique "exceptions" that only happen in generative AI—like context window overflows or safety refusals.

The SQL analogy is a **CONSTRAINT** or a **CHECK** clause. You don't just insert data into a table; you ensure it meets certain criteria (not null, unique, within range). If the criteria aren't met, the transaction fails or triggers a correction.

The Safe Generation recipe (section 4.1) implements this as a "Self-Correction Loop." It generates a response, uses an "LLM-as-Judge" to evaluate the quality, and then branches to different outcomes based on the verdict. It also demonstrates SPL 2.0's advanced `EXCEPTION` handling for generative risks.

<!-- --- -->

## The SPL Approach

This recipe introduces the `EVALUATE` block for semantic branching and the `EXCEPTION` block for handling non-deterministic errors.

<!-- --- -->

## The .spl File (Annotated)

```spl
-- Recipe 07: Safe Generation with Exception Handling
-- Demonstrates LLM-specific error handling patterns

WORKFLOW safe_generation
  INPUT: @prompt text
  OUTPUT: @result text
DO
  GENERATE response(@prompt) INTO @result      -- (1) Initial generation

  -- Quality check via semantic evaluation (LLM-as-judge)
  GENERATE quality_assess(@result) INTO @quality -- (2) The "Judge" step

  EVALUATE @quality                            -- (3) Semantic Branching
    WHEN 'high_quality' THEN
      COMMIT @result WITH status = 'high_quality'
    WHEN 'acceptable' THEN                     -- (4) Refinement loop
      GENERATE improved(@result, @prompt) INTO @result
      COMMIT @result WITH status = 'refined'
    OTHERWISE
      COMMIT @result WITH status = 'best_effort'
  END

EXCEPTION                                      -- (5) Generative Exceptions
  WHEN HallucinationDetected THEN
    GENERATE response(@prompt) INTO @result    -- (6) Strategic recovery
    COMMIT @result WITH status = 'conservative'

  WHEN ContextLengthExceeded THEN
    RETRY WITH temperature = 0.1               -- (7) Automated retry

  WHEN RefusalToAnswer THEN
    COMMIT @prompt WITH status = 'refused'
END
```

### (1) & (2) Generation and Assessment

We start with a standard `GENERATE` call. But instead of returning the result immediately, we pass it to a second `GENERATE` step called `quality_assess`. This is the "LLM-as-Judge" pattern: using a model (often a larger, more capable one) to grade the work of another model.

### (3) `EVALUATE` (Semantic Branching)

In traditional programming, you branch on booleans or integers (`if x > 5`). In SPL, you branch on **Semantic Labels**. The `EVALUATE` block looks at the string returned by `@quality` and matches it against your `WHEN` clauses. 

SQL Analogy: A **CASE** statement. It maps inputs to specific outputs or actions based on a set of conditions.

### (4) Refinement

If the judge returns `'acceptable'`, we don't give up. We trigger a third generation—`improved(@result, @prompt)`—asking the model to fix the specific issues identified. This "Multi-Pass" approach significantly increases the reliability of the final output.

### (5) `EXCEPTION`

This is where SPL 2.0 handles the "known unknowns" of AI. These aren't syntax errors; they are **runtime behaviors** of the model or the adapter.

### (6) `HallucinationDetected`

This is a semantic exception. If the runtime detects (via internal consistency checks or external fact-checkers) that the model is making things up, it triggers this block. Here, we try one more time, perhaps with a more "conservative" prompt.

### (7) `RETRY WITH ...`

Some errors are transient or can be fixed by changing parameters. If the context length is exceeded, we might `RETRY` with a lower temperature to encourage the model to be more concise.

<!-- --- -->

## Running It

Run the safe generation with a potentially complex prompt:

```bash
spl run cookbook/07_safe_generation/safe_generation.spl --adapter ollama \
    prompt="What are the trade-offs of microservices?"
```

Observe the output status. If the first pass is good, you'll see `status='high_quality'`. If the model needed a second try, you'll see `status='refined'`.

<!-- --- -->

## What Just Happened

**LLM calls: 2 or 3.** (Depending on the quality pass)

The "Conductor" (SPL Runtime) ensured the safety of the transaction:
1.  Proposed a response.
2.  Validated the proposal against a quality standard.
3.  Executed a "Compensating Transaction" (improvement) if the quality was marginal.
4.  Committed the result with a clear metadata tag (`status`).

This pattern transforms an LLM from a "black box" into a **controlled component** within a larger system.

<!-- --- -->

## Reproducibility Note

The "Judge" model needs to be highly stable. If your judge is too small (e.g., a 1B parameter model), its evaluations might be inconsistent. For this recipe, we recommend using a "Senior" model like **gemma3 (27B)** or **Claude 3.5 Sonnet** as the evaluator, even if a "Junior" model (like **phi4**) is doing the initial generation.

<!-- --- -->

## When to Use This Pattern

Use the **Safe Generation** pattern when:
- **Quality is Non-Negotiable**: Customer-facing content, documentation, or legal summaries.
- **Handling Refusals**: When you need to gracefully handle cases where the model's safety filters block a legitimate request.
- **Self-Correction**: When the task is complex enough that the model rarely gets it perfect on the first try.

<!-- --- -->

## Exercises

1.  **Strict Guardrails.** Modify the `EVALUATE` block so that `OTHERWISE` results in a `REJECT` or an error message rather than a `best_effort` commit.
2.  **Add a "Banned Word" check.** Use a Python tool (Chapter 3.2) to check for specific words in `@result`. If found, trigger a custom exception.
3.  **Two-Model Judge.** Modify the recipe to use two different models as judges and only commit if they *both* agree the quality is high.
