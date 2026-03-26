# Plan and Execute

<!-- *"A complex task is just a series of simple tasks that haven't been organized yet." — Wen Gong* -->

<!-- --- -->

## The Pattern

In the previous recipes, we focused on single tasks: generate a greeting, fetch a population, judge a debate. But real-world engineering is more complex. If you ask an LLM to "Build a REST API for a todo app," and it tries to write all the code in one go, it will likely fail. It will hit its output token limit, forget to include imports, or lose consistency between the database model and the API routes.

The **Plan and Execute** pattern is the professional way to handle large tasks. Instead of jumping straight to code, the system follows a structured lifecycle:
1.  **Planning**: Decompose the big goal into a numbered list of concrete, independent steps.
2.  **Execution**: Iterate through each step, making design decisions and generating code.
3.  **Refinement**: If a step fails validation, re-plan the remaining steps based on the new information.

The SQL analogy is a **Long-Running Transaction** or a **Recursive Batch Job**. You don't update a million rows in one statement; you break the work into batches, verify each batch, and log your progress so you can resume if something fails.

The Plan and Execute recipe (Recipe 12) is the most advanced workflow in the basics section. It demonstrates how to use nested `WHILE` loops and `EVALUATE` logic to manage a multi-file software project from start to finish.

<!-- --- -->

## The SPL Approach

This recipe introduces the "Two-Phase Loop" pattern, which is essential for generating large artifacts without hitting model limits.

<!-- --- -->

## The .spl File (Annotated)

```spl
-- Recipe 12: Plan and Execute
-- A planner decomposes a task, then an executor implements each step.

WORKFLOW plan_and_execute
    INPUT: @task TEXT, @output_dir TEXT, @max_steps INTEGER DEFAULT 5
DO
    -- Phase 1: Planning
    GENERATE plan(@task) INTO @plan            -- (1) Create the blueprint
    GENERATE count_steps(@plan) INTO @step_count

    -- Phase 2: Design Loop
    WHILE @step_index < @step_count DO         -- (2) Iterative Design
        GENERATE extract_step(@plan, @step_index) INTO @current_step
        GENERATE execute_step(@current_step, @results) INTO @step_result
        
        EVALUATE validate_step(@current_step, @step_result)
            WHEN 'failed' THEN                 -- (3) Automatic Re-planning
                GENERATE replan(@task, @plan, @step_index, @step_result) INTO @plan
                @step_index := 0
            ELSE
                @results := @results + @step_result
                @step_index := @step_index + 1
        END
    END

    -- Phase 3: Implementation Loop
    GENERATE outline_files(@task, @results) INTO @file_outline
    WHILE @file_index < @file_count DO         -- (4) The Implementation Loop
        GENERATE generate_file(...) INTO @file_code
        CALL write_code_files(@file_code, @output_dir) -- (5) Deterministic I/O
        @file_index := @file_index + 1
    END
END
```

### (1) Phase 1: Planning (The Blueprint)

We start by asking a "Senior Architect" persona to break the task down. The output is a simple numbered list. This list is our "Schedule" for the rest of the workflow.

### (2) Phase 2: Design Loop (Lightweight Reasoning)

**Crucial Lesson**: We do *not* generate code inside this first loop. Instead, we generate "Design Notes"—short descriptions of what each step should achieve. 
- Why? Because LLM context windows are finite. If we generated 500 lines of code in Step 1 and passed it all into Step 2, by Step 5 the model would be "drowned" in its own previous output.
- By keeping the loop "lightweight," we ensure the model stays focused on the design intent.

### (3) Automatic Re-planning

If a step fails (e.g., the model realizes a design choice is impossible), we use the `EVALUATE` block to trigger a `replan`. We feed the failure details back into the planner and get a revised list of steps. This is the "Self-Healing" capability of SPL 2.0.

### (4) Phase 3: Implementation Loop (Heavy Lifting)

Only after the entire design is finalized do we start a second loop for the "Heavy Lifting." In this loop, we generate one file at a time.
- One LLM call = One file.
- This ensures that each file gets the model's full attention and output token budget.

### (5) Deterministic I/O (`CALL write_code_files`)

We use a Python tool to write the generated code to disk immediately. We don't wait for the whole workflow to finish. This means that even if the workflow crashes on the last file, your previous work is safe on disk.

<!-- --- -->

## Running It

This is a "heavy" recipe. It's best to use a strong model like **qwen2.5-coder** or **Claude 3.5 Sonnet**:

```bash
spl run cookbook/12_plan_and_execute/plan_execute.spl \
    --adapter ollama -m qwen2.5-coder \
    --tools cookbook/12_plan_and_execute/tools.py \
    task="Build a REST API for a todo app" \
    output_dir="./todo_app"
```

Expected result: A new directory `./todo_app` containing `main.py`, `models.py`, `requirements.txt`, and a `README.md`.

<!-- --- -->

## What Just Happened

**LLM calls: ~15-20.** (Planning, design steps, file generation, summary)

The "Conductor" (SPL Runtime) managed a complex production pipeline:
1.  **Architected** the solution.
2.  **Validated** each design decision.
3.  **Recovered** from mid-process failures via re-planning.
4.  **Serialized** the final product into individual files on disk.

<!-- --- -->

## Reproducibility Note

On a **GTX 1080 Ti**, this recipe can take **3–5 minutes** to complete. Most of the time is spent in Phase 3 (generating the actual code). 

The output is a **First Draft**. While the structure and logic are usually sound, you should always review the generated files for consistency (e.g., ensuring `main.py` uses the same variable names as `models.py`).

<!-- --- -->

## When to Use This Pattern

Use the **Plan and Execute** pattern when:
- **Multi-File Projects**: Generating any application that requires more than one source file.
- **Complex Logic**: Tasks where the "how" is not immediately obvious and needs to be decomposed.
- **Reliability over Speed**: When you are willing to wait a few minutes for a high-quality, structured result rather than a fast, messy one.

<!-- --- -->

## Exercises

1.  **Add a "Test" Step.** Modify the workflow to include a step at the end that generates a `test_main.py` file based on the implementation in `main.py`.
2.  **Global Consistency Check.** Add a step after Phase 2 that asks a "Reviewer" model to look at *all* the design notes at once and check for contradictions before Phase 3 begins.
3.  **Language Swap.** Try running the task for different languages (e.g., `task="Build a todo app in Go"` or `task="Write a data processing script in Rust"`). Observe how the "Architect" persona adapts the steps.
