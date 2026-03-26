# Map-Reduce Summarizer

<!-- *"To understand the mountain, you must first understand the stones." — Wen Gong* -->

<!-- --- -->

## The Pattern

Every LLM has a "Context Window"—a limit on how much text it can process at once. If you try to feed a 50-page technical report into a model with a small window, the model will simply "forget" the beginning of the document or crash entirely. Even with large-context models, processing a massive document in one go often leads to "lost-in-the-middle" syndrome, where the model misses key details buried in the center of the text.

**Map-Reduce** is the classic distributed computing pattern for this problem. 
1.  **Map**: Split the large document into smaller, manageable chunks and summarize each chunk independently.
2.  **Reduce**: Combine those individual summaries into a single, cohesive final report.

The SQL analogy is a **GROUP BY with an Aggregate Function**:

```sql
SELECT REDUCE(summary) 
FROM (
    SELECT MAP(chunk) AS summary 
    FROM document_chunks
) AS subquery;
```

You are aggregating many small insights into one large conclusion.

The Map-Reduce Summarizer recipe (Recipe 13) implements this pattern in SPL. It allows you to summarize documents of any length—from a short article to a full-length book—on commodity hardware with limited memory.

<!-- --- -->

## The SPL Approach

This recipe uses a `WHILE` loop for the Map phase and a final `GENERATE` step for the Reduce phase, with an added `EVALUATE` step for quality control.

<!-- --- -->

## The .spl File (Annotated)

```spl
-- Recipe 13: Map-Reduce Summarizer
-- Splits a document, summarizes chunks, then combines them.

WORKFLOW map_reduce_summarizer
    INPUT: @document TEXT, @style TEXT
DO
    @chunk_index := 0
    @summaries := ''

    -- Phase 1: Planning (The Map Strategy)
    GENERATE chunk_plan(@document) INTO @chunk_count -- (1) Determine the split

    -- Phase 2: MAP (Independent Summarization)
    WHILE @chunk_index < @chunk_count DO
        GENERATE extract_chunk(@document, @chunk_index) INTO @chunk
        GENERATE summarize_chunk(@chunk) INTO @chunk_summary -- (2) The Map Step

        @summaries := @summaries + '\n[Chunk ' + @chunk_index + ']: ' + @chunk_summary
        @chunk_index := @chunk_index + 1
    END

    -- Phase 3: REDUCE (Synthesis)
    GENERATE reduce_summaries(@summaries, @style) INTO @final_summary -- (3) The Reduce Step

    -- Phase 4: Quality Check
    GENERATE quality_score(@final_summary, @document) INTO @score

    EVALUATE @score                             -- (4) Conditional Refinement
        WHEN > 0.7 THEN
            COMMIT @final_summary WITH status = 'complete'
        ELSE
            GENERATE improve_summary(@final_summary, @summaries) INTO @final_summary
            COMMIT @final_summary WITH status = 'refined'
    END
END
```

### (1) Phase 1: The Map Strategy

We don't hardcode the chunk size. Instead, we ask a "Planner" model to look at the document and decide how many chunks are needed based on the document's structure (e.g., splitting at section headers).

### (2) Phase 2: The Map Step

Inside the `WHILE` loop, we extract one chunk at a time and summarize it. 
- Each `summarize_chunk` call is independent. It doesn't know about the other chunks. 
- This keeps the context window small and the model focused on the specific details of that section.

### (3) Phase 3: The Reduce Step

Once we have a collection of small summaries, we pass them *all* to the final `reduce_summaries` step. 
- This step acts as the "Editor." Its job is to find the common themes and write a cohesive report in the requested `@style` (e.g., bullet points or executive brief).
- Because the summaries are much shorter than the original document, they easily fit into a single context window.

### (4) Phase 4: Conditional Refinement

We don't just take the first draft. We use a `quality_score` step to check if the final summary accurately reflects the original document. If the score is low, we trigger a refinement pass. This ensures that the "Reduce" phase didn't accidentally drop a critical piece of information from one of the "Map" chunks.

<!-- --- -->

## Running It

Run the summarizer on a large text file:

```bash
spl run cookbook/13_map_reduce/map_reduce.spl --adapter ollama \
    document="$(cat large_report.txt)" \
    style="executive brief"
```

<!-- --- -->

## What Just Happened

**LLM calls: 1 (plan) + N (map) + 1 (reduce) + 1 (score) + 0 or 1 (refine).**

The "Conductor" (SPL Runtime) managed a classic data pipeline:
1.  **Decomposed** a large dataset (the document) into manageable partitions.
2.  **Processed** each partition in parallel (or sequence) to extract key features.
3.  **Aggregated** the features into a final result.
4.  **Validated** the result against the source data.

<!-- --- -->

## Reproducibility Note

The quality of a Map-Reduce summary depends heavily on the **Chunking Strategy**. If a chunk is cut off mid-sentence or mid-paragraph, the model might lose context. 

On a **GTX 1080 Ti**, a 5-chunk document will take about **30–60 seconds** to summarize. The total time scales linearly with the number of chunks, making this pattern highly predictable for large-scale document processing.

<!-- --- -->

## When to Use This Pattern

Use the **Map-Reduce Summarizer** pattern when:
- **Large Documents**: Anything longer than 5,000 words (depending on your model's context window).
- **Batch Processing**: When you need to summarize hundreds of files and want a consistent structure for each.
- **Hierarchical Summarization**: For extremely large texts (like a book), you can even do "Nested Map-Reduce" (summarize chapters → summarize parts → summarize book).

<!-- --- -->

## Exercises

1.  **Change the Chunking.** Modify the `chunk_plan` to always split by exactly 1,000 words instead of looking for section headers. Compare the quality of the final summary.
2.  **Add a "Key Takeaways" section.** Update the `reduce_summaries` step to always include a "Top 3 Action Items" section at the end of the summary.
3.  **Parallel Map.** (Advanced) If you have multiple GPUs or are using a distributed runtime like **Momagrid**, research how to use `WITH` (Chapter 9.1) to run all the `summarize_chunk` calls in parallel instead of in a `WHILE` loop.
