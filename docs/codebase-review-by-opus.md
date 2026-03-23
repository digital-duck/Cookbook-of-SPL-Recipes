# Codebase Review — Suggestions for Improvement

Reviewed: 2026-03-23

---

## 1. Add a top-level Makefile or task runner

Build commands are scattered across multiple scripts, each requiring a different working directory. A top-level `Makefile` would unify everything:

```makefile
book:        python scripts/compile_book_pdf.py
test:        cd references/SPL20 && pytest
bake-all:    cd references/SPL20 && python cookbook/run_all.py
kitchen:     cd references/SPL20 && streamlit run ../../scripts/recipe_kitchen.py
```

This eliminates the "which directory do I `cd` into?" problem for contributors and AI assistants.

---

## 2. PDF output path vs `.gitignore` mismatch

`.gitignore` excludes `dist/`, but `compile_book_pdf.py` defaults output to `drafts/spl-cookbook.pdf` (line 39), which is tracked by git. Binary PDFs bloat the repo over time. Fix options:

- Move default output back to `dist/` and stop tracking it, or
- Add `drafts/spl-cookbook.pdf` to `.gitignore`

---

## 3. Chapter-to-recipe linkage is implicit

There is no machine-readable mapping between chapter files (`ch02-1-self-refine.md`) and recipe directories (`05_self_refine/`). The numbering schemes differ (chapter 02-1 vs recipe 05). A mapping table (in `cookbook_catalog.json` or a separate file) would enable:

- Auto-validation that every recipe has a chapter and vice versa
- Auto-inserting "Running It" sections with correct CLI args from the catalog
- Detecting drift between chapter content and actual recipe behavior

---

## 4. No CI or pre-commit hooks

There is no automated validation. Even lightweight checks would catch issues early:

- **Chapter template lint** — verify each `ch*.md` has all 8 required sections (The Pattern, The SPL Approach, The .spl File, Running It, What Just Happened, Reproducibility Note, When to Use This Pattern, Exercises)
- **Recipe smoke test** — `run_all.py --dry-run` or syntax-check all `.spl` files without calling LLMs
- **PDF build check** — verify `compile_book_pdf.py --tex-only` succeeds (catches Pandoc/LaTeX issues early)
- **Cross-reference check** — verify recipe IDs mentioned in chapters match `cookbook_catalog.json`

---

## 5. `compile_book_pdf.py` hardcodes `book-v0.3`

`DRAFTS_DIR` is hardcoded to `drafts/book-v0.3` (line 35). When moving to v0.4, the script must be edited. Options:

- Add a `--drafts-dir` CLI argument with `book-v0.3` as default
- Use a symlink like `drafts/current/` that always points to the active version

---

## 6. Recipe Kitchen: unsanitized filename in save path

In `recipe_kitchen.py` line 252, user input is used directly as a filename:

```python
save_path = COOKBOOK_DIR / f"{recipe_name}.spl"
```

A name like `../../etc/something` would write outside the cookbook directory. Low risk since it's a local Streamlit app, but `Path(recipe_name).name` would prevent path traversal.

---

## 7. Log pass/fail counting is fragile

`recipe_kitchen.py` lines 342-343 count pass/fail by substring matching (`content.count("✓")`), which miscounts when those strings appear in recipe output text. Better approach: have `run_all.py` emit a JSON summary, or parse structured markers instead of raw substrings.

---

## 8. Missing `requirements.txt` for book tooling

The SPL engine has `pyproject.toml`, but the book-level scripts (`compile_book_pdf.py`, `recipe_kitchen.py`) have no declared Python dependencies. A top-level `requirements.txt` listing `streamlit` and any other deps would help new contributors get set up quickly.
