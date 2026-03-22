# Support Triage

*"Intelligence is only useful when it is grounded in fact."*

---

## The Pattern

Customer support is the "front line" of any business. But manually triaging thousands of tickets is exhausting. A human has to read the ticket, find the customer's order in a database, decide how urgent it is, and then draft a polite response. If the human is tired, they might miss an urgent complaint or cite the wrong order status.

**Grounded Triage** is the pattern of using deterministic tools to "feed" the LLM the facts it needs *before* it starts reasoning. 
1.  **Extract**: Find order IDs or account numbers in the ticket text.
2.  **Lookup**: Fetch the actual record from your database (or a JSON file).
3.  **Reason**: Use the model to classify the ticket and score its urgency, using the real record as the "Ground Truth."
4.  **Execute**: Either escalate the ticket immediately or draft a response that cites the verified facts.

The SQL analogy is a **LEFT JOIN with a CASE Statement**. You are joining the "Incoming Ticket" (unstructured) with your "Orders Table" (structured) and then using logic to route the result to the right "Department" (table/outcome).

The Support Triage recipe (Recipe 28) implements this full end-to-end pipeline. It shows how SPL can coordinate between Python scripts (for database lookups) and LLMs (for drafting and classification).

---

## The SPL Approach

This recipe introduces the concept of **Grounding Context**—passing verified data into a `GENERATE` call to prevent hallucinations.

---

## The .spl File (Annotated)

```spl
-- Recipe 28: Customer Support Triage
-- Classify → route → draft response grounded in real data.

WORKFLOW support_triage
    INPUT: @ticket TEXT, @tone TEXT DEFAULT 'professional'
DO
    -- Phase 1: Fact Finding (Deterministic)
    CALL extract_order_numbers(@ticket) INTO @order_id -- (1) Python Regex Tool
    CALL lookup_order(@order_id) INTO @order_record    -- (2) Python Database Tool

    -- Phase 2: Intelligence (Probabilistic)
    GENERATE classify_ticket(@ticket, @order_record) INTO @class -- (3) Grounded classification
    GENERATE detect_urgency(@ticket) INTO @urgency

    -- Phase 3: Routing (Branching)
    EVALUATE @urgency
        WHEN > 8 THEN                                  -- (4) Critical Escalation
            GENERATE escalation_alert(@ticket, @class) INTO @alert
            COMMIT @alert WITH status = 'escalated'
        OTHERWISE
            -- Phase 4: Response Generation
            GENERATE draft_response(
                @ticket, 
                @order_record,                         -- (5) Citing the Ground Truth
                response_tone_guide(@tone)
            ) INTO @draft

            -- Phase 5: Quality Gate
            GENERATE check_quality(@draft) INTO @score
            EVALUATE @score
                WHEN < 6 THEN GENERATE improve(@draft) INTO @draft
            END
            
            COMMIT @draft WITH status = 'drafted'
    END
END
```

### (1) & (2) Fact Finding (`CALL`)

We use two Python tools. The first uses a regex to find strings like `#ORD-12345`. The second takes that ID and looks it up in an `orders.json` file. 
- **Why?** Because LLMs are bad at "remembering" order statuses but great at "summarizing" them. We provide the status as a raw fact.

### (3) Grounded Classification

When we ask the model to classify the ticket (e.g., "Billing" vs "Shipping"), we provide the `@order_record`. If the customer is complaining about a charge and the record shows "Payment Failed," the model can accurately classify it as a billing issue without guessing.

### (4) Critical Escalation

Using the `EVALUATE` block, we build a "Safety Valve." If the urgency is high (e.g., an angry customer threatening to cancel), we bypass the drafting phase and send an immediate alert to a human manager.

### (5) Citing the Ground Truth

In the `draft_response` step, the model sees exactly what is in the database. Instead of saying "Your order should arrive soon," it can say "I see your order #ORD-12345 was shipped via DHL on Tuesday and is currently in Memphis." This builds massive trust with the customer.

---

## Running It

Run the triage on a billing complaint:

```bash
spl run cookbook/28_support_triage/support_triage.spl \
    --adapter ollama --tools cookbook/28_support_triage/tools.py \
    ticket="I was charged twice for order #ORD-12345"
```

Observe the trace. You will see the Python tool fetching the record for ORD-12345 and the model using that record to apologize for the duplicate charge.

---

## What Just Happened

**LLM calls: 4–6.**
**Tool calls: 2.**

The "Conductor" (SPL Runtime) managed a "Smart Agent":
1.  **Audited** the input for structured identifiers.
2.  **Queried** the system of record for the facts.
3.  **Assessed** the situation (classification + urgency).
4.  **Routed** the work based on the assessment.
5.  **Drafted** a factually accurate, tone-correct response.

---

## Reproducibility Note

The reliability of this recipe is 100% for the "Fact" part because it uses Python tools. The "Draft" part depends on the model's tone. 

On a **GTX 1080 Ti**, the entire triage takes **15–25 seconds**. Compared to a human taking 5–10 minutes to do the same lookups and typing, this is a **20x–40x speedup** for the support team.

---

## When to Use This Pattern

Use the **Support Triage** pattern when:
- **High Volume Inbound**: Thousands of emails or chats that need a first-pass response.
- **Database-Dependent Tasks**: Any task where the "Right Answer" lives in a database, not in the LLM's brain.
- **SLA Management**: Automatically identifying urgent tickets to ensure they are handled within the required time window.

---

## Exercises

1.  **Add an "Unknown Order" path.** Modify the workflow so that if `@order_record` is empty, the model drafts a response asking the customer for their order number.
2.  **Custom Tone.** Change the `@tone` parameter to "extremely formal" and observe how the model rephrases the same order facts.
3.  **Proactive Refund.** (Advanced) Add a Python tool `issue_refund()` and a step that calls it automatically if the classification is "billing" and the urgency is "critical."
