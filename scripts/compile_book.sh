#!/usr/bin/env bash
# compile_book.sh — compile the SPL Cookbook PDF from a drafts folder
#
# Usage:
#   ./compile_book.sh                     # defaults to drafts/book-v0.3
#   ./compile_book.sh drafts/book-v0.2    # explicit folder
#   ./compile_book.sh drafts/book-v0.3 --keep-tex
#   ./compile_book.sh drafts/book-v0.3 --tex-only

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"
DRAFTS_DIR="${1:-drafts/book-v0.5}"
shift || true   # consume first arg so remaining args pass through to the script

# Resolve to absolute path
if [[ "$DRAFTS_DIR" != /* ]]; then
    DRAFTS_DIR="$REPO_ROOT/$DRAFTS_DIR"
fi

if [[ ! -d "$DRAFTS_DIR" ]]; then
    echo "ERROR: drafts directory not found: $DRAFTS_DIR"
    exit 1
fi

echo "=== SPL Cookbook PDF Compiler ==="
echo "Drafts dir : $DRAFTS_DIR"
echo ""

python "$REPO_ROOT/scripts/compile_book_pdf.py" \
    --drafts-dir "$DRAFTS_DIR" \
    "$@"
