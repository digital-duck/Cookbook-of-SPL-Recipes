# Map-Reduce Summarizer

<!-- *"To understand the mountain, you must first understand the stones." — Wen Gong* -->

## The Pattern

Every LLM has a context window — a limit on how much text it can process at once. Feed a 50-page technical report into a model with a small window, and the model will forget the beginning or fail entirely. Even with large-context models, massive documents suffer from "lost-in-the-middle" syndrome: key details buried in the center get ignored.

**Map-Reduce** is the classic distributed computing solution. It appears in Google's 2004 paper, in Hadoop, in Spark — and it maps directly to the LLM problem:

1. **Map**: Split the large document into chunks. Summarize each chunk independently.
2. **Reduce**: Combine those summaries into a single, cohesive final report.

The SQL analogy is a `GROUP BY` with an aggregate function:

```sql
SELECT REDUCE(summary)
FROM (
    SELECT MAP(chunk) AS summary
    FROM document_chunks
) AS subquery;
```

You are aggregating many small insights into one large conclusion.

---

## Design Thinking: The Efficient Runtime

section 8.1 is the clearest illustration of SPL's most important design principle: **separate deterministic work from probabilistic work**.

Every operation in an AI workflow belongs to one of two categories:

| Category | Characteristic | SPL keyword | Token cost |
|----------|----------------|-------------|------------|
| **Deterministic** | Can be expressed as code — precise, reproducible | `CALL` | Zero |
| **Probabilistic** | Requires judgment, generation, or ambiguity | `GENERATE` | LLM tokens |

In an earlier version of this recipe, `chunk_plan()` and `extract_chunk()` were both `GENERATE` calls. That meant: every time you ran the recipe, you paid LLM tokens to count words and slice a string — operations that a five-line Python function does perfectly.

The fix is not an optimization. It is a correctness decision. Counting words has one right answer. There is no reason to ask a language model for it.

> *"If you can write it as code — write it as code. Reserve GENERATE for what only a language model can do."*
> — SPL Design Principles, Section 4

This is the same insight that made PL/SQL successful in the Oracle era. SQL declared *what* you wanted; PL/SQL let you write the *how* in the same language. SPL 2.0 does the same for GenAI: `GENERATE` declares what the LLM should do; `CALL` handles everything the LLM shouldn't have to.

---

## The SPL File (Annotated)

```spl
-- Recipe 13: Map-Reduce Summarizer
-- Tools: chunk_plan(), extract_chunk() run deterministically (CALL, zero tokens).
--        summarize_chunk(), reduce_summaries(), quality_score(), improve_summary() call the LLM.
-- Logs written to @log_dir:
--   chunk_N.md, summary_N.md  — per-chunk artifacts
--   final_summary.md          — combined result

WORKFLOW map_reduce_summarizer
    INPUT:
        @document TEXT,
        @style TEXT,
        @log_dir TEXT DEFAULT '13_map_reduce/logs'
    OUTPUT: @final_summary TEXT
DO
    @chunk_index := 0
    @summaries := []          -- LIST: accumulates per-chunk summaries     (1)

    LOGGING 'Starting map-reduce | document length: ' + @document

    -- Step 1: Determine how to split the document (deterministic, 0 tokens)
    CALL chunk_plan(@document) INTO @chunk_count                            -- (2)

    LOGGING 'Document split into ' + @chunk_count + ' chunks'

    -- Step 2: MAP — summarize each chunk independently
    WHILE @chunk_index < @chunk_count DO
        CALL extract_chunk(@document, @chunk_index, @chunk_count) INTO @chunk   -- (3)

        CALL write_file(f'{@log_dir}/chunk_{@chunk_index}.md', @chunk) INTO @_  -- (4)

        GENERATE summarize_chunk(@chunk, @chunk_index) INTO @chunk_summary

        CALL write_file(f'{@log_dir}/summary_{@chunk_index}.md', @chunk_summary) INTO @_

        LOGGING f'[Chunk {@chunk_index}/{@chunk_count}] summary saved'          -- (5)

        @summaries := list_append(@summaries, @chunk_summary)                   -- (6)
        @chunk_index := @chunk_index + 1
    END

    -- Step 3: REDUCE — concat all chunk summaries, then combine into final
    @summaries_text := list_concat(@summaries, '\n')                            -- (7)
    GENERATE reduce_summaries(@summaries_text, @style) INTO @final_summary

    -- Step 4: Quality check the final summary
    GENERATE quality_score(@final_summary, @document) INTO @score

    EVALUATE @score
        WHEN > 0.7 THEN
            CALL write_file(f'{@log_dir}/final_summary.md', @final_summary) INTO @_
            LOGGING f'Final summary saved (score={@score})'
            COMMIT @final_summary WITH status = 'complete', chunks = @chunk_count
        ELSE
            GENERATE improve_summary(@final_summary, @summaries_text) INTO @final_summary
            CALL write_file(f'{@log_dir}/final_summary.md', @final_summary) INTO @_
            LOGGING f'Improved summary saved (score={@score})'
            COMMIT @final_summary WITH status = 'refined', chunks = @chunk_count
    END

EXCEPTION
    WHEN ContextLengthExceeded THEN
        @summaries_text := list_concat(@summaries, '\n')
        GENERATE reduce_summaries(@summaries_text, @style) INTO @final_summary
        CALL write_file(f'{@log_dir}/final_summary.md', @final_summary) INTO @_
        COMMIT @final_summary WITH status = 'partial'
    WHEN BudgetExceeded THEN
        @summaries_text := list_concat(@summaries, '\n')
        GENERATE reduce_summaries(@summaries_text, @style) INTO @final_summary
        CALL write_file(f'{@log_dir}/final_summary.md', @final_summary) INTO @_
        COMMIT @final_summary WITH status = 'budget_limit'
END
```

### (1) Native LIST — `@summaries := []`

SPL 2.0 has a native `LIST` type. `[]` is an empty list. You do not need to build a delimiter-separated string and split it later — a pattern that breaks the moment a summary contains your chosen delimiter.

```spl
@summaries := list_append(@summaries, @chunk_summary)   -- append
@text       := list_concat(@summaries, '\n')            -- join to string
@n          := list_count(@summaries)                   -- length
```

All list operations are deterministic built-ins — zero tokens.

### (2) CALL for `chunk_plan` — Zero Tokens

`chunk_plan(@document)` counts words and calculates how many 800-word chunks the document needs. This is arithmetic. No LLM judgment required. `CALL` runs the registered Python tool directly, no API call, no latency, no cost.

Compare with the old approach:
```spl
GENERATE chunk_plan(@document) INTO @chunk_count   -- ❌ wastes tokens on arithmetic
CALL chunk_plan(@document) INTO @chunk_count       -- ✅ deterministic, 0 tokens
```

### (3) CALL for `extract_chunk` — Zero Tokens

Same principle: slicing `words[start:end]` is pure computation. The Python tool does it in microseconds.

### (4) `write_file` — Built-in File I/O

`write_file(path, content)` is a SPL 2.0 built-in — no `--tools` flag needed, no `tools.py` entry required. It creates parent directories automatically and returns `"written: <path>"`.

The result is discarded with `INTO @_` — the SPL equivalent of Python's `_ = fn()`. Explicit, readable, intentional.

```spl
CALL write_file(f'{@log_dir}/chunk_{@chunk_index}.md', @chunk) INTO @_
```

### (5) F-String Interpolation

`f'{@log_dir}/chunk_{@chunk_index}.md'` is an SPL f-string. The `{@varname}` placeholders are substituted at runtime. Borrowed from Python, adapted for SPL's `@variable` convention.

This is also why `@log_dir` is an `INPUT` parameter with a default — the caller controls the log destination. The recipe never hardcodes a path.

### (6) list_append — Accumulate, Then Join

The map phase builds a LIST. The reduce phase joins it into a single string once, then passes that string to the LLM. This is cleaner than string concatenation inside the loop:

```spl
-- Old: fragile, delimiter-dependent
@summaries := @summaries + '\n---\n' + @chunk_summary

-- New: clean accumulation, clean join
@summaries := list_append(@summaries, @chunk_summary)
-- ... later ...
@summaries_text := list_concat(@summaries, '\n')
```

### (7) list_concat — The Bridge Between LIST and TEXT

`list_concat(@summaries, '\n')` joins the list elements with a newline separator, producing a single TEXT value that the LLM can process. The separator is a parameter — use `'\n---\n'` for section breaks, `', '` for inline lists, whatever the downstream prompt expects.

---

## Running It

```bash
spl run cookbook/13_map_reduce/map_reduce.spl \
    --tools cookbook/13_map_reduce/tools.py \
    --adapter ollama -m gemma3 \
    document="$(cat large_report.txt)" \
    style="executive brief"
```

After the run, inspect the `logs/` folder:

```
13_map_reduce/logs/
  chunk_0.md       ← raw extracted text, chunk 0
  chunk_1.md
  summary_0.md     ← LLM summary for chunk 0
  summary_1.md
  final_summary.md ← combined, quality-checked result
```

The log artifacts are the recipe's debugging story. If the final summary misses something, open `chunk_N.md` to see what the model was given and `summary_N.md` to see what it produced. The problem is localized immediately.

---

## What Just Happened

**LLM calls: 0 (plan) + 0 (extract) + N (map) + 1 (reduce) + 1 (score) + 0–1 (refine).**

Token cost is concentrated exactly where intelligence is required. The two most frequent operations in the loop — chunking and extraction — are zero-token `CALL`s. Every `GENERATE` token is spent on language understanding.

The Conductor (SPL Runtime) managed a classic data pipeline:
1. **Decomposed** the document deterministically (CALL — zero cost)
2. **Processed** each chunk with the LLM (GENERATE — focused cost)
3. **Aggregated** summaries via LIST → list_concat → GENERATE
4. **Validated** and optionally refined the result
5. **Logged** every artifact for inspection

---

## Reproducibility Note

The chunking is deterministic — same document, same chunk boundaries, every run. This makes the Map phase reproducible: if `summarize_chunk` is called with the same text, the LLM output will vary slightly by temperature, but the input is always identical. This separates the non-determinism (LLM) from the determinism (chunking), which is the right structure for debugging and benchmarking.

On a **GTX 1080 Ti**, a 5-chunk document takes about **30–60 seconds**. Time scales linearly with chunk count — predictable, budgetable.

---

## When to Use This Pattern

- **Large documents**: Anything longer than ~2,000 words (adjust `_TARGET_CHUNK_WORDS` in `tools.py`)
- **Batch processing**: Summarize hundreds of files with consistent structure
- **Hierarchical summarization**: Nested Map-Reduce — summarize chapters → parts → book
- **Any accumulate-then-reduce pattern**: Feedback aggregation, code review across files, multi-document synthesis

---

## Exercises

1. **Change the chunk size.** Edit `_TARGET_CHUNK_WORDS` in `tools.py` from 800 to 300. How does the number of chunks and quality of summaries change?
2. **Add a `@log_dir` override.** Run with `log_dir="my_logs"` and confirm the artifacts land in the right place.
3. **Read back a chunk.** Add `CALL read_file(f'{@log_dir}/chunk_0.md') INTO @first_chunk` after the loop and `LOGGING` its first 100 characters. Use `truncate(@first_chunk, 100)`.
4. **Parallel Map.** (Advanced) Research how SPL's `WITH` CTEs can dispatch multiple `summarize_chunk` calls concurrently — removing the sequential bottleneck in the WHILE loop.
