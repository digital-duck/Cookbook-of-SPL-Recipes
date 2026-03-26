# SPL Standard Library

<!-- *"Good tools should feel like they were always there."* -->

<!-- --- -->

Every SQL database ships with a standard library of functions — `UPPER`, `ROUND`, `COALESCE`, `JSON_GET` — so practitioners never need to rewrite the same utility logic. SPL 2.0 follows the same philosophy. The SPL Standard Library (`spl.stdlib`) provides 55 built-in functions that are available in every workflow without any `--tools` flag or import statement.

```spl
-- These just work — no --tools needed
CALL to_float(@score_str) INTO @score
CALL upper(@name)         INTO @name_upper
CALL coalesce(@a, @b, 'default') INTO @result
CALL json_get(@payload, 'status') INTO @status
```

The stdlib is auto-loaded when the `spl` package is imported. It is the equivalent of SQL's built-in function set.

<!-- --- -->

## Type Conversion

The most common need: LLMs return everything as text. These functions cast that text to the type you need.

| Function | SQL equivalent | Description |
|---|---|---|
| `to_float(value)` | `CAST(x AS FLOAT)` | Extract first decimal number; returns `0.0` on failure |
| `to_int(value)` | `CAST(x AS INTEGER)` | Truncate to integer; returns `0` on failure |
| `to_text(value)` | `CAST(x AS TEXT)` | Any value → string |
| `to_bool(value)` | `CAST(x AS BOOLEAN)` | `'true'/'false'`; truthy: `1, true, yes, on, t, y` |

`to_float` is deliberately lenient — it extracts the first numeric token from the string, so LLM output like `"Quality score: 0.85\n"` or `"I rate this 0.85 out of 1.0"` both return `0.85`.

```spl
-- Pattern: LLM returns a score string; compare it numerically
GENERATE rate_quality(@text) INTO @score_str
CALL to_float(@score_str) INTO @score

EVALUATE @score
    WHEN > 0.8 THEN COMMIT @text WITH grade = 'A'
    WHEN > 0.6 THEN COMMIT @text WITH grade = 'B'
    ELSE       COMMIT @text WITH grade = 'C'
END
```

<!-- --- -->

## String Functions

Mirrors the SQL string function set exactly.

| Function | SQL equivalent | Description |
|---|---|---|
| `upper(value)` | `UPPER(x)` | Uppercase |
| `lower(value)` | `LOWER(x)` | Lowercase |
| `trim(value)` | `TRIM(x)` | Strip leading/trailing whitespace |
| `ltrim(value)` | `LTRIM(x)` | Strip leading whitespace |
| `rtrim(value)` | `RTRIM(x)` | Strip trailing whitespace |
| `length(value)` | `LEN(x)` / `LENGTH(x)` | Character count |
| `substr(value, start, length)` | `SUBSTR(x, s, n)` | 1-based substring; omit length for rest of string |
| `replace(value, old, new)` | `REPLACE(x, old, new)` | Replace all occurrences |
| `concat(a, b, ...)` | `CONCAT(...)` | Concatenate strings |
| `instr(value, search)` | `INSTR(x, s)` | 1-based index of first match; `0` if not found |
| `lpad(value, width, fill)` | `LPAD(x, w, f)` | Left-pad to width |
| `rpad(value, width, fill)` | `RPAD(x, w, f)` | Right-pad to width |
| `split_part(value, delim, n)` | `SPLIT_PART(x, d, n)` | 1-based nth token after splitting |
| `reverse(value)` | `REVERSE(x)` | Reverse a string |

<!-- --- -->

## Pattern Matching

| Function | SQL equivalent | Description |
|---|---|---|
| `like(value, pattern)` | `x LIKE p` | SQL wildcards: `%` = any chars, `_` = any char |
| `startswith(value, prefix)` | — | Returns `'true'` or `'false'` |
| `endswith(value, suffix)` | — | Returns `'true'` or `'false'` |
| `contains(value, substring)` | — | Returns `'true'` or `'false'` |
| `regexp_match(value, pattern)` | `REGEXP_LIKE(x, p)` | Python regex; returns `'true'` or `'false'` |

Pattern functions return the strings `'true'` and `'false'` so they compose with `EVALUATE`:

```spl
CALL startswith(@category, 'error') INTO @is_error
EVALUATE @is_error
    WHEN 'true' THEN COMMIT @event WITH severity = 'high'
    ELSE        COMMIT @event WITH severity = 'normal'
END
```

<!-- --- -->

## Numeric Functions

| Function | SQL equivalent | Description |
|---|---|---|
| `abs_val(value)` | `ABS(x)` | Absolute value |
| `round_val(value, decimals)` | `ROUND(x, n)` | Round to n decimal places (default 0) |
| `ceil_val(value)` | `CEIL(x)` | Smallest integer ≥ value |
| `floor_val(value)` | `FLOOR(x)` | Largest integer ≤ value |
| `mod_val(dividend, divisor)` | `MOD(a, b)` | Remainder |
| `power_val(base, exponent)` | `POWER(x, n)` | Exponentiation |
| `sqrt_val(value)` | `SQRT(x)` | Square root |
| `sign_val(value)` | `SIGN(x)` | `-1`, `0`, or `1` |
| `clamp(value, lo, hi)` | — | Constrain to `[lo, hi]` range |

<!-- --- -->

## Conditional Functions

| Function | SQL equivalent | Description |
|---|---|---|
| `coalesce(a, b, ...)` | `COALESCE(...)` | First non-null, non-empty argument |
| `nullif(value, compare)` | `NULLIF(x, y)` | Returns `''` if value equals compare |
| `iif(condition, true_val, false_val)` | `IIF(c, t, f)` | Inline if; truthy: `1, true, yes` |

```spl
-- Use coalesce to provide fallback values from LLM output
GENERATE extract_summary(@doc) INTO @summary
CALL coalesce(@summary, @doc) INTO @final   -- fall back to original if summary is blank
```

<!-- --- -->

## Null and Empty Checks

| Function | SQL equivalent | Description |
|---|---|---|
| `isnull(value)` | `IS NULL` | `'true'` if None or empty string |
| `nvl(value, default)` | `NVL(x, d)` | Return default if null/empty (Oracle-style) |
| `isblank(value)` | — | `'true'` if empty or only whitespace |

<!-- --- -->

## Text Aggregates

Useful for measuring LLM output properties without calling another LLM.

| Function | Description |
|---|---|
| `word_count(value)` | Whitespace-delimited token count |
| `char_count(value)` | Characters excluding whitespace |
| `line_count(value)` | Newline-separated line count |

```spl
-- Enforce output length without a second LLM call
GENERATE write_summary(@doc) INTO @summary
CALL word_count(@summary) INTO @words

EVALUATE @words
    WHEN > 150 THEN
        GENERATE shorten(@summary) INTO @summary
    ELSE
        -- length is acceptable
END
```

<!-- --- -->

## JSON Functions

Essential for structured-output workflows where LLMs return JSON payloads.

| Function | SQL equivalent | Description |
|---|---|---|
| `json_get(json, key)` | `JSON_VALUE(x, path)` | Extract field; supports dot notation `'a.b'` |
| `json_set(json, key, value)` | — | Set a top-level key; returns updated JSON string |
| `json_keys(json)` | — | Comma-separated list of top-level keys |
| `json_length(json)` | `JSON_ARRAY_LENGTH(x)` | Number of keys (object) or items (array) |
| `json_pretty(json)` | — | Pretty-print with 2-space indent |

```spl
-- Extract fields from a structured LLM response
GENERATE classify(@text) INTO @json_response
CALL json_get(@json_response, 'category') INTO @category
CALL json_get(@json_response, 'confidence') INTO @conf_str
CALL to_float(@conf_str) INTO @confidence
```

<!-- --- -->

## Date and Time

| Function | SQL equivalent | Description |
|---|---|---|
| `now_iso()` | `NOW()` | Current UTC time as `YYYY-MM-DDTHH:MM:SS` |
| `date_format_val(date, fmt)` | `DATE_FORMAT(x, f)` | Reformat ISO date with `strftime` format string |
| `date_diff_days(date_a, date_b)` | `DATEDIFF(a, b)` | Days between two ISO dates (a − b) |

<!-- --- -->

## Hashing

| Function | SQL equivalent | Description |
|---|---|---|
| `md5_hash(value)` | `MD5(x)` | MD5 hex digest — useful for deduplication keys |
| `sha256_hash(value)` | `SHA2(x, 256)` | SHA-256 hex digest |

<!-- --- -->

## List / Array Helpers

SPL variables are strings. These functions treat a delimited string as an array — useful when a CALL tool returns a comma-separated list.

| Function | Description |
|---|---|
| `list_get(value, index, delimiter)` | 1-based element from delimited list (default delimiter: `,`) |
| `list_length(value, delimiter)` | Number of elements |
| `list_join(value, old_delim, new_delim)` | Re-join with a different delimiter |
| `list_contains(value, item, delimiter)` | `'true'` if item is in list |

```spl
-- Parse a comma-separated LLM response into individual items
GENERATE list_topics(@domain) INTO @topics_csv
CALL list_length(@topics_csv) INTO @count
CALL list_get(@topics_csv, '1') INTO @first_topic
```

<!-- --- -->

## Stdlib vs. UDFs

The stdlib covers routine operations. When you need domain-specific logic — PII detection, database lookups, API calls, file I/O — write a UDF. See Chapter 10.4 for how to extend SPL with your own tools.

The decision rule is simple: if you could express it as a SQL built-in function, it belongs in stdlib. If it requires external state, I/O, or domain knowledge, it belongs in a `tools.py` UDF.
