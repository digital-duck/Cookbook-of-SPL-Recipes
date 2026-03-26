# Hello World

<!-- *"Before you cook anything, you verify that the stove is on." — Wen Gong* -->

<!-- --- -->

## The Pattern

Every technology stack demands a ritual: write the simplest possible program, run it, and confirm that the scaffolding holds. SPL is no different. Before you write a multi-step workflow that CALLs tools and GENERATEs structured output, you need to know that `spl` is installed, the adapter is configured, the model is running, and the runtime can connect them end to end.

The naive approach is to write a Python script: import the Ollama client, define a system message, send the request, print the response. It works. It also requires you to manage the HTTP client, handle the response envelope, deal with streaming vs. non-streaming modes, and remember the exact API shape of whichever model host you are using. For a sanity check, that is too much ceremony.

In SQL, the equivalent sanity check is:

```sql
SELECT 'hello' FROM dual;
```

One row. One column. Confirms the connection is live, the parser understood you, and the engine returned data. No tables, no joins, no logic. Just proof that the pipe works.

SPL's hello world is exactly that: one `PROMPT` block, one `GENERATE` call, no parameters, no tools, no state management. If it runs and returns text, the stack is healthy.

<!-- --- -->

## The SPL Approach

A `PROMPT` block assembles context in a `SELECT` clause, then fires a single `GENERATE` call into the assembled context. The model reads the context and produces the response. One LLM call, no moving parts.

<!-- --- -->

## The .spl File (Annotated)

```spl
-- Recipe 01: Hello World
-- Minimal SPL program — verify spl + adapter + model work.
--
-- Usage:
--   spl run cookbook/01_hello_world/hello.spl
--   spl run cookbook/01_hello_world/hello.spl --adapter ollama
--   spl run cookbook/01_hello_world/hello.spl --adapter ollama -m gemma3

PROMPT hello_world                           -- (1) declare a named PROMPT block
SELECT
    system_role('You are a friendly assistant. Introduce yourself and SPL 2.0 in two sentences.')
                                             -- (2) assemble context in SELECT
GENERATE greeting()                          -- (3) fire the LLM call
```

Three lines of logic. Here is what each one does.

### (1) `PROMPT hello_world`

`PROMPT` is the simplest SPL construct. It is a single-step program: select context, generate response, done. You can think of it as a named view — it has a name that the runtime uses for logging and tracing, but it takes no parameters and returns one result.

The SQL analogy is a named query or a view with no `WHERE` clause:

```sql
CREATE VIEW hello_world AS
SELECT 'hello from the database';
```

You are not filtering. You are not joining. You are simply declaring what this block does and giving it a name the runtime can track.

### (2) `SELECT system_role(...)`

The `SELECT` clause in a `PROMPT` block assembles the context that will be given to the LLM when `GENERATE` fires. Each item in the `SELECT` is a piece of context: a system instruction, a user input, a retrieved document, a computed value.

`system_role()` is a built-in SPL function that wraps its argument as a system-level instruction. In most LLM APIs, the system message establishes the model's role, constraints, and persona — it is the part of the conversation that precedes any user turn. Putting your instruction in `system_role()` signals to the adapter that this text should be injected at the system level, not as user input.

The SQL analogy: the `SELECT` clause computes what you hand to the LLM, just as a SQL `SELECT` computes what you return to the caller. Here, you are computing exactly one thing: a system instruction string. That string becomes the model's full context for this prompt.

In later recipes, the `SELECT` clause will grow — you will add `context.param AS column_name`, `function_call() AS context_label`, and multiple joined context items. The structure is always the same: `SELECT` assembles a context row, `GENERATE` sends it to the model.

### (3) `GENERATE greeting()`

`GENERATE` is an LLM call. It takes the context assembled by `SELECT`, sends it to the configured adapter, waits for the response, and makes the result available to the rest of the workflow.

`greeting()` is the step name, not a function you defined. It is how this call appears in logs, traces, and error messages. Choose step names that describe what the model is doing, not what you are hoping for.

The parentheses can accept arguments — in later recipes you will pass `GENERATE classify(text, examples)` or `GENERATE translate(content, target_language)`. In this recipe, there are no arguments because the entire context is in the `SELECT` clause. The `GENERATE` step sends whatever `SELECT` assembled.

The SQL analogy:

```spl
-- SQL: compute a value
SELECT UPPER('hello world') AS result;

-- SPL: generate a value using the LLM
GENERATE greeting()
```

`UPPER()` is deterministic. `greeting()` is not. That is the entire difference. Both take input from what `SELECT` assembled. Both produce a value the runtime captures.

**The critical distinction**: SPL uses `GENERATE` for operations that require reasoning, language, or judgment — things only a model can do. It uses `CALL` for deterministic operations: loading files, computing checksums, looking up values, writing output. In hello world, you have one GENERATE and no CALLs, because the entire task is generative. Later recipes will mix them, and the discipline of separating them is where most of the design work lives.

<!-- --- -->

## Running It

Ensure Ollama is running and gemma3 is pulled:

```bash
ollama serve          # if not already running as a service
ollama pull gemma3    # one-time download, ~5 GB
```

Run the recipe:

```bash
spl run cookbook/01_hello_world/hello.spl --adapter ollama -m gemma3
```

Expected output (text will vary across runs):

```output
Hello! I'm Gemma, a helpful AI assistant developed by Google DeepMind.
SPL 2.0, or Structured Prompt Language, is a declarative language for
orchestrating LLM workflows — think SQL for AI pipelines.
```

The response is printed to stdout. No files are written, no state is committed. This is a pure read operation.

You can also run without specifying an adapter if Ollama is your configured default:

```bash
spl run cookbook/01_hello_world/hello.spl
```

And you can swap models without changing the file:

```bash
spl run cookbook/01_hello_world/hello.spl --adapter ollama -m llama3.2
spl run cookbook/01_hello_world/hello.spl --adapter ollama -m mistral
```

The `.spl` file does not change. The adapter and model are runtime concerns, not workflow concerns. This is an early demonstration of a principle that pays off in later recipes: SPL workflows are model-agnostic by design.

<!-- --- -->

## What Just Happened

**LLM calls: 1.**

The runtime parsed `hello.spl`, identified the `PROMPT hello_world` block, assembled the context from the `SELECT` clause (one system instruction string), and handed it to the Ollama adapter with a request to the gemma3 model. The model generated a response. The runtime printed it and exited.

No files were read. No tools ran. No variables were set. No exception handlers were evaluated.

This is the minimal path through the SPL runtime. Every more complex recipe is this path plus additional steps layered on top:

- `WORKFLOW` blocks add `INPUT` parameters and multi-step sequences
- `CALL` steps add deterministic operations alongside the generative ones
- `EVALUATE` adds branching on model output
- `COMMIT` adds persistence
- `EXCEPTION` adds error handling

None of those are present here. Hello world establishes the floor: `PROMPT` + `SELECT` + `GENERATE` = one model call, one response, done.

<!-- --- -->

## Reproducibility Note

Latency on a GTX 1080 Ti with gemma3: **3–8 seconds** for a two-sentence response. The range is wide because a cold Ollama server will load the model weights into VRAM on the first call — subsequent calls in the same session are faster once the model is warm.

The response content varies across runs. The model is not seeded to a fixed random state, so each run produces a different phrasing. This is expected and correct for a generative sanity check. What you are verifying is not the exact text but that text arrives at all.

If you need reproducible output for a test: set `temperature=0` via the adapter configuration, or use a workflow with structured output constraints (see Chapter 2.4). For a hello world, variability is not a problem — it is confirmation that the model is actually generating, not returning a cached string.

<!-- --- -->

## When to Use This Pattern

The `PROMPT` form — `PROMPT name / SELECT context / GENERATE step()` — is the right shape for:

- **Stack verification**: Confirm the runtime, adapter, and model are wired together correctly before writing anything more complex.
- **One-shot queries**: A single natural-language question that needs one LLM response and no post-processing. The Ollama proxy recipe (Chapter 2.2) extends this pattern with a parameter.
- **Prototyping a system message**: When you are tuning the persona or instruction in `system_role()`, a `PROMPT` block lets you iterate without running a full workflow.
- **Demonstrations and smoke tests**: CI pipelines that verify adapter connectivity use a hello-world-style `PROMPT` as the probe.

The `PROMPT` form is not the right shape when:

- You need to pass parameters from the command line (use `WORKFLOW` with `INPUT`)
- You need multiple sequential LLM calls (use `WORKFLOW` with multiple `GENERATE` steps)
- You need to call Python tools alongside the LLM (use `WORKFLOW` with `CALL`)
- You need to branch on the model's output (use `WORKFLOW` with `EVALUATE`)

Think of `PROMPT` as `SELECT` without a `FROM`: fast, useful for spot-checks, not a substitute for a full query.

<!-- --- -->

## Exercises

1. **Change the system instruction.** Edit the `system_role()` string to `'You are a gruff database administrator. Explain what SPL 2.0 is in exactly one sentence, using database terminology only.'` Re-run. Observe how the same `GENERATE greeting()` call produces a completely different response when the system context changes. The step name does not constrain the output — the context does.

2. **Swap the adapter.** If you have an Anthropic API key configured, run:
```bash
spl run cookbook/01_hello_world/hello.spl --adapter anthropic
```

The `.spl` file is unchanged. The response will reflect Claude's style rather than gemma3's. This demonstrates adapter portability: the workflow is the specification, the model is the execution engine.

3. **Promote to a WORKFLOW.** Take the `PROMPT` block and rewrite it as a `WORKFLOW` with an `INPUT` parameter called `@persona TEXT DEFAULT 'friendly assistant'`. Pass the persona into the `system_role()` string. Run it with `persona="skeptical engineer"` and `persona="enthusiastic intern"`. This is the shape of section 1.2.

<!-- --- -->

*Next: Chapter 2.2 — Ollama Proxy: Parameterized LLM Queries*
