# ReAct Agent

<!-- *"Don't ask a poet to do your taxes, and don't ask an LLM to do your math." — Wen Gong* -->

<!-- --- -->

## The Pattern

One of the most common pitfalls in AI development is over-reliance on the model. Because LLMs are so good at talking, we tend to ask them to do everything: search the web, extract data, perform calculations, and write reports. But LLMs are probabilistic—they are "guessing" the next token. When it comes to arithmetic or precise data retrieval, "guessing" is not good enough.

The **ReAct (Reason + Act)** pattern solves this by giving the model tools. The model "reasons" about what it needs to do, "acts" by calling an external tool (like a calculator or a search engine), and then observes the result before moving to the next step.

The SQL analogy is an **External Procedure Call** or a **Trigger**. Your database is great at storage and joins, but if you need to send an email or process a credit card, you don't write that logic in SQL; you call an external service.

The ReAct Agent recipe (Recipe 06) demonstrates this "80/20 Rule": 
- Use `CALL` for deterministic operations (math, web search, regex).
- Use `GENERATE` for reasoning (deciding which year to search) and language (writing the final report).

<!-- --- -->

## The SPL Approach

This recipe introduces `PROCEDURE` definitions and the `CALL` statement. It also shows how to register external Python tools using the `@spl_tool` decorator.

<!-- --- -->

## The .spl File (Annotated)

```spl
-- Recipe 06: ReAct Agent — Population Growth
-- Fetch population via WebSearch, compute growth rate via Python tool.

CREATE FUNCTION search_population(country TEXT, year INT) RETURNS TEXT AS $$
Use WebSearch to find the total population of {country} for the year {year}.
Return ONLY the population as a plain integer.
$$;

PROCEDURE search_population(country TEXT, year INT) -- (1) Define a reusable procedure
RETURNS TEXT
DO
  GENERATE search_population(country, year) INTO @result
  COMMIT @result
END

WORKFLOW population_growth
  INPUT: 
    @country TEXT DEFAULT 'China',
    @year_curr integer default 2023
  OUTPUT: @report TEXT
DO
  @year_prev := @year_curr - 1                -- (2) Arithmetic in SPL

  -- Step 1: Fetch population for each year via WebSearch
  CALL search_population(@country, @year_prev) INTO @pop_prev -- (3) Call procedure
  CALL search_population(@country, @year_curr) INTO @pop_curr

  -- Step 2: Compute growth rate — routed to Python tool
  CALL calc_growth_rate(@pop_prev, @pop_curr) INTO @growth_rate -- (4) Call Python tool

  -- Step 3: Compose the final human-readable report
  GENERATE growth_report(...) INTO @report    -- (5) Generate final narrative
  COMMIT @report
END
```

### (1) `PROCEDURE name(...)`

A `PROCEDURE` is a named block of SPL logic. Unlike a `PROMPT`, which is a single model call, a `PROCEDURE` can contain multiple steps. It's the building block of modular agentic workflows.

SQL Analogy: A **Stored Procedure**. It encapsulates a specific task (searching for population) so the main workflow stays clean.

### (2) Arithmetic in SPL

Notice `@year_prev := @year_curr - 1`. SPL handles basic arithmetic and variable assignment directly in the runtime. You don't need an LLM to subtract 1 from a year. This is the "Conductor" doing the simple math so the "Orchestra" can focus on the music.

### (3) `CALL procedure_name(...)`

The `CALL` statement executes a procedure or a tool. It is **deterministic**. When you `CALL search_population`, the runtime executes the steps inside that procedure and returns the result.

### (4) `CALL calc_growth_rate(...)`

This is where the magic happens. `calc_growth_rate` is not an SPL procedure; it's a **Python function** decorated with `@spl_tool`. By using `CALL`, we are leaving the probabilistic world of the LLM and entering the deterministic world of Python. 

The Python tool handles the string parsing (removing commas/spaces) and the floating-point math. The LLM never sees the numbers until the very end.

### (5) `GENERATE growth_report(...)`

Only after the data has been fetched and the math has been verified do we go back to the LLM. We give the model the raw data and ask it to write a "concise 2-3 sentence report." This is what LLMs are best at: **Language Synthesis**.

<!-- --- -->

## Running It

This recipe requires a Python tool file and a web search capability:

```bash
spl run cookbook/06_react_agent/react_agent.spl \
    --adapter claude_cli \
    --allowed-tools WebSearch \
    --tools cookbook/06_react_agent/tools.py \
    country="France"
```

Expected output:
```output
In 2022, France had a population of approximately 67,936,455. 
By 2023, this grew to 68,170,228, representing a year-over-year 
growth rate of 0.3441%.
```

<!-- --- -->

## What Just Happened

**LLM calls: 3.** (2 for searches, 1 for the final report)
**Tool calls: 1.** (Python math tool)

The "Conductor" (SPL Runtime) managed the flow:
1.  Calculated `2022` from `2023 - 1`.
2.  Delegated the searching to the `search_population` procedure.
3.  Delegated the math to the `calc_growth_rate` Python tool.
4.  Assembled the final evidence and asked the model to write the prose.

This separation of concerns is the secret to building **reliable** AI agents. By offloading the math to Python, you eliminate the risk of "hallucinated" growth rates.

<!-- --- -->

## Reproducibility Note

The most variable part of this recipe is the **Web Search**. Different models might navigate to different sources, leading to slightly different population numbers. 

However, because the **math** is handled by Python, the *relationship* between the numbers will always be mathematically sound. This is a critical distinction in SPL 2.0: we accept variability in retrieval but demand correctness in calculation.

<!-- --- -->

## When to Use This Pattern

Use the **ReAct Agent** pattern when:
- **Accuracy is Critical**: Any task involving math, dates, or precise data extraction.
- **External Integration**: You need to fetch data from an API, a database, or the web.
- **Modular Design**: You want to build a library of reusable procedures (`search_population`, `verify_address`, etc.) that can be shared across multiple workflows.

<!-- --- -->

## Exercises

1.  **Add Error Handling.** Use the `EXCEPTION` block to handle cases where `WebSearch` fails to find a number.
2.  **Multi-Year Comparison.** Modify the workflow to fetch data for the last *three* years and calculate the average growth rate.
3.  **Unit Conversion.** Add a Python tool that converts the population number into "millions" or "billions" before passing it to the final report generator.
