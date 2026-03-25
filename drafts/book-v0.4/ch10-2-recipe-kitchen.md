# Recipe Kitchen: A Browser UI for SPL

<!-- *"The best tool is the one you actually use."* -->

<!-- --- -->

## What Is Recipe Kitchen?

Every recipe in this book runs from the command line. That is by design — SPL is a language for developers and data engineers who are comfortable in a terminal. But not every team member who needs to *run* a workflow is the same person who *writes* it.

Recipe Kitchen is a Streamlit application that puts all 40 cookbook recipes one click away. No terminal, no flags, no adapter syntax. You select a recipe, adjust its inputs, and press Run.

It is also the place where new recipes are born. The Recipe Maker tab takes a plain-English description and calls the Text2SPL compiler (Recipe #22) to generate a working SPL workflow. You review the code in a built-in editor, run it, and — if you like what you see — save it to a file.

## Starting the Kitchen

```bash
pip install streamlit          # one-time setup
cd references/SPL20
streamlit run ../../scripts/recipe_kitchen.py
```

Your browser opens at `http://localhost:8501`. The kitchen has three tabs.

<!-- --- -->

## Tab 1 — Playground

The Playground is for running existing recipes interactively.

**How it works:**

1. Filter by category (basics, patterns, reasoning, multi-agent, …)
2. Select a recipe from the dropdown — title and description appear immediately
3. Edit any input parameters. The kitchen reads the `args` field from `cookbook_catalog.json` and renders every `key=value` pair as a live text field. Change the topic, the threshold, the model — without touching a config file.
4. Press **Run Recipe**. Output, stderr (if any), exit code, and elapsed time appear inline.

The base command is shown read-only above the parameter fields. You always see exactly what will be executed.

**Example:** Recipe #7 (Progressive Summary) has a `@source_text` input. In the Playground, that becomes an editable text box. Paste any document, click Run, and the progressive-summary workflow runs against your content — the same SPL, your data.

<!-- --- -->

## Tab 2 — Recipe Maker

Recipe Maker bridges the gap between intent and implementation.

**The workflow:**

1. Describe what you want in plain English. Be specific: "Summarize a support ticket, classify its urgency (low/medium/high), and draft a reply if urgency is high."
2. Choose a mode: `auto` (compiler decides), `prompt` (single GENERATE), or `workflow` (multi-step WORKFLOW).
3. Choose an adapter and model. `claude_cli` with a capable model produces the best SPL for complex workflows.
4. Press **Generate SPL**. The Text2SPL compiler (Recipe #22) generates a `.spl` file and loads it into the inline editor.
5. Read the code. Edit it if needed — the editor is fully writable.
6. Press **Run** to execute. Or press **Save** to write it to a named `.spl` file in the cookbook directory.

Recipe Maker does not write to `cookbook_catalog.json` automatically. When a generated recipe proves useful, add it to the catalog manually and it will appear in the Playground on the next page load.

<!-- --- -->

## Tab 3 — Bake-All

Bake-All runs every active recipe in the catalog and saves a timestamped log.

**When to use it:**

- After updating the SPL runtime: verify all 40 recipes still pass
- After adding a new recipe: confirm it does not break anything downstream
- On a schedule (cron job or CI): track regression over time

**How it works:**

Press **Bake All Active Recipes**. The kitchen calls `run_all.py` as a subprocess with a 600-second timeout. When the run completes, the log is saved to `cookbook/out/run_all_YYYYMMDD_HHMMSS.md`.

The Log Browser shows every saved log. Select one to see an approximate pass/fail count (based on ✓/✗/ERROR markers in the log) and the full output.

<!-- --- -->

## Design Notes

**Why Streamlit?** SPL recipes are Python subprocesses under the hood. Streamlit makes it trivial to wrap any subprocess in a browser UI — no JavaScript, no REST API, no front-end build step. The entire kitchen is ~350 lines of Python.

**Why not a web server?** Recipe Kitchen is a local tool. It runs on your machine, reads your filesystem, and executes your SPL runtime. It is not designed to be deployed publicly. For team use, run it on a shared machine and access it over your local network — Streamlit's `--server.address` flag makes this straightforward.

**The catalog as single source of truth.** The Playground and Bake-All both read `cookbook_catalog.json`. Add a recipe to the catalog and it appears everywhere immediately — no UI code changes required. This is the same principle that drives SPL itself: declare the data, let the system handle the display.

<!-- --- -->

## The Vision: A Community Portal

Recipe Kitchen is the seed of something larger.

The current version runs locally. A future version could connect to a community catalog — a shared registry of SPL recipes contributed by users around the world. Browse recipes by category, adapter, or star rating. Fork a recipe, modify it in the editor, and submit it back. Rate recipes you find useful.

This is not a feature for v1.0. It is the direction.

SPL's value compounds with adoption. Every recipe published to a community catalog makes SPL more useful for the next person. The Recipe Kitchen UI is the interface that makes contributing to that catalog accessible to non-developers — the analyst who built a great summarization workflow, the support engineer who automated ticket triage, the teacher who built a quiz generator for their classroom.

The language is the grammar. The recipes are the vocabulary. The kitchen is the door.
