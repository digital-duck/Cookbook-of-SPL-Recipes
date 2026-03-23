# Multi-Model Pipeline

<!-- *"Choose the right instrument for each movement of the symphony." — Wen Gong* -->

<!-- --- -->

## The Pattern

In a world of thousands of models, the most common mistake is using a "Titan" (like GPT-4o or Claude 3.5 Sonnet) for every single step. While these models are brilliant, they are also slower and more expensive. For many sub-tasks—like basic research, simple summarization, or formatting—a "Junior" model (like Phi-4 or Llama 3.2) can do the job just as well, at a fraction of the cost.

The **Multi-Model Pipeline** pattern is the practice of routing different steps of a workflow to different models based on the task's requirements. 
- Use a **Fast Model** for data retrieval.
- Use a **Reasoning Model** for deep analysis.
- Use a **Creative Model** for final prose.

The SQL analogy is **Polyglot Persistence** or **Federated Queries**. You don't store everything in one massive database. You put your structured data in PostgreSQL, your logs in Elasticsearch, and your cache in Redis. When you run a "query" (the workflow), the system fetches data from the most efficient source for that specific piece of information.

The Multi-Model Pipeline recipe (Recipe 21) demonstrates this "Best-of-Breed" orchestration. It routes research, analysis, and writing to the models most suited for those roles, then wraps them in a quality-control loop.

<!-- --- -->

## The SPL Approach

This recipe introduces the `USING MODEL` clause at the step level, allowing for granular control over the "orchestra."

<!-- --- -->

## The .spl File (Annotated)

```spl
-- Recipe 21: Multi-Model Pipeline
-- Each step targets the model best suited for that task.

WORKFLOW multi_model_pipeline
  INPUT: @topic TEXT
DO
  -- Step 1: Research (Needs factual retrieval)
  GENERATE research(@topic) 
    USING MODEL 'gemma3' INTO @facts;        -- (1) Fast, retrieval-tuned model

  -- Step 2: Analysis (Needs deep reasoning)
  GENERATE analyze(@facts) 
    USING MODEL 'claude-3-5-sonnet' INTO @analysis; -- (2) High-intelligence model

  -- Step 3: Writing (Needs creative style)
  GENERATE write_summary(@analysis) 
    USING MODEL 'llama3.2' INTO @draft;      -- (3) Creative, lightweight model

  -- Step 4: Quality loop
  WHILE @iteration < 3 DO
    GENERATE quality_check(@draft) 
      USING MODEL 'gemma3' INTO @quality;    -- (4) Neutral judge model

    EVALUATE @quality
      WHEN > 0.7 THEN COMMIT @draft
      OTHERWISE
        GENERATE write_summary(@analysis) INTO @draft
        @iteration := @iteration + 1
    END
  END
END
```

### (1) Step 1: Fast Retrieval

For the research phase, we want speed and factual breadth. We target **gemma3** (or a similar local model). This model is excellent at scanning its training data and producing a bulleted list of facts without the latency of a massive cloud model.

### (2) Step 2: Deep Reasoning

For the analysis, we need the "Gold Standard." We use `USING MODEL 'claude-3-5-sonnet'` (via the OpenRouter or Claude adapter). This model's ability to identify subtle trends and risks is superior to smaller models. We are spending our "token budget" where it matters most.

### (3) Step 3: Creative Writing

For the final summary, we might want a specific tone. **Llama 3.2** is known for being conversational and engaging. By switching to a smaller model here, we get the response faster and often with less "corporate" phrasing than the larger frontier models.

### (4) Step 4: The Neutral Judge

Finally, we use a different model (**gemma3** again) to perform the quality check. Using a different model for the judge step prevents "Confirmation Bias"—where a model is too lenient on its own work.

SQL Analogy: **Cross-Engine Join**. You are joining the output of Model A with the judgment of Model B to produce a refined final result.

<!-- --- -->

## Running It

This recipe highlights the power of adapters. Ensure you have your keys configured for cloud models if you choose to use them:

```bash
spl run cookbook/21_multi_model_pipeline/multi_model.spl --adapter openrouter \
    topic="The impact of AI on rural education"
```

In the execution trace, you will see the runtime switching between adapters and model names for each `GENERATE` step.

<!-- --- -->

## What Just Happened

**LLM calls: 4 + (2 * iterations).**

The "Conductor" (SPL Runtime) orchestrated a specialized team:
1.  **Commissioned** research from a fast specialist.
2.  **Requested** analysis from a high-intelligence consultant.
3.  **Hired** a creative writer for the final draft.
4.  **Audited** the work using an independent third party.

This is the peak of agentic design: not just using AI, but using the *right* AI for every single turn.

<!-- --- -->

## Reproducibility Note

The Multi-Model pattern is the most **Cost-Efficient** way to achieve high quality. 
By routing 80% of the tokens to smaller, cheaper models and reserving the remaining 20% for the "frontier" models, you can achieve "GPT-4 level" results at "GPT-3.5 level" costs.

On a **GTX 1080 Ti**, the local steps (Research, Judge) run in **2–5 seconds**, while the cloud steps (Analysis) depend on your internet connection and the provider's latency.

<!-- --- -->

## When to Use This Pattern

Use the **Multi-Model Pipeline** pattern when:
- **Cost/Performance Balance**: You need high quality but want to keep API costs low.
- **Latency Optimization**: You want the user to see the "Researching..." phase happen instantly while the deep thinking happens in the background.
- **Ensemble Benchmarking**: When you want to see how different models "view" each other's work.

<!-- --- -->

## Exercises

1.  **Local-Only Mode.** Modify the recipe to use only local models (e.g., `phi4` for research, `gemma3` for analysis, `mistral` for writing). Compare the quality to the cloud-mixed version.
2.  **Add a "Model Switcher."** (Advanced) Use an `EVALUATE` block to check the complexity of the `@topic`. If it's "simple," use a fast model for all steps. If it's "complex," switch to the full multi-model pipeline.
3.  **Parallel Multi-Model.** Use a `WITH` clause to ask two different models for the Research phase and then have the Analyst merge their findings.
