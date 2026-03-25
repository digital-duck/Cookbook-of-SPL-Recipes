# Reflection Agent

<!-- *"A genius is someone who makes their mistakes quickly and catches them even faster." — Wen Gong* -->

<!-- --- -->

## The Pattern

When you ask an LLM a complex question, its first response is often "directionally correct" but flawed in the details. It might overlook a corner case, make a subtle logical error, or provide a generic answer when a specific one was needed. If you simply accept the first output, you are settling for the model's "System 1" thinking—fast, intuitive, but prone to error.

**Reflection** is the process of forcing the model to look at its own work and find its own mistakes. It is a "System 2" pattern: slow, deliberate, and meta-cognitive. Instead of just answering the problem, the model performs a three-step dance:
1.  **Solve**: Produce an initial answer.
2.  **Reflect**: Analyze that answer for gaps, errors, or weak reasoning.
3.  **Correct**: Revise the answer based on the reflection.

The SQL analogy is a **Self-Correction Loop** or a **Recursive Validation**. You are performing a "sanity check" on a temporary result set before committing it to the final output.

The Reflection Agent recipe (Recipe 16) implements this loop using a `WHILE` block. It doesn't just refine the text; it calculates a "Confidence Score." If the score is too low, it iterates. If the score is high, it stops. This ensures that the workflow is only as complex as the problem requires.

<!-- --- -->

## The SPL Approach

This recipe demonstrates the use of **Meta-Cognitive Branching**—using the model’s own self-assessment to decide whether to continue the loop.

<!-- --- -->

## The .spl File (Annotated)

```spl
-- Recipe 16: Reflection Agent
-- Solve a problem, then reflect and correct until confident.

WORKFLOW reflection_agent
    INPUT: @problem TEXT
DO
    @iteration := 0
    @max_reflections := 3
    @confidence := 0

    -- Phase 1: Initial Attempt
    GENERATE solve(@problem) INTO @answer      -- (1) The "System 1" response

    -- Phase 2: The Meta-Cognitive Loop
    WHILE @iteration < @max_reflections DO
        -- Reflect: find errors or gaps
        GENERATE reflect(@problem, @answer) INTO @reflection -- (2) The "Mirror" step

        -- Score confidence (LLM-as-Judge of its own work)
        GENERATE confidence_score(@answer, @reflection) INTO @confidence -- (3) Quantifying doubt

        EVALUATE @confidence
            WHEN > 0.85 THEN                   -- (4) The Confidence Threshold
                COMMIT @answer WITH status = 'confident'
            OTHERWISE
                -- Extract issues and correct
                GENERATE extract_issues(@reflection) INTO @issues
                GENERATE correct(@answer, @issues, @problem) INTO @answer
                @iteration := @iteration + 1
        END
    END

    -- Final Commit (Best Effort)
    COMMIT @answer WITH status = 'best_effort'
END
```

### (1) The Initial Solve

The first `GENERATE` call is the baseline. We ask the model to solve the problem as it normally would. This result is stored in `@answer`.

### (2) The "Mirror" Step (`reflect`)

Instead of asking for a better answer immediately, we ask the model to be its own "Critical Editor." 
- "What did you miss?" 
- "Are there any logical contradictions?" 
- "Is the reasoning sound?"

This step produces a "Reflection"—a document that describes what is wrong with the current answer.

### (3) Quantifying Doubt (`confidence_score`)

We ask the model (or a second, larger "Judge" model) to look at the `@answer` and the `@reflection` and produce a numeric score from 0 to 1. This turns a subjective feeling into a hard metric that the `WORKFLOW` can use for branching.

### (4) The Confidence Threshold

Using the `EVALUATE` block, we set a high bar (0.85). 
- If the model is confident, we `COMMIT` and exit early. 
- If not, we use the `@reflection` to trigger a `correct` step and try again.

SQL Analogy: **Conditional COMMIT**. You only finalize the transaction if the data passes a series of semantic checks.

<!-- --- -->

## Running It

Run the reflection agent on a complex design problem:

```bash
spl run cookbook/16_reflection/reflection.spl --adapter ollama \
    problem="Design a URL shortener system that handles 1M requests per second"
```

In the execution trace, you will likely see at least one iteration where the model identifies a scaling bottleneck (like a database write limit) and corrects its initial design to include a caching layer or a load balancer.

<!-- --- -->

## What Just Happened

**LLM calls: 3 + (4 * iterations).**

The "Conductor" (SPL Runtime) managed a "Self-Correcting Brain":
1.  **Proposed** a solution.
2.  **Identified** flaws in that proposal.
3.  **Measured** the severity of those flaws.
4.  **Revised** the proposal until the measured risk was below the threshold.

This is how you get "Senior Engineer" level output from "Junior" level models. By forcing the model to slow down and check its work, you unlock its full reasoning potential.

<!-- --- -->

## Reproducibility Note

Reflection is highly effective but adds **Latency**. 
On a **GTX 1080 Ti**, a full 3-iteration loop can take **60–120 seconds**. 

However, the **Stability** is much higher than a single-pass prompt. Because the model has multiple chances to catch and fix its own errors, the final output is far more likely to be correct and complete across different runs.

<!-- --- -->

## When to Use This Pattern

Use the **Reflection Agent** pattern when:
- **Accuracy is the Priority**: Technical designs, logical proofs, or complex explanations.
- **Variable Problem Complexity**: Some problems are easy and don't need reflection; others are hard and need several passes. The confidence score handles both cases automatically.
- **Small Model Boosting**: If you are using a 7B or 14B parameter model, reflection can help it perform at the level of a 70B model.

<!-- --- -->

## Exercises

1.  **Strict Judge.** Use the `USING MODEL` clause (Chapter 9.1) to ensure the `confidence_score` step always uses your strongest model (e.g., `gemma3`), even if `phi4` is doing the reflection.
2.  **Add a "Divergent" step.** In the reflection pass, ask the model to specifically "Think about an alternative perspective" to prevent it from just reinforcing its own biases.
3.  **Manual Stop.** Add a step inside the loop that asks for human feedback before the next reflection pass begins.
