#!/usr/bin/env python3
"""
compile_book_pdf.py
-------------------
Compiles "A Cookbook of SPL Recipes" from Markdown chapters into PDF.

Pipeline:  .md chapters  ->  combined .md  ->  .tex  ->  .pdf

Usage:
    python scripts/compile_book_pdf.py [--keep-tex] [--tex-only] [--output OUTPUT]

Options:
    --keep-tex      Keep the intermediate .tex file after PDF generation
    --tex-only      Stop after generating .tex (no PDF)
    --output PATH   Output PDF path (default: dist/spl-cookbook.pdf)

Requirements:
    pandoc >= 2.9      (apt install pandoc)
    xelatex            (apt install texlive-xetex texlive-fonts-recommended
                        texlive-latex-extra)
"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT        = Path(__file__).resolve().parent.parent
_DEFAULT_DRAFT   = "book-v0.3"
DIST_DIR         = REPO_ROOT / "dist"
COMBINED_MD = DIST_DIR / "spl-cookbook-combined.md"
TEX_OUT     = DIST_DIR / "spl-cookbook.tex"
PDF_DEFAULT = REPO_ROOT / "drafts" / "spl-cookbook.pdf"
BOOK_HEADER = Path(__file__).resolve().parent / "book-header.tex"

# ---------------------------------------------------------------------------
# Book metadata (injected as pandoc YAML front matter)
# ---------------------------------------------------------------------------

METADATA = """\
---
title: "A Cookbook of SPL Recipes"
subtitle: "Declarative Approaches to Agentic Workflow Orchestration"
author: "Wen Gong"
date: "2026"
lang: en
documentclass: book
classoption:
  - 11pt
  - openany
geometry: "margin=1in"
colorlinks: true
linkcolor: "NavyBlue"
urlcolor: "NavyBlue"
citecolor: "NavyBlue"
toc: true
toc-depth: 2
number-sections: true
highlight-style: tango
monofont: "Ubuntu Mono"
header-includes:
  - \\usepackage{listings}
  - \\lstset{breaklines=true, basicstyle=\\small\\ttfamily, keywordstyle=\\ttfamily}
---

"""

# ---------------------------------------------------------------------------
# Part titles (keyed by part number extracted from filename)
# ---------------------------------------------------------------------------

PART_TITLES = {
    0:   "Foundations",
    1:   "Basics",
    2:   "Agentic Patterns",
    3:   "Reasoning",
    4:   "Safety \\& Reliability",
    5:   "Memory \\& Retrieval",
    6:   "Multi-Agent Systems",
    7:   "Applications",
    8:   "Benchmarking \\& Evaluation",
    9:   "The Road Ahead",
    10:  "Tools \\& Community",
}

# ---------------------------------------------------------------------------
# Chapter ordering
# ---------------------------------------------------------------------------

def chapter_sort_key(path: Path) -> tuple:
    """
    Sort chapters in reading order:
      ch00-0  <  ch00-1  <  ch01-1  <  ch07-9  <  ch07-10  <  ch08-1
      about-the-author always last.

    Returns a tuple for stable numeric sorting, handling two-digit recipe
    numbers (ch07-10 > ch07-9, not ch07-1x < ch07-2).
    """
    name = path.stem  # e.g. "ch07-10-progressive-summary"

    if name == "about-the-author":
        return (999, 999, name)

    if name == "glossary":
        return (998, 0, name)

    m = re.match(r"ch(\d+)-(\d+)", name)
    if m:
        part   = int(m.group(1))
        recipe = int(m.group(2))
        return (part, recipe, name)

    # Fallback: sort after numbered chapters, before about-the-author
    return (998, 0, name)


def collect_chapters(drafts_dir: Path) -> list[Path]:
    """Return chapter .md files in correct reading order, excluding drafts."""
    EXCLUDE = {"preface-spl-cookbook-draft.md"}

    chapters = [
        p for p in drafts_dir.glob("*.md")
        if p.name not in EXCLUDE
    ]
    chapters.sort(key=chapter_sort_key)
    return chapters


# ---------------------------------------------------------------------------
# Build steps
# ---------------------------------------------------------------------------

def check_dependencies():
    for tool in ("pandoc", "xelatex"):
        if not shutil.which(tool):
            print(f"ERROR: '{tool}' not found. Install it and retry.")
            sys.exit(1)


def get_part_number(path: Path) -> int | None:
    """Return the part number for a chapter file, or None for about-the-author."""
    m = re.match(r"ch(\d+)-(\d+)", path.stem)
    return int(m.group(1)) if m else None


def build_combined_md(chapters: list[Path]) -> Path:
    """Concatenate chapters into a single Markdown file with YAML front matter.

    Inserts a LaTeX \\part{} divider whenever the part number changes,
    producing proper Part pages in the PDF (e.g. "Part I: Foundations").
    """
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    current_part = None

    with COMBINED_MD.open("w", encoding="utf-8") as out:
        out.write(METADATA)
        for i, chapter in enumerate(chapters):
            part = get_part_number(chapter)

            # Inject \part{} when entering a new numbered part
            if part is not None and part != current_part:
                current_part = part
                title = PART_TITLES.get(part, f"Part {part}")
                out.write(f"\\part{{{title}}}\n\n")
                out.write("\\newpage\n\n")

            text = chapter.read_text(encoding="utf-8").strip()
            out.write(text)
            out.write("\n\n")

            # Page break between chapters
            if i < len(chapters) - 1:
                out.write("\\newpage\n\n")

    print(f"  Combined {len(chapters)} chapters -> {COMBINED_MD.relative_to(REPO_ROOT)}")
    return COMBINED_MD


def build_tex(combined_md: Path, tex_out: Path) -> Path:
    """Convert combined Markdown to LaTeX via pandoc."""
    cmd = [
        "pandoc",
        str(combined_md),
        "--from", "markdown+raw_tex+fenced_code_blocks+backtick_code_blocks",
        "--to", "latex",
        "--standalone",
        "--pdf-engine=xelatex",
        "--listings",                  # use listings package for code blocks
        "--toc",
        "--toc-depth=2",
        "--number-sections",
        "--highlight-style=tango",
        f"--include-in-header={BOOK_HEADER}",
        "--output", str(tex_out),
    ]
    print(f"  pandoc md -> tex ...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("ERROR: pandoc (tex) failed:")
        print(result.stderr)
        sys.exit(1)
    print(f"  LaTeX written -> {tex_out.relative_to(REPO_ROOT)}")
    return tex_out


def build_pdf(combined_md: Path, pdf_out: Path) -> Path:
    """Convert combined Markdown directly to PDF via pandoc + xelatex."""
    cmd = [
        "pandoc",
        str(combined_md),
        "--from", "markdown+raw_tex+fenced_code_blocks+backtick_code_blocks",
        "--pdf-engine=xelatex",
        "--listings",
        "--toc",
        "--toc-depth=2",
        "--number-sections",
        "--highlight-style=tango",
        f"--include-in-header={BOOK_HEADER}",
        "--output", str(pdf_out),
    ]
    print(f"  pandoc md -> pdf (via xelatex) ...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("ERROR: pandoc (pdf) failed:")
        print(result.stderr)
        sys.exit(1)
    size_kb = pdf_out.stat().st_size // 1024
    print(f"  PDF written  -> {pdf_out.relative_to(REPO_ROOT)}  ({size_kb} KB)")
    return pdf_out


def cleanup(paths: list[Path]):
    for p in paths:
        if p.exists():
            p.unlink()
            print(f"  Removed {p.name}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Compile SPL Cookbook from Markdown chapters to PDF"
    )
    parser.add_argument(
        "--keep-tex", action="store_true",
        help="Keep intermediate .tex file after PDF generation"
    )
    parser.add_argument(
        "--tex-only", action="store_true",
        help="Generate .tex only, skip PDF"
    )
    parser.add_argument(
        "--output", type=Path, default=PDF_DEFAULT,
        help="Output PDF path (default: drafts/spl-cookbook.pdf)"
    )
    parser.add_argument(
        "--drafts-dir", type=Path,
        default=REPO_ROOT / "drafts" / _DEFAULT_DRAFT,
        help=f"Directory containing chapter .md files (default: drafts/{_DEFAULT_DRAFT})"
    )
    args = parser.parse_args()

    drafts_dir: Path = args.drafts_dir

    print("\n=== SPL Cookbook PDF Compiler ===\n")
    print(f"Drafts dir: {drafts_dir.relative_to(REPO_ROOT)}\n")

    check_dependencies()

    # 1. Collect and display chapters
    chapters = collect_chapters(drafts_dir)
    print(f"Chapters found: {len(chapters)}")
    for ch in chapters:
        print(f"  {ch.name}")
    print()

    # 2. Combine into single .md
    combined = build_combined_md(chapters)

    # 3. Generate .tex
    build_tex(combined, TEX_OUT)

    if args.tex_only:
        print(f"\nDone (tex-only mode). Review: {TEX_OUT}")
        return

    # 4. Generate PDF
    pdf_path = args.output
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    build_pdf(combined, pdf_path)

    # 5. Cleanup intermediate files unless requested
    to_remove = [combined]
    if not args.keep_tex:
        to_remove.append(TEX_OUT)
    cleanup(to_remove)

    print(f"\n✓ Done: {pdf_path}\n")


if __name__ == "__main__":
    main()
