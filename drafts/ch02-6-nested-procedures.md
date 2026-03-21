# Chapter 2.6 — Nested Procedures

*"Complexity should be composed, not managed."*

---

## The Pattern

As your AI applications grow, your `.spl` files can become long and difficult to read. If you have a workflow that researches a topic, explains it, generates examples, and checks reading level, putting all those steps in one giant `WORKFLOW` block is like writing a 1,000-line `main()` function in C. It’s hard to test, hard to reuse, and hard to debug.

The **Nested Procedures** pattern is the core of modular SPL development. It allows you to break a complex task into small, independent `PROCEDURE` units that can call each other. This is the foundation of **Deep Composability**.

The SQL analogy is **Nested Views** or **Modular Stored Procedures**. You don't write one massive query to generate a financial report. You write a view for `v_revenue`, another for `v_expenses`, and then a third view that joins them. Each piece is independently verified and perfectly encapsulated.

The Nested Procedures recipe (Recipe 25) demonstrates this hierarchy. It builds a "Layered Explainer" where high-level orchestration is separated from low-level generation tasks like complexity calibration and example making.

---

## The SPL Approach

This recipe introduces the pattern of **Procedural Delegation**—passing control from a high-level workflow to specialized sub-procedures.

---

## The .spl File (Annotated)

```spl2
-- Recipe 25: Nested Procedures
-- Demonstrates PROCEDURE calling PROCEDURE — deep composability.

PROCEDURE explain_layer(content TEXT, audience TEXT) -- (1) Leaf Procedure
RETURNS TEXT
DO
    GENERATE explain(content, audience) INTO @explanation
    COMMIT @explanation
END

PROCEDURE calibrate_complexity(text TEXT, audience TEXT) -- (2) Intermediate Procedure
RETURNS TEXT
DO
    GENERATE assess_reading_level(text) INTO @level
    EVALUATE @level
        WHEN > 8 THEN
            GENERATE simplify(text, audience) INTO @calibrated
            COMMIT @calibrated
        OTHERWISE
            COMMIT text
    END
END

WORKFLOW layered_explainer                      -- (3) Root Workflow
    INPUT: @topic TEXT, @audience TEXT
DO
    GENERATE research_overview(@topic) INTO @overview

    -- Calling the specialized procedures
    CALL explain_layer(@overview, @audience) INTO @base_exp -- (4) Delegation

    CALL calibrate_complexity(@base_exp, @audience) INTO @final_exp

    COMMIT @final_exp WITH status = 'complete'
END
```

### (1) The "Leaf" Procedure

`explain_layer` is a simple wrapper around a `GENERATE` call. Why bother making it a procedure? Because it encapsulates the "Explanation Persona." If you want to change how the model explains things (e.g., adding "avoid jargon" to the system prompt), you change it in this one procedure, and every workflow that uses it is automatically updated.

### (2) The "Intermediate" Procedure

`calibrate_complexity` is more complex. It contains its own `EVALUATE` logic and potentially its own nested calls. By making this a procedure, we can test the "Simplification Logic" in isolation without running the whole research workflow.

### (3) The Root Workflow

The `layered_explainer` acts as the "Conductor of Conductors." It doesn't worry about how to simplify text or how to explain a concept. It only worries about the high-level sequence: **Research → Explain → Calibrate**.

SQL Analogy: **Orchestration Query**. You are joining the outputs of multiple modular functions to produce a high-level report.

### (4) Delegation (`CALL`)

The `CALL` statement is the bridge. In SPL 2.0, `CALL` is used for both Python tools (Recipe 06) and other SPL procedures. This unified interface means you can swap a generative procedure for a deterministic tool without changing the calling code.

---

## Running It

Run the layered explainer for different audiences:

```bash
# To high schoolers
spl2 run cookbook/25_nested_procs/nested_procs.spl --adapter ollama \
    topic="quantum computing" audience="high school students"

# To policy makers
spl2 run cookbook/25_nested_procs/nested_procs.spl --adapter ollama \
    topic="CRISPR gene editing" audience="policy makers"
```

In the execution trace, you will see the "Call Stack" growing and shrinking as the runtime enters and exits each procedure.

---

## What Just Happened

**LLM calls: ~5-7.** (Depending on the complexity of the research and calibration steps)

The "Conductor" (SPL Runtime) managed a "Recursive Hierarchy":
1.  **Orchestrated** the high-level business logic.
2.  **Delegated** the domain-specific tasks to specialized "Agents" (Procedures).
3.  **Maintained** state across the hierarchy (passing `@base_exp` from one procedure to another).
4.  **Enforced** encapsulation (the root workflow never saw the intermediate `@level` variable).

---

## Reproducibility Note

Nested procedures are the key to **Scalable Maintenance**. When you find a bug in your "Simplification" logic, you fix it in `calibrate_complexity.spl`. You don't have to hunt through 20 different workflow files to find every place you used a similar prompt.

On a **GTX 1080 Ti**, the overhead of the "Procedure Call" is **zero**. The runtime treats nested procedures as logical blocks within the same execution context. The only latency comes from the underlying LLM calls.

---

## When to Use This Pattern

Use the **Nested Procedures** pattern when:
- **Large Projects**: Any `.spl` file that exceeds 100 lines should probably be broken into procedures.
- **Shared Logic**: When you have a task (like "PII Redaction" or "Tone Check") that is used by multiple different workflows.
- **Unit Testing**: When you want to verify that a specific part of your logic works correctly before integrating it into a complex agent.

---

## Exercises

1.  **Add a "Quiz" Procedure.** Create a third procedure called `make_quiz` that takes the `@final_exp` and generates 3 multiple-choice questions. Call it at the end of the root workflow.
2.  **Shared Library.** Move `explain_layer` into a separate file (`library.spl`) and research how to use the `IMPORT` or `--include` flags to use it in your main workflow.
3.  **Conditional Nesting.** Add a parameter `@skip_calibration` to the root workflow. Use an `EVALUATE` block to only `CALL calibrate_complexity` if the parameter is false.
