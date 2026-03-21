# Chapter 9.2 — The Recipe Maker: SPL Eating Its Own Cake

*"The best proof of a cooking method is a meal cooked with it."*

---

## The Concept: What 37 Recipes Taught Us

You have now built 37 recipes. Each one follows the same rhythm.

You identify a task. You find some data. You write a `tools.py` to load and process that data deterministically. You write a `.spl` workflow that CALLs the tools for everything code does better, and GENERATEs with the LLM for everything that genuinely requires reasoning. You write a `readme.md`. You run it, taste it, fix it, run it again.

After doing this 37 times, a pattern emerges that is hard to miss: **every recipe is the same shape**. The data files change. The domain changes. The workflow steps change. But the structure — data catalog, tool layer, workflow, documentation — is invariant.

A SQL practitioner would recognize this immediately. You have discovered a schema. You have been hand-writing the same INSERT statement 37 times. The next move is obvious: write a procedure that generates the INSERT for you.

That procedure is **recipe 00: the recipe-maker**.

The recipe-maker is SPL eating its own cake. It is a workflow that takes a plain-language concept as input and produces a complete, runnable recipe as output — the `.spl` file, the `tools.py`, the sample data, and the documentation. It applies everything the cookbook taught: CALL for deterministic operations, GENERATE only where reasoning is required, grounding with real data before asking the LLM to think.

This is not a parlor trick. It is the natural destination of a mature declarative system: **the abstractions become generative**. Once you can describe a pattern precisely enough to teach it to a reader, you can describe it precisely enough to execute it as code.

---

## Cooking as Science and Art

Before the recipe chapter, a word about expectations — because the recipe-maker is frequently misunderstood on first encounter.

Cooking is both a science and an art. The science gives you reliability: the soufflé rises every time, the bread proofs in 90 minutes, the sauce reduces to the right consistency. The art gives you excellence: the seasoning is right, the plating is thoughtful, the meal is worth eating.

A recipe in a cookbook does the science for you. It tells you the ratios, the temperatures, the timing. It does not give you the art. That requires a cook — someone who tastes as they go, adjusts, learns what "just right" feels like in this kitchen with this oven at this altitude.

The recipe-maker is a recipe for writing recipes. It does the science: it generates a structurally complete workflow, a tools file with the right shape, sample data, and documentation. It solves the **bootstrap problem** — the hardest moment in writing any recipe is facing an empty directory. The recipe-maker eliminates the blank page.

What it does not do is give you the finished dish. The generated workflow will need tuning. The tools will need edge-case handling. The sample data will cover the happy path but not the corners. The CALL/GENERATE split will be close but occasionally wrong. This is expected and normal. The recipe-maker compresses the bootstrap problem, not the craft problem.

Think of it as a first draft from a very well-read sous-chef who has studied all 37 recipes and understands the pattern cold, but has never tasted *your* dish before.

---

## The Full Lifecycle

The recipe-maker introduces a lifecycle that goes beyond the single-run model of the earlier chapters. Where every recipe from 01 to 37 is a linear pipeline — input → generate → commit — the recipe-maker exposes a cycle:

```
concept
    │
    ▼
GENERATE (plan + components)
    │
    ▼
output_dir (workflow.spl, tools.py, data.json, readme.md, recipe_plan.md)
    │
    ▼
--feedback: taste the cake          ← human (default) or llm-judge
    │
    ├── fail → iterate → taste again
    │
    └── pass
            │
            ▼
        --reflect: document lessons learned
            │
            ▼
        --publish: write publication docs + upload to registry
```

Four phases, two gates. The `--reflect` and `--publish` flags only fire on a passing taste — you do not document or distribute a recipe that has not been validated. This is a deliberate design choice: the registry should contain only recipes that work.

Version 1 of the recipe-maker implements the **generate phase** only. The `--feedback`, `--reflect`, and `--publish` phases are scaffolded in the workflow as commented-out blocks, visible and ready to activate. They are described here because they shape how you work with the generated output even before v2 exists: generate, taste manually, iterate, then publish when it's right.

---

## The CLI Contract

The recipe-maker introduces five new CLI concepts that will become the standard interface for production SPL workflows:

```bash
spl2 run cookbook/00_recipe_maker/recipe_maker.spl \
    --adapter ollama -m gemma3 \
    --tools cookbook/00_recipe_maker/tools.py \
    concept="Customer churn predictor with SHAP explainability" \
    output_dir="cookbook/38_churn_predictor/" \
    dataset="data/customers.csv" \
    resources="references/churn_taxonomy.md" \
    feedback=human
```

Each flag has a role:

| Flag | Layer | Purpose |
|---|---|---|
| `--adapter / -m` | Generative | Which LLM does the creative work |
| `--tools` | Deterministic | Which Python tools handle the code work |
| `dataset=` | Data | Local file (JSON/CSV/TXT) or connection string the recipe will operate on |
| `resources=` | Knowledge | Reference material, domain docs, related work — grounding for the planner |
| `output_dir=` | Artifacts | Where generated files are written |
| `feedback=` | Validation | `human` (default, stops for review) or `llm-judge` (v2) |
| `concept=` | Intent | Plain-language description — what the recipe should do |

If you squint, this is a compiler invocation. `concept` is the source. `output_dir` is the binary. `--adapter` is the compiler backend. `--tools` is the standard library. `dataset` and `resources` are the headers.

---

## Chapter 9.2 — Recipe 00: Recipe Maker

### The Pattern

You have been writing the same structural shape 37 times. Each time: create a data directory, write a `tools.py` with a `load_X()`, a `list_X()`, and processing tools, write a `.spl` workflow that CALLs the tools and GENERATEs with the LLM, write a `readme.md`.

The naive approach is to keep writing this by hand. It is not painful exactly — each recipe is different enough that hand-crafting is satisfying. But it is slow, and the structural parts (file layout, tool scaffolding, readme sections) are not where the creativity lives. They are ceremony.

The recipe-maker is the ceremony automator. Given a concept, it generates the complete recipe skeleton — not perfect, not finished, but structurally sound and immediately runnable. You spend your time on the craft: tuning the GENERATE step names, adding edge cases to the data, adjusting the CALL/GENERATE split. The scaffolding is already there.

### The SPL Approach

The recipe-maker is itself a recipe: CALL to load the pattern catalog and user-supplied context, GENERATE to plan and create each component, CALL to write all artifacts to disk and notify for review.

It demonstrates the core principle of the entire cookbook in miniature: **every step that does not require reasoning is a CALL; every step that does is a GENERATE**. The file I/O, the pattern lookup, the artifact writing, the review formatting — all CALL. The planning, the workflow generation, the tools generation, the data generation, the documentation — all GENERATE, each grounded by the deterministic context loaded before it.

### The .spl File (Annotated)

```spl2
-- Recipe 00: Recipe Maker (Meta-Recipe)
-- SPL 2.0 eating its own cake.

-- System context functions injected as LLM system prompts — zero LLM cost.
-- These ground every GENERATE step with precise expectations.

CREATE FUNCTION spl_syntax_guide()        -- teaches the LLM exact SPL syntax
RETURNS TEXT AS $$ ... $$;

CREATE FUNCTION tools_py_guide()           -- teaches the LLM the @spl_tool pattern
RETURNS TEXT AS $$ ... $$;

CREATE FUNCTION recipe_quality_rubric()    -- defines what "complete recipe" means
RETURNS TEXT AS $$ ... $$;

WORKFLOW recipe_maker
    INPUT:  @concept     TEXT DEFAULT '',       -- the recipe idea, in plain language
            @output_dir  TEXT DEFAULT 'cookbook/output/',
            @dataset     TEXT DEFAULT '',        -- optional: path to real data
            @resources   TEXT DEFAULT '',        -- optional: reference material
            @feedback    TEXT DEFAULT 'human'    -- validation mode
    OUTPUT: @review_notification TEXT
DO
    -- Phase 1: Load context — all CALL, zero LLM cost
    CALL load_patterns('')    INTO @patterns_catalog  -- 11 patterns from the cookbook
    CALL load_dataset(@dataset)   INTO @dataset_context  -- real data as grounding
    CALL load_resources(@resources) INTO @resources_context

    -- Phase 2: Plan — LLM understands intent and chooses the right pattern
    -- Grounded by: pattern catalog + quality rubric + user data context
    GENERATE plan_recipe(
        @concept,
        @patterns_catalog,
        @dataset_context,
        @resources_context,
        recipe_quality_rubric()
    ) INTO @recipe_plan

    -- Phase 3: Generate components — each GENERATE grounded by the plan
    -- SPL syntax guide prevents the LLM from inventing non-existent syntax
    GENERATE generate_spl_workflow(
        @recipe_plan, @concept, spl_syntax_guide()
    ) INTO @spl_content

    -- Tools guide ensures @spl_tool decorator, str parameters, str return types
    GENERATE generate_tools_py(
        @recipe_plan, @concept, @dataset_context, tools_py_guide()
    ) INTO @tools_content

    -- Dataset grounded by user-supplied data if provided
    GENERATE generate_sample_data(
        @recipe_plan, @concept, @dataset_context
    ) INTO @data_content

    -- Readme grounded by the actual generated artifacts, not the plan
    GENERATE generate_readme(
        @recipe_plan, @concept, @spl_content, @tools_content,
        recipe_quality_rubric()
    ) INTO @readme_content

    -- Phase 4: Write artifacts — all CALL, zero LLM cost
    CALL write_artifact(@output_dir, 'workflow.spl',    @spl_content)   INTO @_
    CALL write_artifact(@output_dir, 'tools.py',        @tools_content) INTO @_
    CALL write_artifact(@output_dir, 'data.json',       @data_content)  INTO @_
    CALL write_artifact(@output_dir, 'readme.md',       @readme_content) INTO @_
    CALL write_artifact(@output_dir, 'recipe_plan.md',  @recipe_plan)   INTO @_

    -- Phase 5: Summarise and notify — all CALL, zero LLM cost
    CALL list_artifacts(@output_dir)                              INTO @artifact_list
    CALL notify_review(@output_dir, @artifact_list, @feedback)   INTO @review_notification

    COMMIT @review_notification WITH
        status     = 'awaiting_review',
        concept    = @concept,
        output_dir = @output_dir

    -- ── v2 Placeholders (feedback → reflect → publish) ──────────────────
    -- [v2] GENERATE validate_artifacts(...) INTO @validation
    -- [v2] EVALUATE @validation
    --          WHEN 'pass' THEN
    --              GENERATE reflect(...)   INTO @reflection
    --              GENERATE publish_writeup(...) INTO @writeup
    --              CALL register_recipe(...)
    --          WHEN 'fail' THEN RETRY
    -- [v2] END

EXCEPTION
    WHEN GenerationError THEN
        COMMIT 'Recipe generation failed. Check the concept description and try again.'
            WITH status = 'error', concept = @concept
END
```

The SQL analogy: `load_patterns()` is a lookup join against the pattern catalog. `plan_recipe()` is the query planner. The four `generate_*` steps are the column projections. The `write_artifact()` calls are the INSERT INTO OUTPUT TABLE. `notify_review()` is the audit log entry.

### Running It

```bash
spl2 run cookbook/00_recipe_maker/recipe_maker.spl \
    --adapter ollama -m gemma3 \
    --tools cookbook/00_recipe_maker/tools.py \
    concept="Interview simulator for data science roles with scoring rubric" \
    output_dir="/tmp/spl_recipes/ds_interview/"
```

Expected output (abbreviated):

```
RECIPE GENERATION COMPLETE
────────────────────────────────────────────────────────────────────
GENERATED ARTIFACTS in /tmp/spl_recipes/ds_interview/

  data.json                          2,841 bytes
  readme.md                          4,203 bytes
  recipe_plan.md                     1,876 bytes
  tools.py                           5,512 bytes
  workflow.spl                       3,940 bytes

  Total: 5 file(s), 18,372 bytes
────────────────────────────────────────────────────────────────────

NEXT STEPS — Human Review Required:

  1. Review the generated artifacts in:
     /tmp/spl_recipes/ds_interview/

  2. Run the generated workflow:
     spl2 run /tmp/spl_recipes/ds_interview/workflow.spl
        --adapter ollama -m <model>
        --tools /tmp/spl_recipes/ds_interview/tools.py

  3. Taste the cake — does it produce the expected output?

  4. If satisfied: re-run with --reflect and --publish flags (v2).
     If not: edit the artifacts and re-run with your corrections.

  Status: awaiting_human_review
```

Total LLM calls: **5** (plan + spl + tools + data + readme). Everything else is deterministic Python.

### What Just Happened

The workflow made exactly 5 LLM calls, in sequence:

1. **`plan_recipe`** — the most important call. The LLM read the pattern catalog, the quality rubric, and the concept description. It produced a structured plan naming the pattern (`multi_persona`), the workflow inputs and outputs, the GENERATE steps needed, the tools required, and the shape of the sample data. This plan becomes the grounding context for every subsequent call.

2. **`generate_spl_workflow`** — the LLM wrote the `.spl` file, guided by the recipe plan and the `spl_syntax_guide()` context function that teaches exact SPL syntax. Without the syntax guide, the LLM would invent plausible but invalid clauses.

3. **`generate_tools_py`** — the LLM wrote the tools file, guided by the `tools_py_guide()` context that specifies `@spl_tool` decoration, `str` parameter types, and `str` return types. The dataset context (if provided) shaped the data-loading functions.

4. **`generate_sample_data`** — the LLM generated realistic sample records that match the data schema described in the plan.

5. **`generate_readme`** — the LLM documented the recipe, receiving the actual generated `.spl` and `tools.py` content as input rather than just the plan. This means the readme reflects what was actually generated, not what was intended.

All five calls are grounded: none asks the LLM to reason from scratch. Each receives the accumulated context from the steps before it. This is the chain pattern (recipe 09) applied to the recipe-making process itself.

After the five LLM calls, `write_artifact()` is called five times (one per file), `list_artifacts()` produces the bundle summary, and `notify_review()` formats the human-facing output. Zero additional LLM cost.

### Reproducibility Note

Latency varies significantly with concept complexity. A simple extraction recipe concept (`"Extract structured fields from invoice text"`) plans and generates in 45–90 seconds on a GTX 1080 Ti with gemma3. A complex multi-persona concept (`"Interview simulator with role catalog, candidate profiles, and scoring rubric"`) takes 2–4 minutes — the plan step alone requires reasoning across all 11 patterns and the full quality rubric.

CV% is higher than most earlier recipes because the plan step involves genuine reasoning that varies run-to-run. Two runs of the same concept will produce structurally similar but not identical output. This is expected: the recipe-maker is a creative tool, not a deterministic one. What matters is whether the output is runnable and close to the target, not whether it is identical across runs.

Run with a stronger model (`-m mistral` or `--adapter claude_cli -m claude-sonnet-4-6`) for more reliable plan quality on complex concepts.

### When to Use This Pattern

The recipe-maker is the right tool when you are facing a blank directory and a concept description. Use it to:

- **Bootstrap a new recipe** from a concept you have not implemented before
- **Recreate an existing recipe** to measure how close the generator gets — this is the calibration test: run the recipe-maker against a concept whose ground truth you know
- **Iterate on an existing recipe** by providing the original `.spl` and `tools.py` as `resources=` — the generator will treat them as reference and produce a closer first draft
- **Teach the pattern to a new team member** — `recipe_plan.md` explains the LLM's reasoning at each step, making it a readable design document even before the recipe is complete

Do not use the recipe-maker when:

- The recipe is a minor variation of an existing one — editing the original is faster than generating from scratch
- The concept is vague — the quality of the plan is proportional to the specificity of the concept; `"something with sentiment"` will produce a worse plan than `"batch sentiment classifier for customer support tickets with urgency scoring"`
- You need a production-ready artifact on the first run — the recipe-maker produces a baseline, not a finished dish

### Exercises

1. **The calibration run.** Run the recipe-maker with `concept="Customer support triage with order lookup and response drafting"` and `output_dir` pointing to a fresh directory. Compare the generated workflow to `28_support_triage`. Count how many lines you would need to change to reach parity. This number is your current recipe-maker quality score.

2. **Dataset grounding.** Re-run the calibration with `dataset="cookbook/28_support_triage/orders.json"` added. Does the generated `data.json` more closely match the original? Does the `tools.py` get the schema right?

3. **Concept refinement.** Take a concept that produced a poor plan in your first run. Improve the concept description — add domain vocabulary, specify the pattern explicitly, name the data schema. Observe how much the plan quality improves. The lesson: the recipe-maker multiplies the quality of your concept, it does not replace it.

4. **Swap the model.** Run the same concept with `--adapter ollama -m mistral` and then with `--adapter claude_cli -m claude-sonnet-4-6`. Compare the plans. Stronger models produce better structural reasoning; the pattern catalog and rubric grounding matter more on weaker models.

---

## A Note on What This Means

Thirty-seven recipes in, you have a tool that writes recipes. This is not the end of the cookbook — it is the beginning of a second order of productivity.

The recipes you write by hand will always be better than the recipes the recipe-maker generates on the first pass. You know the domain. You understand the edge cases. You have taste. The recipe-maker does not have taste; it has pattern recognition and grounding.

What the recipe-maker gives you is **the bootstrap**. The blank-page problem vanishes. The structural ceremony is automated. The first draft exists in the time it takes to run five LLM calls. What remains is the craft: reading `recipe_plan.md`, running the generated workflow, tasting the output, adjusting the seasoning, running again.

This is the conductor's work. The score is written. Now it needs to be played.

---

*Next: Chapter 9.3 — The Road Ahead: Declarative AI, Momagrid, and Where SPL Fits*
