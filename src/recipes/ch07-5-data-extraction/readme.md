# ch07-5: Data Extraction

Pulls structured fields from messy free-form text using schema-constrained extraction. Supports three formats: `general`, `invoice`, and `contract`.

## Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `text` | TEXT | *(required)* | The raw text to extract fields from |
| `format` | TEXT | `general` | Schema type: `general`, `invoice`, or `contract` |

## Usage

```bash
# General extraction (names, dates, amounts, references)
# Local Ollama
spl run src/recipes/ch07-5-data-extraction/data_extraction.spl --adapter ollama \
    text="Please process payment of USD 4,250.00 to Riverside Consulting (ref: PO-8821) by end of March."

# Momagrid
spl run src/recipes/ch07-5-data-extraction/data_extraction.spl --adapter momagrid \
    text="Please process payment of USD 4,250.00 to Riverside Consulting (ref: PO-8821) by end of March."

# Invoice extraction
# Local Ollama
spl run src/recipes/ch07-5-data-extraction/data_extraction.spl --adapter ollama \
    text="$(cat invoice.txt)" \
    format="invoice"

# Momagrid
spl run src/recipes/ch07-5-data-extraction/data_extraction.spl --adapter momagrid \
    text="$(cat invoice.txt)" \
    format="invoice"

# Contract extraction
# Local Ollama
spl run src/recipes/ch07-5-data-extraction/data_extraction.spl --adapter ollama \
    text="$(cat contract.txt)" \
    format="contract"

# Momagrid
spl run src/recipes/ch07-5-data-extraction/data_extraction.spl --adapter momagrid \
    text="$(cat contract.txt)" \
    format="contract"
```

## Schemas

| Format | Extracted fields |
|---|---|
| `general` | names, organizations, dates, amounts, references, locations |
| `invoice` | invoice_number, vendor, amount, currency, issue_date, due_date, line_items, po_reference |
| `contract` | parties, effective_date, expiry_date, value, jurisdiction, key_obligations |
