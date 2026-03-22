# Scripts

## compile_book_pdf.py — Book PDF Compiler

Compiles all Markdown chapters from `drafts/book-v0.1/` into a single PDF.

**Pipeline:** `.md chapters` → combined `.md` → `.tex` → `.pdf`

### Requirements

```bash
# pandoc
sudo apt install pandoc

# xelatex + fonts
sudo apt install texlive-xetex texlive-fonts-recommended texlive-latex-extra
```

### Usage

```bash
# From the repo root:
cd /home/gongai/projects/digital-duck/Cookbook-of-SPL-Recipes

# Full build — outputs to drafts/spl-cookbook.pdf
python scripts/compile_book_pdf.py

# Keep the intermediate .tex for inspection
python scripts/compile_book_pdf.py --keep-tex

# Generate .tex only (fast, no PDF — useful for debugging LaTeX)
python scripts/compile_book_pdf.py --tex-only

# Custom output path
python scripts/compile_book_pdf.py --output ~/Desktop/spl-cookbook-draft.pdf
```

### Output

| File | Location |
|------|----------|
| PDF (default) | `drafts/spl-cookbook.pdf` |
| Intermediate .tex | `dist/spl-cookbook.tex` (only with `--keep-tex`) |

### Supporting files

| File | Purpose |
|------|---------|
| `compile_book_pdf.py` | Main compiler script |
| `book-header.tex` | LaTeX customizations: hierarchical numbering (i.j.k.l), centred header/footer, TOC spacing |
