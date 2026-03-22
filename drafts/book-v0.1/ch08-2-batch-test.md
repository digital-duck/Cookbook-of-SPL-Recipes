# Batch Test

*"Don't just run it once; run it until it breaks, then run it again."*

---

## The Pattern

When building AI workflows, the biggest fear is **Regression**. You tweak a prompt to fix a bug in French, but you accidentally break the logic in English. Or you upgrade your model from Version 1 to Version 2, only to find that your structured output is now failing 10% of the time.

The manual way to test is impossible: you have dozens of recipes and multiple models. You cannot manually run and inspect every combination every time you make a change.

The SQL analogy is an **Automated Test Suite** or a **Batch Update**. You want to apply a set of "queries" (your recipes) against a set of "databases" (your models) and verify that the results meet a certain standard.

The Batch Test recipe (Recipe 10) is the "Test Runner" for the SPL cookbook. It fans out multiple recipes across multiple models in parallel, collects the results, and then uses a final "Reporter" model to generate a structured PASS/FAIL report. This is how we ensure the "100% pass rate" claimed in the book's preface.

---

## The SPL Approach

This recipe demonstrates the extreme power of **Parallel Fan-Out** using `WITH` clauses. It also shows how to use a "Judge" model to automate the analysis of test results.

---

## The .spl File (Annotated)

```spl
-- Recipe 10: Batch Test
-- Automated testing of key cookbook recipes across multiple models.

CREATE FUNCTION summarize_results(...) RETURNS TEXT AS $$
You are a test reporter. Produce a concise pass/fail report.
A result is PASS if the output is a non-empty, coherent response.
Format each line as: PASS recipe_name (model)
$$;

WORKFLOW batch_test
    INPUT:
        @model_1 TEXT DEFAULT 'gemma3',
        @model_2 TEXT DEFAULT 'llama3.2'
DO
    WITH                                     -- (1) Extreme Fan-Out
        -- Recipe 01: Hello World
        hello_m1 AS ( ... GENERATE greeting() USING MODEL @model_1 ),
        hello_m2 AS ( ... GENERATE greeting() USING MODEL @model_2 ),

        -- Recipe 02: Ollama Proxy
        proxy_m1 AS ( ... GENERATE answer(prompt) USING MODEL @model_1 ),
        proxy_m2 AS ( ... GENERATE answer(prompt) USING MODEL @model_2 ),

        -- Recipe 03: Multilingual
        multi_m1 AS ( ... GENERATE response(user_input, lang) USING MODEL @model_1 ),
        multi_m2 AS ( ... GENERATE response(user_input, lang) USING MODEL @model_2 )

    SELECT                                   -- (2) Synchronization Point
        hello_m1.greeting  AS hello_m1,  hello_m2.greeting  AS hello_m2,
        proxy_m1.answer    AS proxy_m1,  proxy_m2.answer    AS proxy_m2,
        multi_m1.response  AS multi_m1,  multi_m2.response  AS multi_m2
    INTO @hello_m1, @hello_m2,
         @proxy_m1, @proxy_m2,
         @multi_m1, @multi_m2

    GENERATE summarize_results(              -- (3) The Reporter
        @model_1, @model_2,
        '01_hello_world', @hello_m1, @hello_m2,
        '02_ollama_proxy', @proxy_m1, @proxy_m2,
        '03_multilingual', @multi_m1, @multi_m2
    ) INTO @report

    COMMIT @report                           -- (4) Final Commit
END
```

### (1) Extreme Fan-Out

In Recipe 04 (Model Showdown), we fanned out one prompt to three models. Here, we are fanning out **three different recipes** across **two models each**—a total of six parallel branches. 

This is the "Conductor" managing six instruments at once. If your hardware (like a **GTX 1080 Ti**) has the VRAM, these branches will execute simultaneously. If not, the SPL runtime will intelligently queue them.

### (2) Synchronization Point

The `SELECT ... INTO` acts as a barrier. The workflow will not proceed to the reporter until *all six* parallel branches have returned their results. This ensures your report is always complete.

### (3) The Reporter

We pass all six results into the `summarize_results` template. The judge model (the reporter) doesn't just print the results; it **analyzes** them. It checks for empty strings, error messages, or nonsensical output and applies the PASS/FAIL label.

### (4) Final Commit

The final `@report` is committed with metadata. This makes it easy to parse the output in a CI/CD pipeline (e.g., `grep "FAIL" output.log`).

---

## Running It

Run the batch test with your local models:

```bash
spl run cookbook/10_batch_test/batch_test.spl --adapter ollama
```

Expected output:
```
=== TEST REPORT ===
PASS  01_hello_world  (gemma3)
PASS  01_hello_world  (llama3.2)
PASS  02_ollama_proxy  (gemma3)
PASS  02_ollama_proxy  (llama3.2)
PASS  03_multilingual  (gemma3)
PASS  03_multilingual  (llama3.2)

Results: 6/6 passed, 0 failed
```

---

## What Just Happened

**LLM calls: 7.** (6 parallel tests + 1 reporter)

The SPL Runtime orchestrated a complex matrix of execution:
1.  Prepared six distinct context packages.
2.  Routed them to the appropriate models.
3.  Captured the responses into a structured state.
4.  Synthesized a comparative analysis.

This is the difference between "using AI" and **engineering AI systems**. By building your own test runner in SPL, you own the quality of your application.

---

## Reproducibility Note

Batch testing is the ultimate test of your local hardware. Running six LLM calls in parallel is demanding. If you see `GenerationError` exceptions, it might be because your VRAM is saturated. 

**Pro Tip**: For batch testing on commodity hardware, consider setting a `max_concurrency` parameter in your SPL configuration to limit how many models are loaded at once.

---

## When to Use This Pattern

Use the **Batch Test** pattern when:
- **CI/CD Pipelines**: Automatically verify your workflows before every commit.
- **Model Evaluation**: When you want to see which model is the most "stable" across a variety of tasks.
- **Regression Testing**: After you update a system prompt, run a batch test to ensure you haven't introduced side effects in other parts of the workflow.

---

## Exercises

1.  **Add a 4th Recipe.** Modify the workflow to include Recipe 05 (Self-Refine) in the batch test.
2.  **Strict PASS/FAIL.** Update the `summarize_results` prompt to be even stricter—for example, a result is a "FAIL" if it contains more than 50 words.
3.  **JSON Reporting.** (Advanced) Research how to change the `summarize_results` function to return valid JSON so that the test results can be automatically parsed by a dashboard.
