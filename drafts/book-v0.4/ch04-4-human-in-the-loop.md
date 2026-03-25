# Human-in-the-Loop Approval Gate

<!-- *"Automation without oversight is not efficiency — it is risk deferred." — Wen Gong* -->

<!-- --- -->

### The Pattern

You have an agentic workflow that produces consequential output: a financial report, a customer-facing email, a database mutation, a code deployment. You want the speed of automation but not the risk of fully unsupervised execution. The solution is a human approval gate — a deliberate pause where the workflow surfaces its intermediate result, waits for a human decision, and only proceeds (or aborts) based on that decision.

This is not a sign of weakness in your workflow. It is a design choice. Production agentic systems in regulated industries (finance, healthcare, legal) often *require* human-in-the-loop steps for compliance. Even in unregulated settings, approval gates are the mechanism by which humans maintain meaningful control over automated processes that act on their behalf.

The Python equivalent embeds the approval logic in the application layer — a webhook, a message queue, a polling loop. The result is that the approval logic is separated from the workflow definition, making it hard to read, audit, or modify. SPL keeps the approval gate *inside* the workflow as a named step, visible to anyone reviewing the `.spl` file.

<!-- --- -->

### The SPL Approach

SPL expresses the approval gate through a `CALL` to a tool that blocks until human input is received, combined with conditional logic on the response. The tool handles the mechanics (sending a notification, presenting the draft, waiting for a response); the SPL file handles the workflow logic (what to do when approved, what to do when rejected).

The key insight: the approval step is a **deterministic operation** (`CALL`, not `GENERATE`). It calls a Python tool that returns a structured decision. The workflow branches on that decision using `EVALUATE`. No LLM is involved in the approval step itself — the human *is* the judge.

<!-- --- -->

### The `.spl` File (Annotated)

```sql
-- human_approval_gate.spl
-- Pattern: block workflow at approval checkpoint, branch on human decision

CREATE FUNCTION draft_report(topic TEXT, data TEXT) RETURNS TEXT AS $
You are a professional analyst. Write a concise executive summary report on the following topic.

Topic: {topic}
Source data:
{data}

Format your report with:
- An executive summary (2-3 sentences)
- Key findings (3-5 bullet points)
- Recommended action (1 paragraph)

Write in formal business language. Be specific. Avoid vague generalities.
$;

WORKFLOW approve_and_send_report
  INPUT:
    @topic TEXT DEFAULT 'Q1 Performance Review',
    @data  TEXT DEFAULT 'See attached data file',
    @approver_email TEXT DEFAULT 'manager@example.com'
  OUTPUT:
    @final_report TEXT,
    @disposition  TEXT   -- 'approved' | 'rejected' | 'revised'
DO
  -- Step 1: Generate the draft
  GENERATE draft_report(@topic, @data) INTO @draft

  -- Step 2: Human approval gate
  -- tool.request_approval() sends @draft to @approver_email,
  -- blocks until they respond, and returns a structured decision:
  -- { "decision": "approve"|"reject"|"revise", "comments": "..." }
  CALL tool.request_approval(
    content    = @draft,
    recipient  = @approver_email,
    subject    = 'Approval required: ' || @topic,
    timeout_h  = 24
  ) INTO @approval

  -- Step 3: Branch on the decision
  EVALUATE @approval.decision
    WHEN 'approve' THEN
      @final_report := @draft
      @disposition  := 'approved'
      CALL tool.send_email(
        to      = @approver_email,
        subject = 'Report sent: ' || @topic,
        body    = @final_report
      ) INTO @_
      COMMIT @final_report WITH status = 'sent'

    WHEN 'revise' THEN
      -- Incorporate reviewer comments and generate a revised draft
      GENERATE draft_report(
        @topic,
        @data || '\n\nReviewer comments: ' || @approval.comments
      ) INTO @revised
      @final_report := @revised
      @disposition  := 'revised'
      COMMIT @final_report WITH status = 'revised_pending_send'

    WHEN 'reject' THEN
      @final_report := ''
      @disposition  := 'rejected'
      COMMIT @final_report WITH status = 'rejected'

  END

EXCEPTION
  WHEN TimeoutError THEN
    -- Approval not received within 24 hours
    @disposition := 'timed_out'
    CALL tool.notify(@approver_email, 'Approval request expired: ' || @topic) INTO @_
    COMMIT '' WITH status = 'approval_timed_out'
END
```

**Line-by-line highlights:**

- `CREATE FUNCTION draft_report` — explicit prompt template; the LLM gets a structured role and output format, not an open-ended instruction
- `CALL tool.request_approval(...)` — the approval gate is a deterministic CALL, not GENERATE; the human provides the probabilistic element
- `EVALUATE @approval.decision WHEN ...` — branches cleanly on three outcomes; the `WHEN 'revise'` branch incorporates reviewer comments into a second generation pass
- `EXCEPTION WHEN TimeoutError` — production-grade: if no response within 24 hours, notify and abort rather than hanging indefinitely

<!-- --- -->

### The SQL Analogy

The approval gate is a stored procedure that includes a `WAITFOR` step — an explicit synchronization point that pauses execution until an external condition is met. SQL Server's `WAITFOR DELAY` is the closest syntactic analogue, though the semantics here are event-driven rather than time-driven.

The `EVALUATE @approval.decision WHEN ...` block is a `CASE` statement on the procedure's output. The three branches (approve, revise, reject) correspond exactly to three different code paths in a SQL `IF/ELSIF/ELSE` construct.

The `EXCEPTION WHEN TimeoutError` block is the stored procedure's error handler — the same pattern as `BEGIN ... EXCEPTION WHEN others THEN ... END` in PL/SQL.

<!-- --- -->

### Running It

```bash
# Run with a local approval tool (development mode: auto-approves after 5 seconds)
spl run human_approval_gate.spl \
  --adapter ollama -m gemma3 \
  --tools approval_tools.py \
  --input topic="Q1 Performance Review" \
  --input data="Revenue: $2.4M (+12% YoY). Churn: 3.2% (-0.8pp). NPS: 47 (+5)." \
  --input approver_email="manager@example.com"
```

Expected output (approved path):

```
[draft_report] Generated 312-word executive summary
[request_approval] Sent approval request to manager@example.com
[request_approval] Response received: decision=approve, comments=""
[send_email] Report sent to manager@example.com
Status: sent
```

<!-- --- -->

### What Just Happened

1. `draft_report` was called with the topic and data; the LLM produced a 312-word executive summary
2. `tool.request_approval` sent the draft to the approver and blocked — no LLM tokens consumed during the wait
3. The approver responded with `decision=approve`
4. The workflow took the approval branch, sent the email, and committed with status `sent`

The EVALUATE/EXCEPTION structure means that all three outcomes (approve, revise, reject) and the timeout case are explicitly handled. There is no "what if the human rejects it?" case that falls through to undefined behavior.

<!-- --- -->

### Reproducibility Note

- **Hardware**: GTX 1080 Ti, 11 GB VRAM
- **Model**: Gemma 3 via Ollama
- **Draft generation latency**: 18–25 seconds (varies with report length)
- **Approval tool**: in development mode, `tool.request_approval` returns immediately with `decision=approve`; in production mode, it sends an actual email and blocks on response
- **Revision path**: adds one additional GENERATE call; total latency approximately doubles

<!-- --- -->

### When to Use This Pattern

**Use it when:**
- The workflow output has real-world consequences (sending communications, writing files, calling external APIs)
- Compliance or audit requirements mandate a human sign-off step
- The generation quality is not yet reliably high enough for unsupervised deployment
- You want to train a human reviewer loop that gradually reduces approval frequency as confidence grows

**Do not use it when:**
- The workflow output is purely informational and never acted on automatically
- The approval latency (hours) would defeat the purpose of automation
- The volume of executions makes human review impractical (consider automated quality gates instead — see Recipe 4.2)

**Anti-pattern to avoid:** Treating the approval gate as an afterthought. If the approval step is not in the `.spl` file, it is invisible to anyone reviewing the workflow. Human-in-the-loop logic belongs in the declarative artifact, not in the application layer.

<!-- --- -->

### Exercises

1. Modify the `revise` branch to limit revision attempts: if the reviewer rejects a second revised draft, automatically escalate to a second approver rather than generating a third draft.
2. Add an audit log: call `tool.write_log(disposition, timestamp, reviewer_comments)` at the end of each branch so every workflow execution produces an immutable audit trail.
3. Replace `tool.request_approval` with a Slack webhook: implement `approval_tools.py` so that approval requests are sent as Slack messages with approve/reject buttons, and the tool blocks on the Slack API response.
