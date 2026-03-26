# Structured Output

<!-- *"The bridge between human language and machine logic is a well-defined schema." — Wen Gong* -->

<!-- --- -->

## The Pattern

One of the most powerful features of modern LLMs is their ability to perform **Data Extraction**. You can give them a pile of unstructured text—a lease agreement, a medical report, a customer email—and ask them to "Find the people, the amounts, and the dates."

But if you just ask the model for "JSON," you run a high risk of getting different field names every time. One model might return `{"price": 100}`, another `{"cost": 100}`, and a third might return the price as a string: `{"price": "$100"}`. This inconsistency is the "Data Engineering" nightmare of the AI age.

The **Structured Output** pattern solves this by using a **Schema**. You don't just ask for JSON; you provide a formal definition (usually a JSON Schema) and tell the model: "Your response must match this exact structure, with these exact types."

The SQL analogy is a **Table Schema** or a **CHECK Constraint**. You don't just "Insert data" into a database. You define columns, types (INTEGER, TEXT, BOOLEAN), and constraints. The database ensures that every row matches that schema, and SPL ensures that every LLM response matches your schema.

The Structured Output recipe (section 8.5) demonstrates how to use `CREATE FUNCTION` to define a complex schema for multi-entity extraction.

<!-- --- -->

## The SPL Approach

This recipe uses a **Schema-Driven Prompt** pattern, where the output format is a first-class citizen in the `SELECT` context.

<!-- --- -->

## The .spl File (Annotated)

```spl
-- Recipe 23: Structured Output
-- Extract typed data from text using JSON schema.

CREATE FUNCTION extract_entity_schema()      -- (1) Reusable Schema Definition
RETURNS JSON AS $$
{
  "type": "object",
  "properties": {
    "people": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name":   { "type": "string" },
          "age":    { "type": "integer" },   -- (2) Enforcing numeric types
          "salary": { "type": "number" }
        }
      }
    }
  }
}
$$;

PROMPT extract_entities
SELECT
    system_role('You are a precise data extraction engine.'),
    context.text AS text,
    extract_entity_schema() AS schema       -- (3) Schema context injection
GENERATE structured_extraction(text, schema) -- (4) Constrained generation
```

### (1) Reusable Schema Definition

We define the JSON Schema inside a `CREATE FUNCTION`. This is the "Data Blueprint." By separating it from the prompt, we make the schema reusable across multiple different extraction tasks (e.g., from emails, from PDFs, from web scrapes).

### (2) Enforcing Numeric Types

Notice the `"type": "integer"` for age. By providing this hint to the model (and the adapter), we ensure that the output is a raw number (e.g., `42`) rather than a string (`"42"`). This means you can immediately use the output in a calculation without an extra `int()` step in Python.

### (3) Schema Context Injection

We include the `schema` in the context row of our `SELECT` clause. This ensures the model always has the "Rules of the Game" visible while it is thinking.

### (4) Constrained Generation

The `GENERATE` step takes the `text` and the `schema`. Depending on the adapter (e.g., OpenRouter or OpenAI), SPL uses the provider's "Structured Output" feature to force the model to comply with the schema. If the model tries to return invalid JSON, the runtime (or the provider) will often catch it and retry automatically.

<!-- --- -->

## Running It

Run the extractor on a messy string:

```bash
spl run cookbook/23_structured_output/structured_output.spl --adapter ollama \
    text="John Smith, 42, joined Acme Corp earning $95,000/year"
```

Expected output (clean JSON):
```json
{
  "people": [
    { "name": "John Smith", "age": 42, "salary": 95000 }
  ],
  "organizations": [
    { "name": "Acme Corp" }
  ]
}
```

<!-- --- -->

## What Just Happened

**LLM calls: 1.**

The "Conductor" (SPL Runtime) managed the "Data Capture":
1.  **Prepared** the input text.
2.  **Attached** the formal data blueprint (the schema).
3.  **Instructed** the model to operate as a "Transpiler" from prose to JSON.
4.  **Verified** (at the adapter level) that the response was valid and typed.

This is how you build a **Production-Ready Data Pipeline**. By the time the data reaches your downstream application, it is already cleaned, typed, and structured.

<!-- --- -->

## Reproducibility Note

Structured output is one of the most stable features of modern LLMs. 
Even on small models like **gemma3**, providing a formal JSON Schema increases reliability significantly. It reduces the model's "Creative Freedom" and forces it into a "Deterministic Format."

On a **GTX 1080 Ti**, structured generation is just as fast as unstructured generation, but it saves you the "Latency of Error" (the time spent dealing with broken JSON or missing fields).

<!-- --- -->

## When to Use This Pattern

Use the **Structured Output** pattern when:
- **ETL Pipelines**: Extracting data from thousands of documents into a database.
- **Form Filling**: Turning a voice transcript into a structured customer record.
- **Workflow Inputs**: When the output of one step needs to be precisely parsed as the input for a calculation or a tool call (Chapter 3.2).

<!-- --- -->

## Exercises

1.  **Add a "Required" Field.** Modify the schema to make the `salary` field required. Run it on text that *doesn't* have a salary and see how the model behaves (does it guess? does it return null?).
2.  **Extract an Invoice.** Update the schema to include `invoice_number` and `date`. Run it on the invoice text provided in the cookbook.
3.  **Cross-Schema Validation.** Try giving the model two different schemas in the same `SELECT` and ask it to choose the one that fits the text best.
