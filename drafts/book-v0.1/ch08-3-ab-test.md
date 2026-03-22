# A/B Test

*"The only thing better than a good prompt is a proven prompt."*

---

## The Pattern

In traditional software development, A/B testing is used to compare two versions of a website or feature to see which one performs better with users. In the world of AI, A/B testing is used to compare two different **prompts** (or models) to see which one produces the highest-quality output for a specific task.

Most prompt engineering is done by "vibe check"—you tweak a word, run it once, and if it looks okay, you ship it. This is dangerous. A prompt that looks better for one input might be much worse for another.

**Automated A/B Testing** is the pattern of running two variants in parallel, scoring them against an objective rubric, and picking the winner based on hard data.
1.  **Generate**: Run Variant A and Variant B on the exact same task.
2.  **Score**: Use an LLM-as-Judge to score both responses on criteria like clarity, completeness, and engagement.
3.  **Compare**: Extract the numeric scores and calculate the margin.
4.  **Decide**: If the margin is large enough, pick the winner. If not, declare a tie.

The SQL analogy is a **Champion-Challenger Model** or a **Quality Audit**. You are running two "queries" against the same data and using an aggregate function to decide which one meets the business requirement more efficiently.

The A/B Test recipe (Recipe 26) implements this optimization loop. It can load pre-built experiments from an `experiments.json` file or accept ad-hoc prompt variants from the command line.

---

## The SPL Approach

This recipe demonstrates **Numeric Evaluation**—using SPL's arithmetic capabilities to compare LLM-generated scores and make a binding decision.

---

## The .spl File (Annotated)

```spl
-- Recipe 26: Prompt A/B Test
-- Compare two variants, score them, and pick the winner.

WORKFLOW ab_test
    INPUT: @task TEXT, @prompt_a TEXT, @prompt_b TEXT
DO
    -- Phase 1: Execution
    GENERATE run_variant_a(@task, @prompt_a) INTO @response_a -- (1) The "Champion"
    GENERATE run_variant_b(@task, @prompt_b) INTO @response_b -- (2) The "Challenger"

    -- Phase 2: Scoring
    GENERATE evaluate(@response_a, scoring_rubric()) INTO @score_a_json
    GENERATE evaluate(@response_b, scoring_rubric()) INTO @score_b_json

    -- Phase 3: Extraction (Deterministic)
    CALL extract_total(@score_a_json) INTO @score_a         -- (3) Prose to Numbers
    CALL extract_total(@score_b_json) INTO @score_b

    -- Phase 4: Decision Logic
    EVALUATE (@score_a - @score_b)                          -- (4) The Margin Check
        WHEN > 1.5 THEN
            COMMIT @response_a WITH winner = 'A', margin = (@score_a - @score_b)
        WHEN < -1.5 THEN
            COMMIT @response_b WITH winner = 'B', margin = (@score_b - @score_a)
        OTHERWISE
            COMMIT 'Tie' WITH winner = 'none'
    END
END
```

### (1) & (2) The Tournament

We run both versions of the prompt. Variant A is often your existing "Production" prompt (the Champion), and Variant B is the "Experimental" version (the Challenger). By running them in the same workflow, we ensure they are tested under identical conditions.

### (3) Prose to Numbers (`extract_total`)

The judge model returns a JSON object with several scores (clarity, accuracy, etc.) and a total. We use a Python tool to extract the raw `total` number. This is critical because SPL's `EVALUATE` block can perform mathematical comparisons (like `> 1.5`), which LLMs often struggle to do consistently in prose.

### (4) The Margin Check

We don't just pick the higher number. We look for a **Significant Margin** (in this case, 1.5 points). 
- If Variant A is only 0.1 points higher, it's effectively a tie.
- If Variant B is 2.0 points higher, it's a clear improvement, and the system declares it the winner.

SQL Analogy: **Threshold Filtering**. You are only acting on data that exceeds a certain "Confidence Interval."

---

## Running It

Run an ad-hoc test comparing two ways to explain neural networks:

```bash
spl run cookbook/26_ab_test/ab_test.spl --adapter ollama \
    task="Explain neural networks" \
    prompt_a="Explain like I'm 5 years old" \
    prompt_b="Give a technical explanation with analogies"
```

Expected output: The winning response, along with metadata showing the scores for both variants and the margin of victory.

---

## What Just Happened

**LLM calls: 4.** (2 runs + 2 scores)
**Tool calls: 2.** (2 score extractions)

The "Conductor" (SPL Runtime) managed a "Scientific Experiment":
1.  **Executed** the control and the variable groups.
2.  **Measured** the results against a standard rubric.
3.  **Quantified** the performance delta.
4.  **Rendered** an objective verdict based on data, not vibes.

---

## Reproducibility Note

Prompt A/B testing is the foundation of **Continuous Improvement**. By running this recipe every time you change a prompt, you ensure that your "improvements" are actually making the system better.

On a **GTX 1080 Ti**, a full A/B test takes **20–40 seconds**. This is a small price to pay for the confidence that your production prompts are optimized.

---

## When to Use This Pattern

Use the **A/B Test** pattern when:
- **Prompt Optimization**: You are trying to find the "Perfect Phrasing" for a complex task.
- **Model Migration**: Comparing how your existing prompts perform on a new model (e.g., Llama 3.1 vs Llama 3.2).
- **Regression Testing**: Ensuring that a "Safe" version of a prompt hasn't lost too much "Creativity" or "Detail."

---

## Exercises

1.  **Multi-Input Test.** Modify the workflow to run the A/B test across three different inputs and pick the variant that has the highest *average* score.
2.  **Add a "Cost" Weight.** (Advanced) If Variant A is run on a local model and Variant B is run on a cloud model, modify the decision logic to only pick Variant B if its score is at least 3 points higher (to justify the cost).
3.  **Tie-Breaker.** If the margin check results in a "Tie," add a final step that asks a third, even stronger model (the "Super Judge") to break the tie.
