# SPL Cheatsheet

*All SPL 2.0 syntax on one page.*

## Core Statements

| Statement | Purpose |
|-----------|---------|
| `PROMPT name` | Single-shot LLM invocation |
| `SELECT ... GENERATE fn()` | Context assembly + generation |
| `WORKFLOW name` | Multi-step agentic workflow |
| `PROCEDURE name(args)` | Reusable sub-workflow |
| `CREATE FUNCTION name` | Prompt template definition |

## WORKFLOW Structure

```sql
WORKFLOW workflow_name
  INPUT:
    @param1 TYPE DEFAULT value,
    @param2 TYPE DEFAULT value
  OUTPUT:
    @result1 TYPE,
    @result2 TYPE
DO
  -- body
  COMMIT @result1 WITH key = value
EXCEPTION
  WHEN ErrorType THEN
    -- handler
END
```

## Keywords and Clauses

### Data flow
| Keyword | Meaning |
|---------|---------|
| `INTO @var` | Store result in variable |
| `:=` | Assign value to variable |
| `CAST(x AS TYPE)` | Type conversion |
| `\|\|` | String concatenation |

### Generation
| Keyword | Meaning |
|---------|---------|
| `GENERATE fn(@arg)` | Call LLM via named function template |
| `CALL tool.fn(@arg)` | Call deterministic Python tool (no tokens) |
| `SELECT expr AS alias` | Assemble context for next GENERATE |

### Control flow
| Keyword | Meaning |
|---------|---------|
| `WHILE condition DO ... END` | Loop while condition is true |
| `EVALUATE @var WHEN ... END` | Branch on variable value |
| `WHEN > threshold` | Numeric comparison in EVALUATE |
| `WHEN 'value'` | String match in EVALUATE |
| `ELSE` | Default branch in EVALUATE |
| `BREAK` | Exit WHILE loop |
| `RETRY` | Re-execute current step (in EXCEPTION handler) |

### State
| Keyword | Meaning |
|---------|---------|
| `COMMIT @var WITH key=val` | Write output and metadata |
| `STORE @var IN memory.key` | Write to named memory slot |
| `memory.get('key')` | Read from named memory slot |

### Exception handling
| Keyword | Meaning |
|---------|---------|
| `EXCEPTION` | Begin exception handler block |
| `WHEN ErrorType THEN` | Handle specific error type |

## Built-in Error Types

| Error | When it fires |
|-------|--------------|
| `GenerationError` | LLM call failed or returned malformed output |
| `MaxIterationsReached` | WHILE loop hit its bound without completing |
| `BudgetExceeded` | Token or cost limit exceeded |
| `ContextLengthExceeded` | Input exceeded model's context window |
| `HallucinationDetected` | Downstream validator flagged hallucination |
| `ValidationError` | Structured output failed schema validation |
| `TimeoutError` | Operation did not complete within time limit |
| `FileNotFoundError` | Tool connector could not find the specified file |

## Tool Connectors (Planned)

```bash
spl run script.spl --connector pdf=pymupdf --connector transcribe=whisper
```

| Function | Operation | Default backend |
|----------|-----------|----------------|
| `tool.pdf_to_md(file)` | PDF → Markdown | pymupdf |
| `tool.md_to_pdf(text)` | Markdown → PDF | pandoc |
| `tool.transcribe(file)` | Audio → Text | whisper |
| `tool.tts(text)` | Text → Audio | piper |
| `tool.ocr(image)` | Image → Text | tesseract |
| `tool.caption(image)` | Image → Caption | llava |
| `tool.read_file(path)` | File → Text | built-in |
| `tool.write_file(path, text)` | Text → File | built-in |
| `tool.get_user_input(prompt)` | Console → Text | built-in |
| `tool.display(text)` | Text → Console | built-in |

## Adapter CLI Flags

```bash
spl run script.spl \
  --adapter ollama \          # or: claude_cli, openrouter, momagrid
  -m gemma3 \                 # model name (adapter-specific)
  --input @param=value \      # override INPUT parameters
  --tools tools.py \          # Python tool definitions
  --connector pdf=pymupdf     # tool connector backend
```

| Adapter | Backend |
|---------|---------|
| `ollama` | Local Ollama server (open models) |
| `claude_cli` | Anthropic API (Claude models) |
| `openrouter` | OpenRouter API (multi-provider) |
| `momagrid` | Momagrid decentralized grid |

## CALL vs GENERATE

| | `CALL` | `GENERATE` |
|-|--------|------------|
| What it does | Calls a Python function | Calls an LLM |
| Output | Deterministic | Probabilistic |
| Token cost | Zero | Non-zero |
| Use for | Computation, I/O, tools | Generation, reasoning, evaluation |

**Rule:** If a Python function can do it reliably, use `CALL`. Reserve `GENERATE` for tasks that require language understanding.

## SQL → SPL Mapping

| SQL / PL-SQL | SPL equivalent |
|-------------|----------------|
| `SELECT col FROM table` | `SELECT @var AS alias` |
| `INSERT INTO result` | `COMMIT @var WITH key=val` |
| `CALL stored_proc()` | `CALL tool.fn()` or `PROCEDURE` |
| `IF / CASE WHEN` | `EVALUATE @var WHEN ... END` |
| `WHILE / LOOP` | `WHILE condition DO ... END` |
| `BEGIN ... EXCEPTION ... END` | `WORKFLOW ... EXCEPTION WHEN ... END` |
| `CREATE PROCEDURE` | `WORKFLOW` or `PROCEDURE` |
| `CREATE FUNCTION` | `CREATE FUNCTION` (prompt template) |
| `EXECUTE` / `CALL` | `spl run script.spl --adapter X` |

## Input / Output Types

| Type | SPL keyword |
|------|-------------|
| Text | `TEXT` |
| Integer | `INT` |
| Floating-point | `FLOAT` |
| Boolean | `BOOL` |
| JSON object | `JSON` |
| List | `LIST` |

## Recipe Template Structure

Every recipe follows this eight-section structure:

1. **The Pattern** — what problem this solves
2. **The SPL Approach** — why SPL makes it natural
3. **The `.spl` File (Annotated)** — full source with comments
4. **The SQL Analogy** — structural parallel for SQL practitioners
5. **Running It** — exact commands and expected output
6. **What Just Happened** — execution trace
7. **Reproducibility Note** — latency, hardware, variability
8. **When to Use This Pattern** — use cases, anti-patterns, alternatives
