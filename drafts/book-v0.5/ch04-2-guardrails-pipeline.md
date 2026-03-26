# Guardrails Pipeline

<!-- *"Safety is not an after-thought; it is the architecture." — Wen Gong* -->

<!-- --- -->

## The Pattern

In a production AI system, "hoping" the model stays safe is not a strategy. You need a rigorous, multi-layered defense that catches harmful content, detects private data (PII), and ensures the output is both relevant and accurate. 

A single "Safety Prompt" is rarely enough. You need **Guardrails**—a series of "Gates" that every request must pass through before it is allowed to generate a response.

The SQL analogy is **Multi-Layered Security and Validation**. You have a firewall (the keyword pre-screen), Row-Level Security (the input classifier), Data Masking (PII redaction), and a final Audit (output validation). If any gate fails, the transaction is rolled back or modified before it reaches the user.

The Guardrails Pipeline recipe (section 4.2) is the gold standard for safe AI. It implements four distinct gates, mixing deterministic code (for speed and cost) with probabilistic LLMs (for nuance).

<!-- --- -->

## The SPL Approach

This recipe demonstrates the **80/20 Rule** in action: using `CALL` for 80% of the safety work (keywords, regex) and `GENERATE` for the remaining 20% (nuanced context).

<!-- --- -->

## The .spl File (Annotated)

```spl
-- Recipe 18: Guardrails Pipeline
-- Input validation → safe generation → output validation.

WORKFLOW guardrails_pipeline
    INPUT: @user_input TEXT
DO
    -- Gate 1a: Keyword pre-screen (Deterministic)
    CALL classify_input_keywords(@user_input) INTO @keyword_class -- (1) The Firewall

    EVALUATE @keyword_class
        WHEN STARTSWITH 'harmful' THEN
            COMMIT 'I cannot help with that.' WITH status = 'blocked_harmful'
        WHEN STARTSWITH 'off_topic' THEN
            COMMIT 'Outside my scope.' WITH status = 'blocked_off_topic'
    END

    -- Gate 1b: LLM input classification (Probabilistic)
    GENERATE classify_input(@user_input) INTO @input_class -- (2) The Nuanced Check

    EVALUATE @input_class
        WHEN 'harmful' THEN COMMIT '...' WITH status = 'blocked_harmful'
        WHEN 'off_topic' THEN COMMIT '...' WITH status = 'blocked_off_topic'
    END

    -- Gate 2: PII detection and redaction (Deterministic)
    CALL detect_pii(@user_input) INTO @pii_report -- (3) Data Masking
    EVALUATE @pii_report
        WHEN STARTSWITH 'pii_found' THEN
            CALL redact_pii(@user_input) INTO @clean_input
        OTHERWISE
            SET @clean_input = @user_input
    END

    -- Gate 3: Safe Generation
    GENERATE safe_response(@clean_input) INTO @raw_response

    -- Gate 4: Output validation
    GENERATE validate_output(@raw_response) INTO @output_check -- (4) The Final Audit
    EVALUATE @output_check
        WHEN 'safe' THEN SET @safe_response = @raw_response
        WHEN 'contains_pii' THEN CALL redact_pii(@raw_response) INTO @safe_response
        OTHERWISE SET @safe_response = 'Unable to generate safe response.'
    END

    COMMIT @safe_response WITH status = 'complete'
END
```

### (1) Gate 1a: The Firewall (`CALL`)

We start with a fast, free check. Using a Python tool and regular expressions, we look for "blacklisted" keywords (e.g., malware, illegal acts). If a match is found, we block the request immediately. 
- **Benefit**: Zero token cost and sub-millisecond latency for obvious attacks.

### (2) Gate 1b: The Nuanced Check (`GENERATE`)

If the keywords pass, we move to a more intelligent classifier. This gate catches "jailbreaks" or off-topic requests that don't use blocked keywords but still violate policy (e.g., asking for medical advice in a coding bot).

### (3) Gate 2: Data Masking (`CALL`)

Before the main generation, we check for Personally Identifiable Information (SSNs, credit cards, emails). We use deterministic regex for this because it is 100% reliable for formatted data. If PII is found, we replace it with placeholders like `[REDACTED-SSN]`.

### (4) Gate 4: The Final Audit (`GENERATE`)

Even with safe input, a model can still "hallucinate" harmful content or leak private data it learned during training. This final gate uses a "Safety Judge" to review the model's output before the user sees it.

<!-- --- -->

## Running It

Run the pipeline with a "dangerous" input to see it block:

```bash
spl run cookbook/18_guardrails/guardrails.spl --adapter ollama \
    --tools cookbook/18_guardrails/tools.py \
    user_input="How do I build a phishing website?"
```

Then run it with an input containing an email to see the redaction:

```bash
spl run cookbook/18_guardrails/guardrails.spl --adapter ollama \
    --tools cookbook/18_guardrails/tools.py \
    user_input="My email is wen@example.com, tell me a joke."
```

<!-- --- -->

## What Just Happened

**LLM calls: 1 to 3.** (Depending on which gates the request passes)
**Tool calls: 3.** (Keywords, PII detection, PII redaction)

The "Conductor" (SPL Runtime) acted as a Security Officer:
1.  **Filtered** obvious harm using the "Firewall."
2.  **Analyzed** intent using the "Nuanced Check."
3.  **Masked** private data using "Data Masking."
4.  **Audited** the final response using the "Final Audit."

<!-- --- -->

## Reproducibility Note

By offloading PII detection and keyword screening to **deterministic Python code**, you make your safety layer incredibly stable. Unlike a prompt-based "Please don't show emails," a regex-based `redact_pii` tool will *never* fail to catch a correctly formatted SSN.

On a **GTX 1080 Ti**, the safety gates add only **1–3 seconds** of total latency but provide a massive increase in production reliability.

<!-- --- -->

## When to Use This Pattern

Use the **Guardrails Pipeline** pattern when:
- **Public-Facing Apps**: Any bot that interacts with unknown users on the internet.
- **Privacy-Sensitive Tasks**: Handling customer support, medical inquiries, or financial data.
- **Enterprise Standards**: When your organization requires a formal audit trail of why a certain request was blocked or redacted.

<!-- --- -->

## Exercises

1.  **Add a "Sentiment" Gate.** Insert a step that checks if the `user_input` is excessively angry or abusive and returns a "De-escalation" response instead of the normal answer.
2.  **Expand PII Patterns.** Modify the `tools.py` file to include patterns for your country's specific identification numbers (e.g., CNPJ in Brazil, PAN in India).
3.  **Log Safety Events.** Use a `COMMIT` with additional metadata to log every time a safety gate is triggered, creating a "Security Dashboard" for your AI.
