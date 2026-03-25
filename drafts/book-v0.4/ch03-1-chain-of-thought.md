# Chain of Thought

### The Pattern

You have a topic — "distributed AI inference," say — and you want not just a surface summary but a piece of writing that demonstrates actual reasoning. The naive Python approach is a single `requests.post` to the LLM with an instruction like "think carefully and then summarise." Sometimes it works. More often you get a paragraph that opens confidently, wanders, and concludes with something vague. The model has to do the research thinking, the analytical thinking, and the synthesis all in one forward pass, which is a lot to ask. Debugging it is worse: when the output is thin, you cannot tell whether the model failed to surface facts, failed to analyse them, or failed to compress the analysis. The whole thing is a black box.

The sharper practitioners will try prompt engineering — "first list what you know, then analyse, then summarise" — inside a single GENERATE call. This helps, but you still cannot inspect intermediate results, you cannot swap a better research prompt later without re-testing the whole pipeline, and you lose the ability to halt early if step one produces garbage. You are also paying for tokens in steps two and three that are built on a shaky foundation you cannot see.

The recurring pain is that reasoning is not a single act. It is a sequence of acts, each contingent on the one before. Compressing that sequence into one LLM call trades controllability for convenience, and in practice the convenience is illusory — you end up debugging by staring at final output and guessing.

### The SPL Approach

Model the reasoning stages explicitly as a linear chain of GENERATE steps, threading each output as context for the next, so that Research feeds Analysis and Analysis feeds Synthesis — a CTE chain written for thought instead of tables.

### The .spl File (Annotated)

```sql
-- Recipe 09: Chain of Thought
-- Multi-step reasoning: Research → Analyze → Summarize
-- Each GENERATE feeds into the next via workflow variables.
--
-- Usage:
--   spl run cookbook/09_chain_of_thought/chain.spl \
--       --adapter ollama -m gemma3 \
--       topic="distributed AI inference"

WORKFLOW chain_of_thought
    INPUT:  @topic TEXT        -- The subject to reason about; caller decides, not the workflow.
    OUTPUT: @summary TEXT      -- Final synthesised output; the only thing the caller receives.
DO
    -- Step 1: Research
    -- The model's job here is narrow: surface what is known about @topic.
    -- Analogous to: WITH research AS (SELECT facts FROM knowledge WHERE subject = @topic)
    GENERATE research(@topic) INTO @research

    -- Step 2: Analyze
    -- @research is now in scope. The model cannot "forget" what was surfaced;
    -- it must reason from it. Narrow job: find patterns, tensions, implications.
    -- Analogous to: WITH analysis AS (SELECT interpret(facts) FROM research)
    GENERATE analyze(@research) INTO @analysis

    -- Step 3: Summarize
    -- The model works from @analysis, not from @topic directly.
    -- This is the key difference from a single-prompt approach: the summary
    -- is grounded in the analysis, which is grounded in the research.
    -- Analogous to: SELECT synthesize(interpretation) FROM analysis
    GENERATE summarize(@analysis) INTO @summary

    -- Commit the final variable. status metadata travels with the result.
    COMMIT @summary WITH status = 'complete'
END
```

**On the SQL analogy.** In SQL you write:

```sql
WITH research  AS (SELECT facts        FROM knowledge WHERE subject = :topic),
     analysis  AS (SELECT interpret(f) FROM research),
     summary   AS (SELECT compress(i)  FROM analysis)
SELECT * FROM summary;
```

Each CTE can only see what the previous one produced. There is no way for `summary` to reach back past `analysis` and pull raw `facts` — the chain forces discipline. The SPL chain works identically: `@summary` is computed from `@analysis`, which was computed from `@research`. You cannot accidentally skip a step.

**Why three variables instead of one?** Because each is individually inspectable. After a run you can log `@research`, `@analysis`, and `@summary` separately. If the summary is thin, you check the analysis first. If the analysis is thin, you check the research. The isolation of failure modes is the point.

**On INPUT design.** `@topic` is the only input. The workflow does not hard-code "distributed AI inference" or set a default — the caller decides what to reason about. This respects a core SPL principle: a workflow specifies the shape of the computation, not the subject matter.

**On GENERATE prompt resolution.** Each GENERATE call (`research`, `analyze`, `summarize`) corresponds to a prompt template that the runtime resolves. In the absence of explicit `CREATE FUNCTION` definitions in this file, the runtime uses the step name and arguments to construct the system and user prompts. The practical implication: you can override any one prompt — say, swapping `analyze` for a domain-specific analysis prompt — without touching the others.

**On COMMIT.** `COMMIT @summary WITH status = 'complete'` writes the result to the output store with a status label. The workflow has no EXCEPTION block. This is deliberate for a recipe at this stage of complexity: the chain of thought pattern is the mechanism; safety wrapping is a separate concern handled in Part 4.

### Running It

```bash
spl run cookbook/09_chain_of_thought/chain.spl \
    --adapter ollama -m gemma3 \
    topic="distributed AI inference"
```

Expected output (truncated — your model's phrasing will differ):

```
[chain_of_thought] Running on topic: "distributed AI inference"

[research] Generating...
  Distributed AI inference refers to the practice of spreading model
  execution across multiple nodes or devices rather than centralising
  computation on a single server. Key considerations include network
  latency between nodes, model partitioning strategies (tensor parallel,
  pipeline parallel), memory bandwidth constraints at edge devices...
  [~340 tokens]

[analyze] Generating...
  Three tensions emerge from the research. First, latency vs. throughput:
  distributing a single request across nodes adds coordination overhead
  that can exceed the gains from parallelism unless batch sizes are large.
  Second, model size vs. edge capability: the economics favour distribution
  only when individual nodes cannot host the full model...
  [~280 tokens]

[summarize] Generating...
  Distributed AI inference becomes economically and technically compelling
  when model size exceeds single-node memory, batching is feasible, and
  network topology is controlled. For latency-sensitive single-request
  workloads, a well-provisioned central server typically wins...
  [~180 tokens]

status: complete
```

### What Just Happened

Three LLM calls were made, in strict sequence. No LLM call was made for anything other than reasoning — there is no CALL in this workflow, because there is no deterministic tool work to do.

**Step 1 (research):** The model received `@topic` and was asked to surface relevant knowledge. The output went into `@research` — a variable that exists only inside this workflow run.

**Step 2 (analyze):** The model received `@research`. It had no access to `@topic` directly (unless the prompt template passes it through, which in this recipe it does not). The model's task was narrowed to interpretation of the material already surfaced.

**Step 3 (summarize):** The model received `@analysis`. Its task was compression and synthesis. By this point, the chain has done the work of separating "what do we know" from "what does it mean" from "what is the bottom line" — three jobs that, when conflated, produce the bland summary we were trying to avoid.

**COMMIT:** Writes `@summary` to the output store with `status = 'complete'`. The caller receives `@summary` as the workflow's declared OUTPUT.

**Token budget awareness.** Three GENERATE calls means three round-trips to the model. For a local model on a GTX 1080 Ti this is noticeable — roughly 12–20 seconds total depending on output length. For a production API it is three billing events. This is the cost of the pattern. It is worth it when the quality gain matters; for a quick lookup it is not.

### Reproducibility Note

Tested on a GTX 1080 Ti with gemma3 (4-bit quantised) via Ollama. End-to-end latency for `topic="distributed AI inference"`: approximately 14 seconds. For `topic="quantum computing"` with llama3.2: approximately 18 seconds.

Output stability: the structure of the chain (research → analysis → summary) is stable across runs. The specific phrasing of each step varies, as expected from generative models. The summary at step three tends to be more focused and grounded than a single-prompt alternative because it inherits the structure imposed by step two.

If you need bit-for-bit reproducibility, set `temperature=0` on all three GENERATE calls. You will lose some expressiveness but gain determinism within a given model version. Note that model updates will still change output even at temperature zero.

One observed failure mode: if `@topic` is extremely broad ("everything about AI"), the research step produces a sprawling dump that overwhelms the analysis step, which then produces a similarly sprawling analysis, and the summary step cannot compress it coherently. Keep topics scoped. The workflow does not enforce this — that is the caller's responsibility.

### When to Use This Pattern

**Use chain of thought when:**

- The task has identifiable reasoning stages that benefit from isolation (research / analysis / synthesis; hypothesis / evidence / conclusion; diagnosis / differential / recommendation).
- You want to inspect intermediate reasoning, not just final output.
- You expect to iterate on individual stages — for example, replacing the analysis prompt with a domain-specific one — without re-engineering the whole pipeline.
- Output quality is more important than token economy.

**Do not use chain of thought when:**

- A single, well-crafted prompt reliably produces the quality you need. Complexity for its own sake is expensive.
- Latency is the binding constraint. Three sequential LLM calls compound latency. If you need a fast answer and quality is acceptable from one pass, use one pass.
- The stages are not genuinely sequential. If step two does not depend on step one's output, they should run in parallel (see Chapter 4.2, Tree of Thought, which explores parallel path generation before convergence).

**Comparison with alternatives:**

| Approach | Quality | Latency | Debuggability |
|---|---|---|---|
| Single GENERATE | Variable | Low | Poor |
| Chain of Thought (this recipe) | Higher | Medium | Good |
| Tree of Thought (Recipe 17) | Highest | High | Good |

The chain of thought pattern is the minimum viable structure for tasks where reasoning quality matters. Tree of thought adds parallel exploration when you are uncertain which reasoning path is best. Chain of thought assumes you know the right sequence of reasoning acts; tree of thought does not.

### Exercises

1. **Add a fourth step.** After `summarize`, add `GENERATE critique(@summary, @topic) INTO @critique` that asks the model to identify the weakest claim in the summary. Then `COMMIT @critique WITH status = 'critique'`. Run both the original and the extended version; compare whether the critique surfaces anything the single-prompt approach would have missed.

2. **Swap the analysis prompt.** The `analyze` step uses the default prompt template. Create a `CREATE FUNCTION analysis_prompt() RETURNS TEXT` that specialises the analysis for a domain of your choice (security, economics, biology). Pass it to `GENERATE analyze(@research, analysis_prompt()) INTO @analysis`. Observe how specialising one stage changes the downstream summary without touching any other step.

3. **Fail gracefully.** Wrap the workflow in an EXCEPTION block. Add `WHEN GenerationError THEN COMMIT @research WITH status = 'research_only'` — so that if the analysis or summary step fails, the caller still receives the research output rather than nothing. This is the starting point for understanding the safety patterns in Part 4.
