# Sentiment Pipeline

*"Data tells you what happened; sentiment tells you why it matters."*

---

## The Pattern

In the age of social media and instant feedback, businesses are drowning in text. Thousands of reviews, support tickets, and tweets arrive every day. A human can read ten reviews and get a "vibe," but they cannot objectively score 1,000 reviews for emotional nuance, statistical trends, and extreme outliers without losing their mind.

**Batch Sentiment Orchestration** is the pattern of converting a stream of raw text into a structured analytical report.
1.  **Ingest**: Load and split a list of items (e.g., from a file or a pipe).
2.  **Analyze**: Use a model to classify each item according to a strict schema (Label, Score, Confidence, Emotions).
3.  **Aggregate**: Use deterministic code to compute averages, ratios, and distributions.
4.  **Synthesize**: Use a "Senior Analyst" model to write a narrative summary of the trends and highlight extreme cases.

The SQL analogy is an **Aggregate Query with a Window Function**. You are processing a "batch" of rows, calculating statistics across the whole set (`AVG(score)`), and identifying specific rows that stand out (`RANK() OVER ...`).

The Sentiment Pipeline recipe (Recipe 31) implements this full stack. It demonstrates the **80/20 Rule** perfectly: LLMs do the hard work of "feeling" the text, while Python does the heavy lifting of "calculating" the statistics.

---

## The SPL Approach

This recipe introduces **Batch Schema Enforcement**—forcing the LLM to return an array of structured objects that map 1:1 to your input list.

---

## The .spl File (Annotated)

```spl
-- Recipe 31: Sentiment Pipeline
-- Batch sentiment over a list, aggregate trend statistics.

WORKFLOW sentiment_pipeline
    INPUT: @filename TEXT DEFAULT '', @domain TEXT DEFAULT 'general'
DO
    -- Phase 1: Preparation (Deterministic)
    CALL load_items(@filename) INTO @file_content
    CALL split_items(@file_content) INTO @item_list -- (1) Python Splitting Tool

    -- Phase 2: Analysis (Probabilistic)
    GENERATE batch_sentiment(
        @item_list, 
        sentiment_schema(),                         -- (2) The Extraction Schema
        @domain
    ) INTO @sentiment_results

    -- Phase 3: Statistics (Deterministic)
    CALL compute_stats(@sentiment_results) INTO @stats -- (3) Python Math Tool
    CALL find_extremes(@sentiment_results) INTO @extremes

    -- Phase 4: Narrative Synthesis (Probabilistic)
    GENERATE summarize_trends(@stats, @extremes) INTO @summary

    -- Phase 5: Final Assembly
    GENERATE assemble_report(@sentiment_results, @stats, @summary) INTO @report
    COMMIT @report WITH status = 'complete'
END
```

### (1) Python Splitting Tool (`split_items`)

We use a Python tool to turn a raw text file (e.g., reviews separated by newlines) into a JSON array. 
- **Why?** It is much cheaper and more reliable to split strings in Python than to ask an LLM to "parse this file."

### (2) The Extraction Schema (`sentiment_schema`)

We pass a formal JSON schema that requires the model to provide a `score` between -1 and 1 and a `label` from a fixed list (`positive`, `negative`, `neutral`). This ensures the data is ready for the math step.

### (3) Python Math Tool (`compute_stats`)

Once we have the LLM's scores, we hand them back to Python. 
- **Why?** LLMs are notorious for hallucinating math. Python, however, can calculate the `mean`, `standard deviation`, and `sentiment_ratio` perfectly. This is the **Human-in-the-loop** (or rather, **Code-in-the-loop**) principle of SPL 2.0.

---

## Running It

Run the pipeline on a file of product reviews:

```bash
spl run cookbook/31_sentiment_pipeline/sentiment.spl \
    --adapter ollama --tools cookbook/31_sentiment_pipeline/tools.py \
    filename="product_reviews.txt" \
    domain="product_reviews"
```

Expected output: A comprehensive report including a statistical breakdown (e.g., "75% Positive, 1.2x Sentiment Ratio") and a narrative summary highlighting specific complaints or praises.

---

## What Just Happened

**LLM calls: 3.** (Batch analysis, Trend summary, Final assembly)
**Tool calls: 4.** (Load, Split, Stats, Extremes)

The "Conductor" (SPL Runtime) managed a "Data Science Lab":
1.  **Cleaned** and partitioned the raw data.
2.  **Extracted** high-dimensional features (sentiment and emotion) using the model.
3.  **Calculated** low-dimensional statistics using Python.
4.  **Translated** those statistics back into a human-readable story.

---

## Reproducibility Note

The accuracy of the statistics is 100% (given the model's scores). The "Vibe" of the sentiment analysis is highly reproducible on larger models like **gemma3**. 

On a **GTX 1080 Ti**, a batch of 15 reviews takes **20–40 seconds**. The pipeline is designed to be "Elastic"—if you have more reviews, the `GENERATE` step simply takes more tokens, but the logic remains identical.

---

## When to Use This Pattern

Use the **Sentiment Pipeline** pattern when:
- **Market Research**: Analyzing feedback from multiple sources to see how a brand is perceived.
- **Support Operations**: Identifying a sudden "spike" in negative sentiment that might indicate a system outage.
- **Product Launches**: Tracking real-time reaction to a new feature across different demographics.

---

## Exercises

1.  **Add a "Competitor" filter.** Modify the schema to include a `mentions_competitor` boolean field. Update the `compute_stats` tool to calculate what percentage of reviews mention a rival product.
2.  **Filter by Confidence.** Add a step after Phase 3 that filters out any analysis where the model's `confidence` is below 0.5 and asks for a manual review.
3.  **Cross-Domain Test.** Run the recipe on the `social_media.txt` file but set the `domain` to `legal_contracts`. Observe how the "Sentiment" becomes much more neutral and analytical.
