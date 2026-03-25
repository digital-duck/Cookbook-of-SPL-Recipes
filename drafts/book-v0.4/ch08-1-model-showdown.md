# Model Showdown

<!-- *"A conductor is only as good as their understanding of each instrument in the orchestra." — Wen Gong* -->

<!-- --- -->

## The Pattern

In the world of LLMs, no single model is the best at everything. One model might excel at creative writing, another at logical reasoning, and a third at being fast and efficient. As a practitioner, your job is to choose the right tool for the task. But how do you compare them objectively?

The manual way is tedious: copy-paste the same prompt into three different chat windows, wait for the responses, and try to keep the differences in your head. 

The SQL analogy is a **Parallel Join** or a **UNION ALL** across different data sources. You want to fetch the same logical entity (the answer) from three different "tables" (the models) and see them side-by-side.

The Model Showdown recipe automates this comparison. It sends the exact same prompt to three different models simultaneously, collects their answers, and then—in a final "judge" step—uses an LLM to evaluate which response was the most effective. This is the foundation of model-agnostic benchmarking.

<!-- --- -->

## The SPL Approach

This recipe introduces the `WORKFLOW` block, which is the powerhouse of SPL 2.0. Unlike a `PROMPT` block, a `WORKFLOW` can have multiple steps, parallel execution branches (`WITH` clauses), and complex logic.

<!-- --- -->

## The .spl File (Annotated)

```spl
-- Recipe 04: Model Showdown
-- Same prompt to multiple Ollama models — compare responses side-by-side.

CREATE FUNCTION compare_responses(            -- (1) Define a reusable template
    prompt TEXT,
    model_1 TEXT, answer_1 TEXT,
    model_2 TEXT, answer_2 TEXT,
    model_3 TEXT, answer_3 TEXT
) RETURNS TEXT AS $$
You are a neutral evaluator comparing responses from three AI models.
... evaluate quality, strengths, and weaknesses ...
$$;

WORKFLOW model_showdown                      -- (2) Define the entry point
    INPUT:                                   -- (3) Declare parameters
        @prompt  TEXT DEFAULT 'What is the meaning of life?',
        @model_1 TEXT DEFAULT 'gemma3',
        @model_2 TEXT DEFAULT 'phi3',
        @model_3 TEXT DEFAULT 'qwen2.5'
    OUTPUT: @comparison TEXT
DO
    WITH                                     -- (4) Parallel execution branch
        response_1 AS (
            PROMPT ask_model_1
            SELECT @prompt AS prompt
            GENERATE answer(prompt)
            USING MODEL @model_1             -- (5) Dynamic model selection
        ),
        response_2 AS (
            PROMPT ask_model_2
            SELECT @prompt AS prompt
            GENERATE answer(prompt)
            USING MODEL @model_2
        ),
        response_3 AS (
            PROMPT ask_model_3
            SELECT @prompt AS prompt
            GENERATE answer(prompt)
            USING MODEL @model_3
        )
    SELECT                                   -- (6) Collect results
        response_1.answer AS answer_1,
        response_2.answer AS answer_2,
        response_3.answer AS answer_3
    INTO @answer_1, @answer_2, @answer_3

    GENERATE compare_responses(              -- (7) The "Judge" step
        @prompt,
        @model_1, @answer_1,
        @model_2, @answer_2,
        @model_3, @answer_3
    ) INTO @comparison

    COMMIT @comparison                       -- (8) Finalize the output
END
```

### (1) `CREATE FUNCTION ... AS $$ ... $$`

In SPL, functions are often used as **Prompt Templates**. Instead of messy string concatenation, you define a block of text with placeholders (like `{prompt}` or `{answer_1}`). When you call the function, SPL injects the data into the template. 

The SQL analogy: A **Stored Procedure** or a **User Defined Function (UDF)** that encapsulates logic for reuse.

### (2) & (3) `WORKFLOW` and `INPUT`

A `WORKFLOW` is a stateful program. It starts with `INPUT` parameters that have types and default values. This is where we declare our "instruments" (@model_1, @model_2, @model_3).

### (4) `WITH ... AS (...)` (Parallel CTEs)

This is a signature feature of SPL 2.0. In SQL, a CTE (`WITH`) is a temporary result set. In SPL, a CTE is a **parallel execution branch**. The runtime fires all three `PROMPT` blocks at the same time. If you have enough VRAM or multiple GPUs, they will run truly in parallel.

### (5) `USING MODEL @model_1`

In previous recipes, we specified the model via the CLI flag `-m`. Here, we specify it *inside the code* using a variable. This allows the workflow to be dynamic—you can swap models by just changing the input parameters.

### (6) `SELECT ... INTO ...`

Once the parallel branches finish, we collect their outputs into workflow-level variables (`@answer_1`, etc.). This is identical to the `SELECT ... INTO` syntax found in PL/SQL or T-SQL.

### (7) The "Judge" Step

We call a final `GENERATE` step using the `compare_responses` template we defined earlier. This step uses the default model (e.g., your strongest model like `gemma3`) to act as the neutral evaluator of the other three.

<!-- --- -->

## Running It

Run the showdown with the default models:

```bash
spl run cookbook/04_model_showdown/showdown.spl --adapter ollama \
    prompt="Explain recursion in 3 sentences"
```

Or override the models to compare specific versions:

```bash
spl run cookbook/04_model_showdown/showdown.spl --adapter ollama \
    prompt="Write a haiku about a GTX 1080 Ti" \
    model_1="llama3.2" model_2="mistral" model_3="qwen2.5"
```

<!-- --- -->

## What Just Happened

**LLM calls: 4.** (3 in parallel + 1 judge step)

The runtime executed the fan-out:
1.  **Branch 1**: Sent prompt to Model A.
2.  **Branch 2**: Sent prompt to Model B.
3.  **Branch 3**: Sent prompt to Model C.
4.  **Synchronization**: The runtime waited for all three to return.
5.  **Judge Step**: Combined all three answers and sent them to the judge model.

This demonstrates the "Conductor" metaphor perfectly. You are the conductor, the models are the orchestra, and the `WORKFLOW` is the score that ensures everyone plays their part at the right time.

<!-- --- -->

## Reproducibility Note

When comparing models, **Latency** becomes a key metric. 
On a **GTX 1080 Ti**, running three models in parallel might slow down generation if they don't all fit in VRAM at once. Ollama handles the swapping, but you will see a performance hit. 

For the most accurate "Model Showdown," run on a system with enough VRAM to hold all models, or use a distributed runtime like **Momagrid** where each model can live on a separate node.

<!-- --- -->

## When to Use This Pattern

Use the **Model Showdown** pattern when:
- **Model Selection**: You are trying to decide which model is best for a specific production task.
- **Regression Testing**: You want to see if a newer version of a model (e.g., Llama 3.1 vs 3.2) actually improves your specific use case.
- **Ensemble Judgment**: You want to avoid the bias of a single model by getting a "second and third opinion."

<!-- --- -->

## Exercises

1.  **Add Latency Tracking.** (Advanced) Research the `context.latency` property and see if you can include the time it took for each model to respond in the final comparison.
2.  **Change the Judge.** Use the `USING MODEL` clause on the final `GENERATE` step to specify a different model for the judge (e.g., `USING MODEL 'gpt-4o'` if using the OpenRouter adapter).
3.  **Variable Prompting.** Modify the recipe so that each model receives a slightly different prompt (e.g., Model 1 gets a "short" instruction, Model 2 gets a "detailed" instruction).
