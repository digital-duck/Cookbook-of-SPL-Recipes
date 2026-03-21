# Chapter 6.1 — Debate Arena

*"The truth is a spark that flies when two stones of opinion are struck together."*

---

## The Pattern

When a single model answers a question, you get a single perspective. That perspective is shaped by the model's training data, its safety filters, and its inherent biases. If you are exploring a complex, nuanced topic—like "Should AI be open-sourced?"—a single response is rarely enough. You need to see the "pro" and the "con" argued with equal vigor.

The **Debate Arena** pattern uses multiple LLM instances (or personas) to argue opposing sides of a motion. By forcing the models to rebut each other's points over several rounds, you expose the depth of the topic and the weaknesses in each argument.

The SQL analogy is a **Self-Join with State** or a **Recursive CTE**. You are taking the "output" of one row (the pro argument) and using it as the "input" for the next row (the con rebuttal), repeating the process until a termination condition is met.

The Debate Arena recipe (Recipe 11) implements a multi-round debate. Two personas trade opening statements and rebuttals, while a third "Judge" persona monitors the history and declares a winner. This is a powerful technique for stress-testing ideas and discovering edge cases.

---

## The SPL Approach

This recipe introduces the `WHILE` loop for iterative reasoning and the pattern of "State Accumulation" (building a history string over multiple steps).

---

## The .spl File (Annotated)

```sql
-- Recipe 11: Debate Arena
-- Two personas argue opposing sides, then a judge picks the winner.

WORKFLOW debate_arena
    INPUT: @topic TEXT, @max_rounds integer DEFAULT 3
DO
    @round := 0
    @pro_history := ''                        -- (1) State initialization
    @con_history := ''

    -- Opening statements
    GENERATE pro_argument(@topic, 'opening statement') INTO @pro
    GENERATE con_argument(@topic, 'opening statement') INTO @con

    @pro_history := @pro                      -- (2) Seeding the history
    @con_history := @con

    WHILE @round < @max_rounds DO              -- (3) Iterative Reasoning
        -- Pro rebuts Con's latest point
        GENERATE pro_argument(@topic, @con_history) INTO @pro_rebuttal
        @pro_history := @pro_history + '\n---\n' + @pro_rebuttal

        -- Con rebuts Pro's latest point
        GENERATE con_argument(@topic, @pro_history) INTO @con_rebuttal
        @con_history := @con_history + '\n---\n' + @con_rebuttal

        @round := @round + 1
    END

    -- Judge evaluates both sides
    GENERATE judge_debate(@topic, @pro_history, @con_history) INTO @verdict

    COMMIT @verdict                           -- (4) Final Judgment
END
```

### (1) & (2) State Management

In a debate, context is everything. You cannot rebut an argument you haven't seen. We initialize `@pro_history` and `@con_history` as strings and "seed" them with the opening statements. This is the "Working Memory" of the workflow.

### (3) `WHILE` (Iterative Reasoning)

This is the first time we've seen a loop in SPL. The `WHILE` loop allows the workflow to "think" for multiple turns. 
- In the first turn, the models establish their positions.
- In subsequent turns, they refine their positions based on the opponent's "evidence."

SQL Analogy: A **Recursive CTE** (`WITH RECURSIVE`). Each iteration of the loop builds upon the result set of the previous iteration.

### (4) The Final Judgment

After the rebuttals are complete, we call the `judge_debate` step. This step receives the *entire* history of the conversation. The judge is instructed to look for logical fallacies, strength of evidence, and clarity of thought to decide which side "won" the debate.

---

## Running It

Pick a controversial topic and let the models fight it out:

```bash
spl2 run cookbook/11_debate_arena/debate.spl --adapter ollama \
    topic="Remote work is better than office work"
```

Watch the execution trace. You will see the `pro_argument` and `con_argument` steps repeating as the loop progresses.

---

## What Just Happened

**LLM calls: 2 + (2 * max_rounds) + 1.** (With 3 rounds, that's 9 calls)

The "Conductor" (SPL Runtime) managed a dynamic conversation:
1.  Set the stage with opening statements.
2.  Iteratively "passed the microphone" between the pro and con personas.
3.  Appended the new arguments to the cumulative history strings.
4.  Terminated the loop after the specified number of rounds.
5.  Presented the full "transcript" to the judge for a final verdict.

---

## Reproducibility Note

Debates are highly non-deterministic. A single strong point in the opening statement can shift the entire trajectory of the conversation. 

On a **GTX 1080 Ti**, a 3-round debate can take **30–90 seconds**, as each rebuttal depends on the previous generation finishing. This is a sequential process—it cannot be fanned out in parallel because the context of Round 2 depends on the output of Round 1.

---

## When to Use This Pattern

Use the **Debate Arena** pattern when:
- **Red Teaming**: Argue against your own product's features or security assumptions to find weaknesses.
- **Complex Decision Making**: When you have two valid paths (e.g., "SQL vs. NoSQL") and want to explore the trade-offs in depth.
- **Educational Tools**: Create an interactive tutor that can argue multiple sides of a historical or scientific debate.

---

## Exercises

1.  **Change the Personas.** (Advanced) Research how to use `CREATE FUNCTION` (Chapter 8.1) to give the Pro and Con sides specific "backgrounds" (e.g., "You are a CEO" vs. "You are a junior developer").
2.  **Add a Moderator.** Insert a step inside the `WHILE` loop where a "Moderator" model summarizes the debate so far and asks a specific follow-up question.
3.  **Variable Rounds.** Modify the workflow to accept `@max_rounds` from the command line, and try a "Lightning Round" (1 round) vs. an "Exhaustive Debate" (5 rounds).
