# Makefile — spl-cookbook
# Run from the repo root.

.PHONY: help kitchen bake test book book-tex lint clean

PYTHON     := python
SPL20_DIR  := references/SPL20
COOKBOOK   := $(SPL20_DIR)/cookbook

help:
	@echo "spl-cookbook — available targets:"
	@echo ""
	@echo "  make kitchen    Launch the Recipe Kitchen Streamlit UI"
	@echo "  make bake       Run all active cookbook recipes"
	@echo "  make test       Run the SPL runtime test suite"
	@echo "  make book       Compile the book to PDF (requires pandoc + xelatex)"
	@echo "  make book-tex   Compile to .tex only (no PDF)"
	@echo "  make lint       Lint Python files with ruff (if installed)"
	@echo "  make clean      Remove build artifacts"

kitchen:
	streamlit run scripts/recipe_kitchen.py

bake:
	$(PYTHON) $(COOKBOOK)/run_all.py

test:
	cd $(SPL20_DIR) && pytest

book:
	bash scripts/compile_book.sh

book-tex:
	bash scripts/compile_book.sh drafts/book-v0.3 --tex-only

lint:
	@ruff check src scripts references/SPL20/spl2 2>/dev/null || echo "ruff not installed — pip install ruff"

clean:
	rm -rf dist/ build/ src/*.egg-info
	find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
