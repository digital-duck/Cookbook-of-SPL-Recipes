# Chapter 1.4 — Few-Shot Learning

*"Show, don't just tell."*

---

## The Pattern

Even the most sophisticated LLMs sometimes struggle to follow complex instructions. You might ask for a "JSON object with sentiment and summary," and the model might return a markdown-formatted string with a conversational preamble: *"Sure! Here is the JSON you requested..."*. This "chattiness" breaks automated pipelines.

**Few-Shot Learning** (or Few-Shot Prompting) is the technique of providing the model with 2–3 "gold-standard" examples of what a perfect input-output pair looks like. By seeing examples, the model "calibrates" its tone, format, and reasoning pattern to match your expectations. It is often more effective than writing a three-page instruction manual.

The SQL analogy is a **Lookup Table** or a **Reference Dataset**. You aren't just giving the database a schema; you are giving it a small set of "row templates" that define what valid data looks like.

The Few-Shot Learning recipe (Recipe 24) demonstrates how to embed these examples directly into the `SELECT` context. It uses a domain-swappable set of examples to guide the model across different industries (Finance, Ops, General).

---

## The SPL Approach

This recipe uses `CREATE FUNCTION` with a `SELECT CASE` block to deliver dynamic, domain-specific examples into the context row.

---

## The .spl File (Annotated)

```spl2
-- Recipe 24: Few-Shot Prompting
-- Embed gold-standard examples in context to guide output format.

CREATE FUNCTION few_shot_examples(domain TEXT DEFAULT 'general')
RETURNS TEXT AS $$
SELECT CASE domain                          -- (1) Domain-specific example sets
  WHEN 'finance' THEN
    '### Examples
     Input: "Revenue up 12% YoY."
     Output: {"sentiment": "positive", ...}'
  WHEN 'ops' THEN
    '### Examples
     Input: "Deployment succeeded."
     Output: {"status": "healthy", ...}'
  ELSE
    '### Examples
     Input: "New feature launched!"
     Output: {"sentiment": "positive", ...}'
END
$$;

PROMPT few_shot_classifier
SELECT
    system_role('You are a precise text classifier. Follow the examples exactly.'),
    few_shot_examples(context.domain) AS examples, -- (2) Dynamic context injection
    context.text AS text,
    context.domain AS domain
GENERATE classify(text, examples)           -- (3) Calibrated generation
```

### (1) Dynamic Examples via `SELECT CASE`

Instead of hardcoding examples into the prompt string, we encapsulate them in a function. This allows us to maintain different "Reference Sets" for different domains in one place. 

SQL Analogy: A **Stored Function** that returns a configuration string based on a parameter.

### (2) Dynamic Context Injection

In the `SELECT` clause, we call `few_shot_examples(context.domain)`. 
- If you pass `domain="finance"` on the CLI, the LLM receives finance-related examples. 
- If you pass `domain="ops"`, it gets operations-related examples.

This makes your workflow "Context-Aware" without duplicating the prompt logic.

### (3) Calibrated Generation

The `GENERATE` step receives both the user's `text` and the `examples`. Because the model sees the `### Examples` block right before it generates its own response, it naturally adopts the same JSON structure and field names shown in the examples.

---

## Running It

Run the classifier for the finance domain:

```bash
spl2 run cookbook/24_few_shot/few_shot.spl --adapter ollama \
    text="The quarterly results exceeded all analyst forecasts" \
    domain="finance"
```

Expected output (clean JSON):
```json
{"sentiment": "positive", "magnitude": 0.9, "topics": ["earnings", "forecasts"], "summary": "Q3 results beat analyst forecasts."}
```

Now try the operations domain:

```bash
spl2 run cookbook/24_few_shot/few_shot.spl --adapter ollama \
    text="System outage detected in EU-WEST-2" \
    domain="ops"
```

Expected output:
```json
{"status": "incident", "severity": "high", "action_required": true, "summary": "System outage in EU-WEST-2."}
```

---

## What Just Happened

**LLM calls: 1.**

The "Conductor" (SPL Runtime) managed the calibration:
1.  Looked up the `domain` parameter.
2.  Retrieved the matching "Reference Set" from the `few_shot_examples` function.
3.  Assembled a context package containing: System Role + Reference Examples + User Input.
4.  Executed a single, high-precision generation.

---

## Reproducibility Note

Few-shot prompting is one of the most effective ways to increase **Stability**. While a "Zero-Shot" prompt (no examples) might fail 5% of the time, a "Two-Shot" prompt usually reaches 99%+ reliability for formatting.

On a **GTX 1080 Ti**, adding a few examples adds negligible latency (a few milliseconds for the extra tokens) but saves hours of post-processing and debugging.

---

## When to Use This Pattern

Use the **Few-Shot Learning** pattern when:
- **Strict Format Requirements**: You need JSON, YAML, or a specific tone that the model doesn't always hit on the first try.
- **Domain Specialization**: You want the same workflow to behave differently for "Medical" vs. "Legal" vs. "Code" tasks.
- **Edge Case Handling**: If the model keeps making a specific mistake, add a "Negative Example" to the few-shot set to show it what *not* to do.

---

## Exercises

1.  **Add a "Negative" Case.** Modify the `few_shot_examples` to include a case where the input is "ambiguous" and the output should be an empty JSON object.
2.  **Toggle Example Count.** Modify the function to accept a second parameter `@count` and use it to return 1, 2, or 3 examples. See how the accuracy changes.
3.  **Cross-Domain Test.** Run the recipe with a Finance text but pass `domain="ops"`. Observe how the model tries to force-fit finance data into an operations schema. This is a great way to understand the "gravity" of examples.
