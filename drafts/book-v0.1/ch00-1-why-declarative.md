# Chapter 0.1 — Why Declarative? SQL as the Mental Model

---

## The Problem You Already Solved

You have written SQL for years. Maybe a decade. You know what it feels like to sit down with a business question — "how many customers churned last quarter by region?" — and translate it directly into a query that returns exactly that, without worrying about B-tree traversal strategies, page cache management, or network round-trips to the storage layer.

You wrote:

```sql
SELECT region, COUNT(*) AS churned
FROM customers
WHERE status = 'churned'
  AND churned_at BETWEEN '2025-10-01' AND '2025-12-31'
GROUP BY region
ORDER BY churned DESC;
```

The database figured out the rest.

This is declarative programming. You describe *what* you want. The engine decides *how* to produce it. The physical details — indexes, join algorithms, parallelism — are someone else's problem. Your job is the query.

Now contrast that with what most engineers write the first time they try to build an LLM workflow.

---

## What Imperative LLM Code Looks Like

Here is a realistic Python script for a simple draft-critique-refine loop. Three steps: draft a proposal, critique it, refine based on the critique. Straightforward in description. Watch what happens in implementation.

```python
import anthropic
import json
import sys
import time

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

def draft_proposal(topic: str) -> str:
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"Write a one-paragraph proposal for: {topic}"
            }
        ]
    )
    return response.content[0].text

def critique_proposal(draft: str) -> str:
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=512,
        messages=[
            {
                "role": "user",
                "content": f"Critique this proposal. Be specific about weaknesses:\n\n{draft}"
            }
        ]
    )
    return response.content[0].text

def refine_proposal(draft: str, critique: str) -> str:
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Revise this proposal based on the critique below.\n\n"
                    f"Original:\n{draft}\n\n"
                    f"Critique:\n{critique}"
                )
            }
        ]
    )
    return response.content[0].text

if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else "a new employee onboarding process"

    print("Drafting...")
    draft = draft_proposal(topic)

    print("Critiquing...")
    critique = critique_proposal(draft)

    print("Refining...")
    result = refine_proposal(draft, critique)

    # Save output
    with open("output.json", "w") as f:
        json.dump({
            "topic": topic,
            "draft": draft,
            "critique": critique,
            "result": result,
            "timestamp": time.time()
        }, f, indent=2)

    print(result)
```

This works. It runs. A developer reviewing it can follow the logic. But look at what you had to decide:

Which model. What `max_tokens`. How to format the messages list. How to extract `response.content[0].text` — the right accessor for this SDK version. How to pass context between steps. How to handle output. Whether to save intermediate states. What to do if the API call fails (this script does nothing — it crashes).

None of those decisions are about your *intent*. They are all about the *mechanics* of talking to one specific provider's API in one specific programming language using one specific SDK version that may have breaking changes in six months.

The business logic — draft, critique, refine — is buried inside three functions that look nearly identical. The signal is drowning in noise.

And if you want to switch from Claude to Gemini to test whether it produces better proposals? You rewrite three functions, update the import, change the accessor, and pray the response schema is compatible. Then you maintain two versions of the same logic.

This is the imperative LLM problem. You are managing infrastructure details when you should be thinking about intent.

---

## The SQL Analogy

SQL solved this problem for data in the 1970s. The insight was simple but radical: separate *what* you want from *how* the system produces it.

Before SQL, you wrote navigational database code. You traversed records manually, managed cursors, tracked positions in file hierarchies. To get the churn report, you wrote a loop. You opened a file handle. You read records. You checked dates. You aggregated. The query and the execution plan were the same thing.

SQL said: stop. Describe the result set. The query optimizer will figure out whether to use a nested loop join or a hash join, whether to scan the index forward or backward, whether to parallelize across partitions. That is the engine's job. Your job is the query.

SPL applies the same insight to LLM workflows.

You describe the workflow — what steps exist, what each step produces, how data flows between steps, what conditions branch the logic. SPL figures out how to execute it: which model to call, how to format the prompt for that model's API, how to parse the response, how to pass context forward.

The mental model shift is not about learning new syntax. It is about recognizing a pattern you already know and applying it to a new domain.

---

## The Mapping

SQL and SPL share more than a philosophy. They share a structural vocabulary.

**SELECT → GENERATE**

In SQL, `SELECT` defines what you want to retrieve or compute. In SPL, `GENERATE` defines what you want the LLM to produce.

```sql
-- SQL: retrieve a computed column
SELECT summarize(article_text) AS summary
FROM articles
WHERE published_at > '2025-01-01';
```

```spl2
-- SPL: generate a summary using an LLM
GENERATE summarize(article_text) INTO @summary
```

Both express *what* you want. Neither tells the engine *how* to produce it.

**WHERE → EVALUATE**

In SQL, `WHERE` filters rows based on a condition. In SPL, `EVALUATE` branches execution based on the content of an LLM output.

```sql
-- SQL: filter based on a computed value
SELECT *
FROM proposals
WHERE sentiment_score > 0.7;
```

```spl2
-- SPL: branch based on an LLM judgment
EVALUATE @sentiment
  WHEN 'positive' THEN
    COMMIT @proposal WITH status = 'approved'
  OTHERWISE
    GENERATE revision(@proposal, @feedback) INTO @proposal
END
```

SQL's `WHERE` is deterministic — you know the filter will behave the same every time. SPL's `EVALUATE` is probabilistic — the LLM decides the value of `@sentiment`, so the branch depends on a judgment call. The syntax looks similar because the intent is similar: route data based on a condition.

**Stored Procedure → WORKFLOW**

In SQL, a stored procedure encapsulates a named, parameterized sequence of operations. In SPL, a `WORKFLOW` does the same.

```sql
-- SQL stored procedure
CREATE PROCEDURE generate_churn_report(
    start_date DATE,
    end_date DATE
)
AS BEGIN
    SELECT region, COUNT(*) AS churned
    FROM customers
    WHERE churned_at BETWEEN start_date AND end_date
    GROUP BY region;
END;
```

```spl2
-- SPL workflow
WORKFLOW draft_and_refine
  INPUT:
    @topic TEXT,
    @max_iterations INTEGER DEFAULT 3
  OUTPUT: @result TEXT
DO
  GENERATE draft(@topic) INTO @current
  -- ... loop and refine
END
```

Both are named, reusable, parameterized. Both separate the caller (who provides inputs) from the implementation (which decides how to produce outputs).

**UDF → CREATE FUNCTION**

In SQL, a user-defined function returns a scalar or table value that the query engine can use anywhere a value is expected. In SPL, `CREATE FUNCTION` defines a system context block — effectively a prompt component — that can be injected into any `GENERATE` call.

```sql
-- SQL UDF
CREATE FUNCTION business_hours(ts TIMESTAMP)
RETURNS BOOLEAN AS $$
    RETURN EXTRACT(HOUR FROM ts) BETWEEN 9 AND 17;
$$ LANGUAGE plpgsql;
```

```spl2
-- SPL function: defines system context injected as an LLM prompt
CREATE FUNCTION expert_reviewer()
RETURNS TEXT AS $$
  You are a senior technical reviewer with 15 years of experience.
  You provide specific, actionable feedback.
  You do not hedge or soften criticism.
$$
```

The SQL UDF is called by the query engine wherever the function name appears. The SPL function is injected as system context wherever the function name appears in a `GENERATE` call. Same concept: composable, reusable units that plug into a larger expression.

---

## CALL vs. GENERATE: The Most Important Distinction

There is one concept in SPL that has no direct SQL analog, but every SQL practitioner will immediately understand it once the motivation is clear.

SPL has two types of steps: `CALL` and `GENERATE`.

`CALL` invokes a deterministic Python function. It costs nothing in tokens. It runs at machine speed. It is perfectly reproducible — run it a thousand times with the same input and you get the same output every time.

`GENERATE` invokes an LLM. It costs tokens. It is relatively slow. It is probabilistic — run it a thousand times and you get slightly different outputs each time.

The rule is simple: **use CALL for everything code can do. Use GENERATE only for what genuinely requires reasoning or generation.**

A SQL practitioner understands this instinctively. If you can write it as `WHERE date > '2025-01-01'`, you do not need a subquery. If you can compute it in the SELECT clause with a deterministic expression, you do not call a stored procedure. You use the cheapest, most reliable tool that produces the right result.

```spl2
-- Wrong: asking the LLM to do arithmetic
GENERATE count_words(@document) INTO @word_count

-- Right: use a Python function
CALL count_words(@document) INTO @word_count
```

The LLM cannot count words more reliably than `len(text.split())`. It costs more. It is slower. It might be wrong. There is no reason to involve it.

```spl2
-- Wrong: trying to parse a JSON field in SPL when code can do it
GENERATE extract_author(@raw_json) INTO @author

-- Right: deterministic extraction
CALL extract_field(@raw_json, 'author') INTO @author
```

The LLM cannot parse JSON more reliably than `json.loads()`. It should not be asked to.

```spl2
-- Right: using the LLM for what only it can do
GENERATE assess_argument_quality(@essay, @criteria) INTO @assessment
```

Is this argument coherent? Does it address the counterargument? Is the evidence relevant? Code cannot do this. A regex cannot do this. A lookup table cannot do this. This is where LLM tokens are earned.

The CALL/GENERATE split is the single most important design decision in any SPL workflow. It determines quality, cost, and reliability all at once. A workflow that routes everything through `GENERATE` is like a SQL query that computes everything in a subquery when a simple expression would suffice — technically correct, unnecessarily expensive, and harder to debug.

---

## The Adapter Abstraction

Here is where the SQL analogy pays its biggest dividend.

When you write SQL, you do not write "PostgreSQL." You write SQL. The same `SELECT * FROM customers WHERE status = 'active'` runs on PostgreSQL, MySQL, BigQuery, and Snowflake. The syntax may have minor dialects. The performance characteristics differ. But the query expresses the same intent and produces the same result set regardless of the engine underneath.

SPL works the same way for LLM workflows. The same `.spl` file runs against Ollama (local models), OpenRouter (API-based cloud models), or claude_cli (Claude directly). You change the adapter flag at the command line. The workflow does not change.

```bash
# Same .spl file, three different adapters
spl2 run workflow.spl --adapter ollama -m gemma3
spl2 run workflow.spl --adapter openrouter -m openai/gpt-4o
spl2 run workflow.spl --adapter claude_cli -m claude-opus-4-5
```

A SQL database does not expose B-tree implementations to your queries. An SPL adapter does not expose API schemas, authentication headers, response parsing, or token accounting to your workflows. These are infrastructure concerns. The workflow describes intent. The adapter handles execution.

This matters enormously in practice. When you build a workflow against a local Ollama model during development, you are not taking on technical debt. You are building the real workflow. When you move to production on a cloud model, you change one flag. The workflow file is unchanged, unmodified, and untested against the new model — but it runs, because the adapter handles the translation.

SQL practitioners know what it is like to develop against a local database and deploy against a production cluster. The adapter abstraction is the same thing.

---

## Side by Side

The clearest way to see the difference is to solve the same problem both ways. A draft-critique-refine loop: given a topic, generate a draft, have the model critique it, refine based on the critique.

**Python (imperative)**

```python
import anthropic
import os

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

def run(topic: str) -> str:
    # Step 1: Draft
    draft_response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system="You are an experienced technical writer.",
        messages=[{"role": "user", "content": f"Write a draft proposal for: {topic}"}]
    )
    draft = draft_response.content[0].text

    # Step 2: Critique
    critique_response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=512,
        system="You are a critical editor. Find specific weaknesses.",
        messages=[{"role": "user", "content": f"Critique this draft:\n\n{draft}"}]
    )
    critique = critique_response.content[0].text

    # Step 3: Refine
    refine_response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system="You are an experienced technical writer.",
        messages=[{
            "role": "user",
            "content": f"Revise the draft based on this critique.\n\nDraft:\n{draft}\n\nCritique:\n{critique}"
        }]
    )
    return refine_response.content[0].text

if __name__ == "__main__":
    import sys
    result = run(sys.argv[1])
    print(result)
```

Count the decisions baked into this file: the provider (Anthropic), the model name (hardcoded), the API key source (environment variable name), the max_tokens values (guessed), the response accessor (`.content[0].text`), the system prompt duplication (writer appears twice), the context formatting (manual string concatenation), and the complete absence of error handling.

**SPL (declarative)**

```spl2
CREATE FUNCTION technical_writer()
RETURNS TEXT AS $$
  You are an experienced technical writer.
  Your drafts are clear, specific, and actionable.
$$

CREATE FUNCTION critical_editor()
RETURNS TEXT AS $$
  You are a critical editor. Find specific weaknesses.
  Be direct. Do not soften your feedback.
$$

WORKFLOW draft_critique_refine
  INPUT:
    @topic TEXT
  OUTPUT: @result TEXT
DO
  GENERATE draft(technical_writer(), @topic) INTO @current
  GENERATE critique(critical_editor(), @current) INTO @feedback
  GENERATE refine(technical_writer(), @current, @feedback) INTO @result

  COMMIT @result WITH topic = @topic, status = 'complete'
END
```

The SPL version describes the workflow. The Python version implements it. Every line in the SPL file is about intent. Most lines in the Python file are about mechanics.

The SPL version runs on any adapter. The Python version runs on Anthropic's API with the claude-opus-4-5 model. Changing models requires editing the source. Changing providers requires rewriting the client.

The SPL version has error handling built into the runtime (the adapter layer catches API failures, retries, and surfaces them as typed exceptions the workflow can handle). The Python version crashes.

The SPL version is readable by someone who has never seen LLM code before — they will recognize the pattern immediately because it looks like a stored procedure. The Python version is readable only to someone who knows this specific SDK's response schema.

Neither version is "better" in every situation. Python gives you the full language for cases where SPL's abstraction is too constraining. But for the canonical LLM workflow patterns — draft, critique, refine, route, retry — SPL is not a workaround. It is the right tool.

---

## Why This Matters for SQL Practitioners Specifically

You already know declarative thinking. You already know how to describe what you want and let an engine figure out how to produce it. You already know how to decompose a complex data transformation into named, composable steps. You already know how to think in pipelines.

The SQL-to-SPL transfer is not a leap. It is a lateral move.

The domain changes: instead of rows and columns, you are working with text and language model outputs. The stakes change: instead of a deterministic join, you are routing through a probabilistic judgment. The tooling changes: instead of `psql` or `dbeaver`, you use `spl2`.

But the mental model is the same. Describe what you want. Let the engine handle how. Trust the abstraction until you have a reason not to.

One more thing carries over directly: the instinct to profile before optimizing. SQL practitioners do not rewrite queries on a hunch — they check the execution plan, identify the bottleneck, and fix the specific problem. SPL workflows deserve the same discipline. Do not route through `GENERATE` unless you have confirmed that `CALL` cannot do the job. Do not run a three-step GENERATE loop when a single well-constructed prompt would suffice. Spend tokens where they earn their cost.

The models are the orchestra. SPL is the score. The score says what to play and in what order. The conductor does not tune the instruments or manage the rosin — the adapter handles that. Your job is to write music worth performing.

You already know how to think about this. You have been doing it with data for years. The domain is new. The discipline is not.

---

## What Comes Next

The next chapter gets you running. Install `spl-llm`, pull a model, and execute a workflow in under fifteen minutes. From there, every recipe in this book is open to you.

The conceptual work is done here. The rest is practice.

---
