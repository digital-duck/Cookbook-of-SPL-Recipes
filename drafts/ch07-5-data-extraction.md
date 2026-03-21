# Chapter 7.5 — Data Extraction

*"The real world is messy; your data doesn't have to be."*

---

## The Pattern

Most data extraction tutorials use "perfect" examples—clean, short sentences where the information is easy to find. In the real world, data is buried in noisy, unstructured text: emails with three different addresses, invoices with cryptic line items, or contracts with hundreds of clauses.

**Schema-Constrained Extraction** is the professional way to handle this noise. Instead of asking the model to "find the data," you provide a **dynamic schema** that changes based on the *type* of document you are processing.

The SQL analogy is **Dynamic Schema Mapping** or a **Pivot Table**. You are taking a raw "blob" of text and forcing it into a predefined relational structure (rows and columns) that your downstream database can understand.

The Data Extraction recipe (Recipe 27) implements this pattern. It uses a `CREATE FUNCTION` block to deliver different extraction schemas based on a `format` parameter (e.g., `invoice`, `contract`, or `general`). This allows a single workflow to handle a wide variety of business documents with high precision.

---

## The SPL Approach

This recipe demonstrates **Conditional Schema Injection**—choosing the data blueprint at runtime based on the input type.

---

## The .spl File (Annotated)

```spl2
-- Recipe 27: Data Extraction
-- Pull structured fields from messy text using dynamic schemas.

CREATE FUNCTION extraction_schema(format TEXT DEFAULT 'general')
RETURNS JSON AS $$
SELECT CASE format                          -- (1) The Blueprint Library
  WHEN 'invoice' THEN '{
    "type": "object",
    "properties": {
      "invoice_number": {"type": "string"},
      "amount":         {"type": "number"},
      "vendor":         {"type": "string"}
    }
  }'
  WHEN 'contract' THEN '{
    "type": "object",
    "properties": {
      "parties":        {"type": "array", "items": {"type": "string"}},
      "value":          {"type": "number"}
    }
  }'
  ELSE '{ ... general schema ... }'         -- (2) Fallback schema
END
$$;

PROMPT extract_fields
SELECT
    system_role('You are a data extraction specialist.'),
    context.text AS text,
    extraction_schema(context.format) AS schema -- (3) Injecting the right blueprint
GENERATE extract(text, schema)              -- (4) Precision extraction
```

### (1) & (2) The Blueprint Library

Instead of writing three different `.spl` files for invoices, contracts, and emails, we keep all our "Data Blueprints" in one function. This makes it easy to maintain a consistent extraction standard across your entire organization.

### (3) Injecting the right blueprint

In the `SELECT` clause, we pass the user-provided `format` into the `extraction_schema` function. 
- If the user says `format="invoice"`, the LLM sees the invoice schema.
- If they say `format="contract"`, it sees the contract schema.

This is the "Just-in-Time" context pattern that keeps the model focused only on the fields that matter for the current document.

### (4) Precision Extraction

The `GENERATE` step uses the schema to constrain the output. Because we explicitly defined `amount` as a `"number"`, the model will strip out currency symbols and commas, returning a value that can be directly inserted into a `DECIMAL` column in a SQL database.

---

## Running It

Extract data from a noisy payment request:

```bash
spl2 run cookbook/27_data_extraction/data_extraction.spl --adapter ollama \
    text="Please process payment of USD 4,250.00 to Riverside Consulting (ref: PO-8821)" \
    format="invoice"
```

Expected output:
```json
{
  "invoice_number": "PO-8821",
  "vendor": "Riverside Consulting",
  "amount": 4250.00,
  "currency": "USD"
}
```

---

## What Just Happened

**LLM calls: 1.**

The "Conductor" (SPL Runtime) managed the "Factory Line":
1.  **Categorized** the work using the `format` parameter.
2.  **Selected** the correct extraction tool (the schema).
3.  **Filtered** the noisy input text through that tool.
4.  **Delivered** a perfectly structured data object.

---

## Reproducibility Note

The stability of extraction is highly dependent on the **Schema Complexity**. If your schema has 50 fields, small models might miss some. For complex extraction, we recommend using **gemma3 (27B)** or **Claude 3.5 Sonnet**.

On a **GTX 1080 Ti**, a standard invoice extraction takes **2–4 seconds**. The bottleneck is the number of tokens in the input document, not the complexity of the schema itself.

---

## When to Use This Pattern

Use the **Data Extraction** pattern when:
- **Legacy Migration**: You have thousands of old text files that need to be moved into a modern database.
- **Workflow Automation**: When a human email needs to trigger an automated business process (like paying a bill).
- **Audit Compliance**: When you need to ensure that every document processed by your system contains specific required fields.

---

## Exercises

1.  **Add a "Sentiment" Field.** Modify the "general" schema to include a `tone` field (e.g., "urgent," "polite," "angry") so you can prioritize the extracted data.
2.  **Handle Multi-Entity.** Modify the "invoice" schema to include an `array` of `line_items`, each with a `description` and a `price`.
3.  **Strict Mode.** (Advanced) Research the `"additionalProperties": false` flag in JSON Schema and see how it prevents the model from adding extra, unrequested fields to the output.
