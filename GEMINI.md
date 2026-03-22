# GEMINI.md: Instructional Context for "Cookbook of SPL Recipes"

This project is a book development initiative for **SPL (Structured Prompt Language) 2.0**, a declarative language for orchestrating agentic LLM workflows. The book is designed for SQL-fluent engineers and data practitioners.

## 1. Project Overview

The "Cookbook of SPL Recipes" provides real-world, runnable examples (recipes) of AI workflows. It aims to lower the barrier to AI application development by applying the declarative philosophy of SQL to the world of LLMs.

### Core Philosophy
- **Declarative vs. Imperative:** Like SQL, SPL describes *what* the result should be, while the underlying engine (`spl-llm`) handles *how* to execute it across different models/adapters.
- **The Conductor Metaphor:** The human is the conductor; LLMs are the orchestra; SPL is the score. The score (intent) remains constant even if you swap the orchestra (model/adapter).
- **The 80/20 Rule (CALL vs. GENERATE):** Use `CALL` for deterministic operations (math, I/O, regex) and `GENERATE` only for reasoning or language generation.

## 2. Directory Structure & Key Files

### 2.1. Planning and Vision
- `README.md`: The master book plan, including the one-sentence pitch, target audience, publication timeline, and a detailed 35+ recipe chapter map.
- `brainstorming-ideas.md`: Philosophical foundations, metaphors (Dvořák, conductor), and raw vision fragments.
- `prompt-gemini.md`: Contextual prompt for AI assistants helping with the book writing process.

### 2.2. Content and Drafts
- `drafts/`: Contains the actual chapter files in Markdown.
    - `ch00-1-why-declarative.md`: The foundational argument for the SQL-to-SPL mental model.
    - `ch09-2-recipe-maker.md`: Documentation for the meta-recipe that generates other recipes.
- `resolve-cookbook-issues-1.md`: A log of recipe improvements that established the "Recipe Maker" pattern (Data -> Tools -> SPL -> Readme).

## 3. Standard Chapter Template
Every recipe chapter should follow this consistent structure:
1.  **The Pattern:** Problem motivation and why the imperative approach is painful.
2.  **The SPL Approach:** The core idea and how SPL makes it natural.
3.  **The .spl File (Annotated):** Full source listing with SQL analogies.
4.  **Running It:** CLI invocation and expected output.
5.  **What Just Happened:** Execution trace walkthrough.
6.  **Reproducibility Note:** Latency on reference hardware (GTX 1080 Ti) and stability notes.
7.  **When to Use This Pattern:** Concrete use cases.
8.  **Exercises:** Modifications for the reader to try.

## 4. Workflows for Gemini CLI

### Writing New Chapters
When asked to draft a chapter:
1.  Reference the `README.md` chapter map for the specific recipe number and name.
2.  Adhere to the **Standard Chapter Template** defined above.
3.  Use the "Conductor" and "SQL Analogy" metaphors established in `brainstorming-ideas.md`.
4.  Maintain a senior-engineer, practitioner-focused tone (no "toy" examples).

### Recipe Analysis
If analyzing a `.spl` file:
- Evaluate the balance of `CALL` vs. `GENERATE`.
- Check for "Dataset Grounding" (does it use real mock data?).
- Verify that system context is separated into `CREATE FUNCTION` blocks.

### Technical References
- **Package:** `spl-llm` (PyPI).
- **Binary:** `spl`.
- **Primary Model:** `gemma3`.
- **Reference Hardware:** GTX 1080 Ti.
- **Academic Foundations:** arXiv:2602.21257 (SPL 1.0) and forthcoming SPL 2.0 / Momagrid papers.
