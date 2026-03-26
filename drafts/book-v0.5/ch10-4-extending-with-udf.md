# Extending SPL with User-Defined Functions

<!-- *"The real power of a declarative language is not what it does — it is what it lets you plug in."* -->

<!-- --- -->

## CALL Is SPL's Design Strength

Every SPL workflow makes exactly two kinds of operations. `GENERATE` calls an LLM — probabilistic, creative, slow, expensive. `CALL` calls a Python function — deterministic, testable, instant, free. This distinction is not a syntax choice. It is an architectural principle.

The Anthropic editorial review of SPL 2.0 called this split out explicitly as the language's most important strength:

> *CALL vs. GENERATE is the clearest design decision in SPL. It forces the workflow author to be explicit about which operations are deterministic and which are probabilistic. Most LLM frameworks blur this line — SPL draws it in ink.*

`CALL` is SPL's bridge into the Python ecosystem. The `@spl_tool` decorator is a Foreign Function Interface: any Python callable — from a one-liner to a 500-line class method that queries a database, calls a REST API, runs a scikit-learn model, or reads a file — becomes a first-class SPL operation with a single line.

```python
@spl_tool
def lookup_customer(customer_id: str) -> str: ...   # database query
```

```spl
CALL lookup_customer(@id) INTO @customer_json        -- deterministic, zero LLM cost
GENERATE write_response(@customer_json) INTO @reply  -- LLM for the language part only
```

The entire Python ecosystem — NumPy, pandas, SQLAlchemy, Requests, scikit-learn, OpenCV, PyTorch inference, any internal SDK — is one decorator away. This is what makes SPL production-grade: not that it can call LLMs, but that it can precisely control *when* it does.

<!-- --- -->

## What Becomes Possible

Because any Python function can be a CALL target, SPL workflows can:

| Operation | Python library | Example CALL |
|---|---|---|
| Query a database | `sqlalchemy`, `psycopg2` | `CALL db_lookup(@id) INTO @row` |
| Call a REST API | `httpx`, `requests` | `CALL fetch_weather(@city) INTO @forecast` |
| Run ML inference | `scikit-learn`, `transformers` | `CALL classify_intent(@text) INTO @intent` |
| Read/write files | `pathlib`, `csv`, `openpyxl` | `CALL load_csv(@path) INTO @data` |
| Validate data | `pydantic`, `jsonschema` | `CALL validate_schema(@json) INTO @errors` |
| Send a notification | `slack-sdk`, `smtplib` | `CALL notify_slack(@message) INTO @status` |
| Compute embeddings | `sentence-transformers` | `CALL embed(@text) INTO @vector` |
| Detect PII | `presidio`, regex | `CALL detect_pii(@text) INTO @report` |
| Cache results | `redis`, `diskcache` | `CALL cache_get(@key) INTO @cached` |
| Hash / sign data | `hashlib`, `hmac` | `CALL sign_payload(@data) INTO @sig` |

None of these require changes to SPL itself. The language stays small. The ecosystem grows without limit.

<!-- --- -->

## How CALL Dispatches

When SPL encounters `CALL foo(@arg)`, it resolves the function name in this order:

1. **Registered Python tool** — loaded via `--tools tools.py` or from stdlib
2. **SPL PROCEDURE** — defined earlier in the same `.spl` file
3. **LLM fallback** — treated as a GENERATE if nothing else matches

UDFs take priority over everything else. If you register a tool named `upper`, it overrides the stdlib `upper`. Use this consciously — override when you need domain-specific behaviour; otherwise rely on stdlib.

<!-- --- -->

## The `@spl_tool` Decorator

The entire UDF system is a single decorator. Any Python callable decorated with `@spl_tool` becomes available as a `CALL` target:

```python
# tools.py
from spl.tools import spl_tool

@spl_tool
def word_count(text: str) -> int:
    """Count words in a string."""
    return len(text.split())
```

```spl
-- workflow.spl
CALL word_count(@response) INTO @n_words
```

That is the complete API. No registration table to maintain, no base classes to inherit, no configuration files. The decorator handles everything.

<!-- --- -->

## section 11.4 — The Definitive Example

section 11.4 (Tool-Use / Function-Call) is the reference implementation of the UDF pattern. It embodies the core architectural principle:

> **LLMs for language. Python for computation.**

```python
# cookbook/36_tool_use/tools.py

@spl_tool
def sum_values(csv: str) -> str:
    """Sum a comma-separated list of numbers."""
    values = [float(v.strip()) for v in csv.split(",") if v.strip()]
    return str(sum(values))

@spl_tool
def percentage_change(old: str, new: str) -> str:
    """Compute percentage change from old to new."""
    old_f = float(old.replace(",", "").strip())
    new_f = float(new.replace(",", "").strip())
    if old_f == 0:
        return "N/A"
    change = ((new_f - old_f) / abs(old_f)) * 100
    sign = "+" if change >= 0 else ""
    return f"{sign}{change:.2f}"

@spl_tool
def format_currency(amount: str, symbol: str = "USD") -> str:
    """Format as currency string: 'USD 1,234.56'."""
    val = float(amount.replace(",", "").strip())
    return f"{symbol} {val:,.2f}"
```

The SPL workflow delegates all arithmetic to these tools and sends only the narrative summary to the LLM:

```spl
WORKFLOW sales_analysis
  INPUT:  @sales TEXT, @prev_total TEXT, @period TEXT
  OUTPUT: @report TEXT
DO
  -- Deterministic math — zero LLM tokens, no hallucination risk
  CALL sum_values(@sales)                     INTO @total
  CALL average_values(@sales)                 INTO @avg
  CALL percentage_change(@prev_total, @total) INTO @growth
  CALL format_currency(@total)                INTO @total_fmt

  -- LLM only writes the narrative
  GENERATE sales_report(@period, @total_fmt, @avg, @growth) INTO @report
  COMMIT @report
END
```

Run it:

```bash
spl run cookbook/36_tool_use/tool_use.spl \
    --adapter ollama -m gemma3 \
    --tools cookbook/36_tool_use/tools.py \
    sales="1200,1450,1380,1600,1750,1900" \
    prev_total="7800" \
    period="H1 2025"
```

<!-- --- -->

## Writing Good UDFs

### Accept and return strings

SPL variables are strings. Tools receive strings and should return strings (or Python primitives that get coerced to strings). Avoid returning complex objects.

```python
# Good — returns a string
@spl_tool
def extract_domain(email: str) -> str:
    return email.split("@")[-1] if "@" in email else ""

# Also fine — Python int/float returned, coerced by executor
@spl_tool
def word_count(text: str) -> int:
    return len(text.split())
```

### Fail safely

LLM output is unpredictable. Guard against malformed input rather than raising exceptions that halt the workflow.

```python
@spl_tool
def parse_score(text: str) -> float:
    """Extract a 0-1 score from LLM text. Returns 0.0 on any failure."""
    import re
    m = re.search(r"\b(0?\.\d+|1\.0|[01])\b", str(text))
    return float(m.group()) if m else 0.0
```

### Pure functions when possible

Tools without side effects are trivially testable and composable. Reserve I/O (database, API, file) for tools that genuinely need it.

```python
# Pure — easy to test in isolation
@spl_tool
def normalize_name(name: str) -> str:
    return " ".join(w.capitalize() for w in name.strip().split())

# Impure — I/O justified; wrap carefully
@spl_tool
def lookup_customer(customer_id: str) -> str:
    row = db.query("SELECT name, tier FROM customers WHERE id = ?", customer_id)
    return json.dumps(row) if row else ""
```

### Document with docstrings

The docstring becomes the tool's description in `spl explain` output. Write it for the workflow author, not the Python author.

```python
@spl_tool
def detect_language(text: str) -> str:
    """Detect the ISO 639-1 language code for the input text.

    Returns a 2-letter code like 'en', 'fr', 'zh'.
    Returns 'unknown' if detection confidence is below threshold.
    Requires: pip install langdetect
    """
    ...
```

<!-- --- -->

## Custom Name

If the Python function name cannot be used in SPL (conflicts with a keyword, or you want a shorter name), pass `name=` to the decorator:

```python
@spl_tool(name="pct_change")
def compute_percentage_change_with_guard(old: str, new: str) -> str:
    ...
```

```spl
CALL pct_change(@prev, @curr) INTO @delta
```

<!-- --- -->

## Multiple Tools in One File

A single `tools.py` can register any number of tools. Group them by domain:

```python
# tools.py — order management tools

@spl_tool
def lookup_order(order_id: str) -> str:
    """Return JSON with order status and items for an order ID."""
    ...

@spl_tool
def extract_order_numbers(text: str) -> str:
    """Extract all ORD-XXXXXX order numbers from text as a comma-separated list."""
    import re
    return ", ".join(re.findall(r"ORD-\d{6}", text))

@spl_tool
def format_order_summary(order_json: str) -> str:
    """Format an order JSON payload as a human-readable summary."""
    ...
```

Load all of them with a single flag:

```bash
spl run workflow.spl --tools tools.py
```

<!-- --- -->

## Async Tools

For I/O-bound operations (HTTP calls, database queries), define the tool as an `async def`. The SPL executor runs inside `asyncio`, so async tools compose naturally:

```python
import httpx
from spl.tools import spl_tool

@spl_tool
async def fetch_webpage(url: str) -> str:
    """Fetch the text content of a webpage (first 4000 chars)."""
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        return r.text[:4000]
```

```spl
CALL fetch_webpage(@url) INTO @page_text
GENERATE summarize(@page_text) INTO @summary
```

<!-- --- -->

## Stdlib vs. UDF: The Decision Rule

| Question | Answer |
|---|---|
| Is it a general-purpose string/numeric/date operation? | Use **stdlib** |
| Does it require external I/O (DB, API, file)? | Write a **UDF** |
| Is it domain-specific (PII, financial, medical)? | Write a **UDF** |
| Could it appear in any SQL database's built-in list? | Use **stdlib** |
| Does it encode business rules specific to your org? | Write a **UDF** |

The stdlib exists so you never write `to_float` or `upper` again. UDFs exist so you can encode the things that only your team knows.

<!-- --- -->

## Testing Your Tools

Because tools are plain Python, they test with plain `pytest` — no LLM runtime needed:

```python
# test_tools.py
from tools import extract_order_numbers, parse_score

def test_extract_orders():
    text = "Customer mentioned ORD-123456 and ORD-789012 were delayed."
    assert extract_order_numbers(text) == "ORD-123456, ORD-789012"

def test_parse_score_lenient():
    assert parse_score("Quality: 0.87 out of 1.0") == 0.87
    assert parse_score("no number here") == 0.0
    assert parse_score("") == 0.0
```

```bash
pytest test_tools.py -v
```

Testing tools in isolation — before wiring them into a workflow — is the fastest feedback loop in SPL development. Fix the Python logic here, not inside a 30-second LLM run.

<!-- --- -->

## The Guardrails Recipe: A Real UDF Pattern

section 4.2 (Guardrails Pipeline) shows UDFs doing exactly what an LLM should not: deterministic pattern matching.

```python
# cookbook/18_guardrails/tools.py (excerpt)

@spl_tool
def classify_input_keywords(text: str) -> str:
    """Keyword pre-screen: returns 'harmful', 'off_topic', or 'safe'."""
    lower = text.lower()
    for kw in _HARMFUL_KEYWORDS:
        if kw in lower:
            return "harmful"
    for kw in _OFF_TOPIC_KEYWORDS:
        if kw in lower:
            return "off_topic"
    return "safe"

@spl_tool
def detect_pii(text: str) -> str:
    """Regex PII detection. Returns 'pii_found' or 'clean'."""
    ...
```

The EVALUATE in the workflow branches on these exact string values — no LLM involved, no hallucination risk, microsecond latency:

```spl
CALL classify_input_keywords(@user_input) INTO @keyword_class
EVALUATE @keyword_class
    WHEN 'harmful'   THEN COMMIT 'I cannot help with that.' WITH status = 'blocked'
    WHEN 'off_topic' THEN COMMIT 'Outside my scope.'         WITH status = 'blocked'
    OTHERWISE             -- pass through to LLM classification
END
```

This is the UDF pattern at its best: deterministic gates that protect LLM calls, not replace them.
