# Self-Refine

<!-- *"The first draft is never the answer. The discipline is knowing when to stop revising." — Wen Gong* -->

<!-- --- -->

## The Pattern

You have a task that benefits from iteration: drafting a persuasive email, writing technical documentation, composing a code review comment. The naive approach is to call the LLM once and accept whatever comes back. Experienced practitioners know the first pass is rarely production-ready.

The Python equivalent looks roughly like this:

```python
draft = llm.generate(task)
for i in range(max_iterations):
    feedback = llm.critique(draft)
    if feedback.strip().lower() == "satisfactory":
        break
    draft = llm.refine(draft, feedback)
```

This is manageable to write, but awkward to maintain. The loop logic, the exit condition, and the budget handling are all tangled together. When you add exception handling for budget overruns or you want to pass quality metadata to the caller, the code grows in directions that obscure the original intent. Six months later, a new team member reads this and has to reconstruct the algorithm from the implementation details.

More practically: every team that uses LLMs for iterative generation writes this loop. They each write it slightly differently. There is no shared vocabulary for the pattern, no standard way to configure `max_iterations` from the outside, no consistent exception surface.

SPL gives this pattern a name and a syntax.

<!-- --- -->

## The SPL Approach

Generate a draft, then loop: critique the draft, exit if satisfactory, otherwise refine and repeat — up to a configurable iteration limit.

<!-- --- -->

## The .spl File (Annotated)

```spl
-- SPL 2.0: Self-Refine Pattern
-- Iteratively improves output through critique and refinement

WORKFLOW self_refine
  INPUT:
    @task text,
    @max_iterations integer default 5      -- caller controls iteration budget
  OUTPUT: @result text
DO
  @iteration := 0
  -- @max_iterations := 5                 -- default shown; overridable at runtime

  -- Initial draft — one LLM call, cold start
  GENERATE draft(@task) INTO @current
  --
  -- SQL analogy: this is the seed row that the UPDATE loop will refine.
  -- Think: INSERT INTO drafts VALUES (llm_generate(task));

  -- Iterative refinement loop
  WHILE @iteration < @max_iterations DO
    -- Ask the LLM to critique its own output
    GENERATE critique(@current) INTO @feedback
    --
    -- critique() is a CREATE FUNCTION (not shown in this file, but registered
    -- in the system context). It receives @current as input and is prompted
    -- to return either "satisfactory" or a specific critique.
    -- The LLM is not deciding the control flow — EVALUATE is.

    EVALUATE @feedback
      WHEN 'satisfactory' THEN
        -- Early exit: quality threshold reached before max_iterations
        -- SQL analogy: BREAK in a cursor loop when WHERE condition is met
        COMMIT @current WITH status = 'complete', iterations = @iteration
      OTHERWISE
        -- Refine: feed the critique back into the LLM alongside the draft
        GENERATE refined(@current, @feedback) INTO @current
        @iteration := @iteration + 1
    END
  END

  -- Loop exhausted without hitting 'satisfactory' — commit best effort
  -- SQL analogy: the cursor reached EOF; commit whatever state we're in
  COMMIT @current WITH status = 'max_iterations', iterations = @iteration

EXCEPTION
  WHEN MaxIterationsReached THEN
    -- Runtime raised this before our loop could: external budget enforcer
    COMMIT @current WITH status = 'partial'
  WHEN BudgetExceeded THEN
    -- Token/cost budget hit — commit whatever is in @current
    COMMIT @current WITH status = 'budget_limit'
END
```

**Key design decisions to notice:**

`EVALUATE @feedback / WHEN 'satisfactory'` — The LLM wrote `@feedback`, but the LLM does not decide whether to exit the loop. `EVALUATE` is deterministic string matching. The LLM's job is to produce the word "satisfactory" or a critique. The runtime's job is to act on it. This separation is intentional and important.

`@max_iterations integer default 5` — This is not hardcoded. The caller decides the iteration budget. A CI pipeline might pass `max_iterations=2` for speed; an offline document editor might pass `max_iterations=10` for quality. The workflow has no opinion.

`COMMIT @current WITH status = 'complete', iterations = @iteration` — The COMMIT carries metadata. Downstream code can see how many iterations were needed. A monitoring dashboard can track this over time: if your average `iterations` is creeping up, your base draft quality may be degrading, or your critique prompt has become too strict.

`EXCEPTION / WHEN BudgetExceeded` — The runtime enforces a token budget independently of your loop counter. If costs spike mid-run, the workflow does not crash with an unhandled exception. It commits what it has and marks the status clearly.

<!-- --- -->

## The SQL Analogy in Depth

SQL practitioners are comfortable with cursor loops. The self-refine pattern is a cursor loop where the exit condition is semantic rather than positional.

A conventional cursor loop:

```sql
DECLARE cur CURSOR FOR SELECT id, text FROM drafts WHERE status = 'pending';
OPEN cur;
LOOP
  FETCH cur INTO v_id, v_text;
  EXIT WHEN NOT FOUND;
  UPDATE drafts SET text = improve(v_text) WHERE id = v_id;
END LOOP;
CLOSE cur;
```

The self-refine SPL workflow is structurally identical, except:
- There is only one row (the current draft).
- The exit condition (`WHEN 'satisfactory'`) is evaluated by the LLM at each step, not derived from a SQL predicate.
- The "UPDATE" is a GENERATE that produces a new version of the same row.

A stored procedure that calls `UPDATE` in a loop until a quality score exceeds a threshold is doing exactly what `self_refine.spl` does. The syntax differs. The logic is the same.

<!-- --- -->

## Running It

```bash
spl run cookbook/05_self_refine/self_refine.spl \
    --adapter ollama -m gemma3 \
    task="Write a concise product description for a noise-cancelling travel headphone" \
    max_iterations=3
```

Expected output (truncated):

```output
[draft] Generating initial draft...
[critique] Iteration 0: feedback received
[refined] Iteration 0: draft updated
[critique] Iteration 1: satisfactory
[commit] status=complete iterations=1

Result:
Experience travel in silence. Our noise-cancelling headphones block ambient
cabin noise while delivering rich, balanced audio across a 30-hour battery
life. Lightweight folding design fits any carry-on pocket. USB-C charging
from 0 to 80% in 45 minutes.
```

<!-- --- -->

## What Just Happened

**LLM calls made:** 3 (1 draft + 1 critique at iteration 0 + 1 critique at iteration 1).

**Step-by-step:**

1. `GENERATE draft(@task)` — Cold start. The LLM writes a first-pass product description from nothing.

2. `GENERATE critique(@current)` at iteration 0 — The LLM evaluates its own output. In this run it found the draft vague ("rich audio" with no specifics), returned structured feedback.

3. `GENERATE refined(@current, @feedback)` at iteration 0 — The LLM revised the draft incorporating the critique. Concrete battery life, charge time, and weight claim were added.

4. `GENERATE critique(@current)` at iteration 1 — The LLM re-evaluated. Returned "satisfactory".

5. `EVALUATE 'satisfactory'` — Matched the exit branch. `COMMIT` fired with `status='complete'` and `iterations=1`.

The key insight: the workflow ran 2 fewer LLM calls than `max_iterations` would have permitted. Early exit is working correctly. On poor-quality base prompts, expect to see `iterations=4` or `iterations=5` (max).

<!-- --- -->

## Reproducibility Note

**Hardware:** GTX 1080 Ti, 11GB VRAM. **Model:** gemma3 via Ollama.

Typical wall-clock time for a short copywriting task: 8–14 seconds for a 2-iteration run, 18–28 seconds for a 5-iteration run.

**Stability:** The critique function's "satisfactory" output is sensitive to prompt wording. If your critique prompt does not explicitly instruct the model to return the exact string "satisfactory" (and nothing else) when the draft meets the bar, you will see false negatives — the EVALUATE branch will always fall through to OTHERWISE, exhausting `max_iterations` every run. Test your critique prompt in isolation before embedding it in the loop.

**Non-determinism:** Two runs on identical input will often differ at iteration count. One run exits at iteration 1, the next at iteration 2. This is expected. The self-refine pattern is not designed to be deterministic at the iteration level — only at the structural level (the loop always terminates, the output is always committed, exceptions are always handled).

<!-- --- -->

## When to Use This Pattern

**Good fit:**
- Content generation where quality has a measurable (if fuzzy) threshold: product copy, executive summaries, cover letters, commit messages.
- Code documentation where "complete and accurate" is a binary outcome that can be evaluated by a second LLM pass.
- Any task where you have seen humans naturally do "write, review, rewrite" manually.

**Poor fit:**
- Tasks with an objective correct answer. Use `CALL` + a Python validator instead of a critique loop. An LLM critiquing a SQL query it generated may not catch a logical error it already made.
- High-volume batch jobs where you need strict cost control. A 5-iteration loop on 1,000 inputs could mean 5,000 LLM calls in the worst case. Set `max_iterations=2` for batch workloads and accept the quality tradeoff.
- Real-time applications. The latency stacks multiplicatively. A 3-second LLM call becomes 15 seconds at `max_iterations=5`.

**The right tool vs. alternatives:**
- Self-Refine vs. Reflection (Chapter 3.4): Self-refine evaluates the *output*. Reflection evaluates the *reasoning process*. Use self-refine when the output quality is observable; use reflection when the reasoning steps may be subtly wrong even when the output looks correct.
- Self-Refine vs. Ensemble Voting (section 6.3): Ensemble generates N drafts and picks the best. Self-refine generates one draft and improves it. Use self-refine when you have a clear critique standard; use ensemble when you want diversity.

<!-- --- -->

## Exercises

1. **Tighten the critique prompt.** The default critique function accepts any structured feedback. Modify the `CREATE FUNCTION critique()` to require a structured output: a rating 1–10 and a bullet-point list of specific issues. Change `EVALUATE @feedback` to check `WHEN > 7` instead of `WHEN 'satisfactory'`. How does output quality change?

2. **Add a word-count constraint.** The current workflow has no length control. Add a `CALL count_words(@current) INTO @word_count` step using a Python tool, and add a second EVALUATE that truncates or expands the draft if it falls outside a target range (e.g., 50–80 words). This introduces a hybrid: deterministic length enforcement combined with LLM quality refinement.

3. **Instrument the iteration cost.** Modify the COMMIT to also record an estimated token cost per iteration. Add a Python tool `estimate_tokens(text)` that returns a character-count approximation. After 10 runs, plot the cost vs. iterations vs. final quality. This gives you the data to set `max_iterations` empirically rather than arbitrarily.
