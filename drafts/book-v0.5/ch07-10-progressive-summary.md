# Progressive Summary

<!-- *"The length of a summary should be determined by the reader's time, not the document's size." — Wen Gong* -->

<!-- --- -->

## The Pattern

In a busy professional environment, one size never fits all. A CEO needs a one-sentence "bottom line." A manager needs a one-paragraph "executive brief." A researcher needs a one-page "technical summary." Most summarization tools force you to pick one. If you want all three, you have to run three separate prompts, which often leads to inconsistent or contradictory summaries.

**Progressive Summarization** is the pattern of building summaries in "Layers." 
1.  **Sentence Layer**: Capture the single most important idea in 25 words or less.
2.  **Paragraph Layer**: Expand the sentence summary into a 3–5 sentence brief, adding key supporting evidence.
3.  **Page Layer**: Expand the paragraph summary into a full report, adding context, implications, and conclusions.

The SQL analogy is **Materialized View Hierarchies**. You have your raw data (the document), a high-level aggregate view (the sentence), a mid-level summary view (the paragraph), and a detailed analytical view (the page). Each view is derived from the one above it, ensuring perfect logical consistency across all levels of abstraction.

The Progressive Summary recipe (section 8.11) implements this "Zoomable" interface. It generates all three layers in a single workflow, ensuring that the paragraph summary supports the sentence, and the page summary supports the paragraph.

<!-- --- -->

## The SPL Approach

This recipe introduces **Sequential Expansion**—using the output of a "compressed" step as the seed for a more "detailed" step.

<!-- --- -->

## The .spl File (Annotated)

```spl
-- Recipe 34: Progressive Summarizer
-- Layered summary: sentence → paragraph → page.

CREATE FUNCTION summary_constraints(layer TEXT)
RETURNS TEXT AS $$
SELECT CASE layer
  WHEN 'sentence'  THEN 'One sentence only. Maximum 25 words. Capture the single most important idea.'
  WHEN 'paragraph' THEN '3-5 sentences. Cover main points and key supporting evidence. No examples or details.'
  WHEN 'page'      THEN '2-3 paragraphs. Include context, main argument, evidence, and implications.'
  ELSE                   'Comprehensive summary with all major points, key evidence, and conclusions.'
END
$$;

WORKFLOW progressive_summarizer
    INPUT:
        @text     TEXT,
        @audience TEXT DEFAULT 'general',
        @layers   INT  DEFAULT 3
    OUTPUT: @summary_package TEXT
DO
    LOGGING f'Progressive summary | audience={@audience} layers={@layers}' LEVEL INFO

    -- Layer 1: One-sentence summary
    GENERATE summarize(
        @text,
        summary_constraints('sentence'),
        @audience
    ) INTO @sentence_summary
    LOGGING f'Layer 1 done | sentence summary ready' LEVEL DEBUG

    -- Layer 2: Paragraph summary (built on layer 1 for coherence)
    GENERATE expand_summary(
        @text,
        @sentence_summary,
        summary_constraints('paragraph'),
        @audience
    ) INTO @paragraph_summary
    LOGGING f'Layer 2 done | paragraph summary ready' LEVEL DEBUG

    -- Layer 3: Page-length summary (built on layer 2)
    EVALUATE @layers
        WHEN >= 3 THEN
            GENERATE expand_summary(
                @text,
                @paragraph_summary,
                summary_constraints('page'),
                @audience
            ) INTO @page_summary
            LOGGING 'Layer 3 done | page summary ready' LEVEL DEBUG
        ELSE
            @page_summary := ''
    END

    -- Quality check: does each layer faithfully represent the original?
    GENERATE verify_summary_fidelity(@text, @sentence_summary, @paragraph_summary) INTO @fidelity_score
    LOGGING f'Fidelity score: {@fidelity_score}' LEVEL INFO

    -- Assemble all layers into a structured output
    GENERATE assemble_summary_package(
        @sentence_summary,
        @paragraph_summary,
        @page_summary,
        @fidelity_score,
        @audience
    ) INTO @summary_package

    COMMIT @summary_package WITH
        status = 'complete',
        layers_generated = @layers,
        audience = @audience,
        fidelity = @fidelity_score
END
```

### (1) Layer 1: The Core

We start with the hardest task: extreme compression. By forcing the model to pick *one* idea first, we establish the "Anchor" for the entire workflow.

### (2) Layer 2: The Brief (`expand_summary`)

Instead of summarizing the raw `@text` from scratch, we provide `@sentence_summary` as a guide.
- **Why?** This ensures the paragraph does not wander into minor details. It forces the model to stay aligned with the "core truth" identified in the first step.

### (3) Layer 3: The Report

If the user requested three layers, we repeat the expansion. This "Recursive Detail" pattern is much more stable than asking for three different summaries in a single prompt, which often causes the model to lose track of the length constraints.

SQL Analogy: **Drill-Down**. You are starting at the highest level of aggregation and progressively "joining" more detail from the source text.

### (4) LOGGING for Pipeline Visibility

Each layer logs its completion at `LEVEL DEBUG`. The fidelity score logs at `LEVEL INFO` — that is the metric you care about at a glance. The opening `LOGGING` line shows audience and layers at the start, so you know what you asked for before results arrive.

### (5) `@audience` and Fidelity Check

The updated recipe adds an `@audience` parameter and a fidelity check not shown in the earlier version. The fidelity step (`verify_summary_fidelity`) asks the LLM: does the sentence summary faithfully represent the original? The score is committed alongside the package so downstream consumers know how much to trust the compression.

<!-- --- -->

## Running It

Run the summarizer on a long research paper:

```bash
spl run cookbook/34_progressive_summary/progressive_summary.spl \
    --adapter ollama -m gemma3 \
    text="$(cat research_paper.txt)" audience="executive" layers=3
```

Expected output: A "Summary Package" containing three distinct sections — sentence, paragraph, page — clearly labeled, with a fidelity score confirming consistency across all three.

<!-- --- -->

## What Just Happened

**LLM calls: 4.** (3 layers + 1 final assembly)

The "Conductor" (SPL Runtime) managed an "Editorial Team":
1.  **Distilled** the essence of the document.
2.  **Elaborated** the essence into a brief.
3.  **Contextualized** the brief into a full summary.
4.  **Verified** (at each step) that the new detail supported the previous layer.

<!-- --- -->

## Reproducibility Note

The Progressive pattern is highly **Coherent**. Because each step is grounded in the previous one, you avoid the "drift" that often happens in long-context summarization.

On a **GTX 1080 Ti**, a 3-layer summary takes **20–40 seconds**. The sequential nature means it cannot be parallelized, but the quality gain from the "step-by-step expansion" is worth the extra few seconds of latency.

<!-- --- -->

## When to Use This Pattern

Use the **Progressive Summary** pattern when:
- **Multi-Stakeholder Reporting**: When you need to send different versions of the same information to different people (e.g., Slack, Email, and internal wiki).
- **Zoomable UIs**: Building interfaces where a user can click a "Show More" button to see a more detailed summary of a document.
- **Context Management**: When you need to summarize a document to fit into a specific token budget for a downstream prompt (e.g., Chapter 6.1).

<!-- --- -->

## Exercises

1.  **Add an "Audience" Pass.** Modify the `summary_constraints` to change the tone of all layers based on an `@audience` parameter (e.g., "explain to a 5-year-old" vs "technical expert").
2.  **Custom Layer.** Add a 4th layer called "Twitter" that generates a 280-character summary with 3 relevant hashtags.
3.  **Fidelity Check.** Add a step at the end that compares the "Sentence Layer" to the "Page Layer" and flags any contradictions.
