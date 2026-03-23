# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **book development project** for "A Cookbook of SPL Recipes" — a practitioner's guide to SPL 2.0 (Structured Prompt Language), a declarative SQL-inspired language for orchestrating agentic LLM workflows. Target audience: SQL-fluent engineers and data practitioners. Publication target: Leanpub early access July 2026.

## Build & Run Commands

### Compile Book PDF
```bash
python scripts/compile_book_pdf.py                    # builds dist/spl-cookbook.pdf
python scripts/compile_book_pdf.py --keep-tex          # keep intermediate .tex
python scripts/compile_book_pdf.py --tex-only          # generate .tex without PDF
python scripts/compile_book_pdf.py --output path.pdf   # custom output path
```
Requires: `pandoc` (≥2.9), `xelatex`, `texlive-xetex`, `texlive-fonts-recommended`, `texlive-latex-extra`

### Run SPL Recipes
```bash
cd references/SPL20
spl run cookbook/<NN>_recipe_name/<file>.spl             # run a single recipe
python cookbook/run_all.py                               # run all active recipes
python cookbook/run_all.py --ids "04,10,23-35"           # run specific recipes
python cookbook/run_all.py --category agentic            # filter by category
```
Requires: Python 3.11+, Ollama (default model: `gemma3`)

### Run Tests (SPL 2.0 engine)
```bash
cd references/SPL20
pytest                                                  # all 231 tests
pytest tests/test_specific.py                           # single test file
pytest tests/test_specific.py::test_name                # single test
```

### Recipe Kitchen (Streamlit UI)
```bash
streamlit run scripts/recipe_kitchen.py
```

## Architecture

### Key Directories
- **`references/SPL20/`** — Full SPL 2.0 language runtime, source code (`spl/`), tests, and the 40-recipe cookbook. This is the source of truth for all recipes.
- **`references/SPL20/cookbook/`** — 40 production recipes (numbered `00_`–`40_`), each in its own directory with `.spl` files. Metadata lives in `cookbook_catalog.json`.
- **`drafts/book-v0.3/`** — Current book manuscript (52 markdown chapters). Earlier versions in `book-v0.1/` and `book-v0.2/`.
- **`scripts/`** — Build automation: `compile_book_pdf.py` (MD→LaTeX→PDF pipeline), `recipe_kitchen.py` (Streamlit explorer).
- **`dist/`** — Compiled book output (PDF).
- **`docs/`** — Planning documents, brainstorming, feedback tracking.

### PDF Compilation Pipeline
`compile_book_pdf.py` reads all `.md` files from `drafts/book-v0.3/`, sorts them by chapter number (ch00-0 < ch00-1 < ch01-1), injects part titles automatically, converts via Pandoc to LaTeX, then compiles with XeLaTeX. LaTeX customizations are in `scripts/book-header.tex`.

### Recipe Catalog System
`cookbook_catalog.json` is the central registry for all 40 recipes, storing: ID, name, description, CLI args, directory path, category, active status, and approval status (`new`/`approved`/`wip`/`disabled`). Both `run_all.py` and `recipe_kitchen.py` consume this catalog.

## Book Content Guidelines

### Standard Chapter Template
Every recipe chapter follows this structure:
1. **The Pattern** — Problem motivation, why imperative approach fails
2. **The SPL Approach** — Core idea, how SPL expresses it naturally
3. **The .spl File (Annotated)** — Full source with SQL analogies
4. **Running It** — CLI commands and expected output
5. **What Just Happened** — Execution trace walkthrough
6. **Reproducibility Note** — Latency on reference hardware (GTX 1080 Ti), stability notes
7. **When to Use This Pattern** — Concrete use cases, anti-patterns
8. **Exercises** — 2–3 modifications for the reader

### Core Metaphors & Philosophy
- **Conductor Metaphor:** Human = conductor (vision), LLMs = orchestra (swappable), SPL = score (declarative spec)
- **Declarative over imperative:** Like SQL, SPL describes *what*, the engine handles *how*
- **80/20 Rule:** `CALL` for deterministic ops (math, I/O, regex); `GENERATE` only for reasoning/language generation
- **Adapter-agnostic:** Recipes work across ollama, openrouter, claude, momagrid backends

### SPL 2.0 Core Constructs
- `PROMPT` — Single LLM call
- `WORKFLOW ... DO ... END` — Multi-step orchestration
- `PROCEDURE(args) DO ... END` — Reusable sub-workflows
- `GENERATE expr() INTO @var` — LLM invocation with result capture
- `WHILE ... DO ... END` — Iterative refinement
- `EVALUATE @var WHEN ... THEN ... OTHERWISE ... END` — Semantic branching
- `CALL func(args)` — Deterministic tool operations
- `COMMIT @var` — Finalize workflow output
- `EXCEPTION WHEN ... THEN ... END` — Error handling

### Tone
Senior-engineer, practitioner-focused. No toy examples. Maintain the SQL-to-SPL mental model throughout.
