# Meeting Actions

<!-- *"Talk is cheap; action items are the currency of progress." — Wen Gong* -->

<!-- --- -->

## The Pattern

Meetings are where decisions are made, but transcripts are where those decisions go to die. A 30-minute meeting can generate 5,000 words of text. Finding the three actual "tasks" buried in those words is a manual chore that everyone hates.

**Structured Meeting Synthesis** is the pattern of converting raw human dialogue into a machine-readable schema. 
1.  **Normalize**: Clean up the transcript (remove "umms," "ahhs," and duplicate lines).
2.  **Extract**: Identify speakers and the specific tasks they committed to.
3.  **Validate**: Use deterministic logic to ensure every task has an "owner" and a "due date."
4.  **Format**: Turn the structured data into a Markdown report or a JSON object for your project management tool (like Jira or Trello).

The SQL analogy is an **Extract-Transform-Load (ETL) Pipeline**. You are extracting raw logs, transforming them into a structured schema, validating them against business rules (e.g., "every task must have an owner"), and loading them into a final report.

The Meeting Actions recipe (Recipe 29) implements this pipeline. it shows how SPL can manage "Long-Form" context by breaking the task into speaker identification, action extraction, and date normalization phases.

<!-- --- -->

## The SPL Approach

This recipe introduces the use of **Schema Grounding**—passing a formal JSON Schema into the `GENERATE` step to ensure the model output is perfectly structured.

<!-- --- -->

## The .spl File (Annotated)

```spl
-- Recipe 29: Meeting Notes → Action Items
-- Transcript in, structured TODO list + owners out.

WORKFLOW meeting_to_actions
    INPUT: @filename TEXT DEFAULT '', @transcript TEXT DEFAULT ''
DO
    -- Phase 1: Pre-processing (Deterministic)
    CALL load_transcript(@filename) INTO @file_content
    CALL extract_speakers(@file_content) INTO @speakers    -- (1) Finding the actors

    -- Phase 2: Synthesis (Probabilistic)
    GENERATE normalize_transcript(@file_content) INTO @clean -- (2) Noise reduction
    
    GENERATE extract_actions(
        @clean,
        action_item_schema(),                             -- (3) The Schema constraint
        @speakers
    ) INTO @structured_json

    -- Phase 3: Post-processing (Deterministic)
    CALL normalize_dates(@structured_json) INTO @iso_json -- (4) Date Fixing
    CALL validate_ownership(@iso_json) INTO @warnings

    -- Phase 4: Delivery
    GENERATE format_as_markdown(@iso_json, @warnings) INTO @output
    COMMIT @output WITH status = 'complete'
END
```

### (1) Finding the Actors (`extract_speakers`)

We use a Python tool to scan the transcript for patterns like `Alice:` or `Bob:`. 
- **Why?** By identifying the names *first*, we can tell the LLM: "Only assign tasks to people in this list." This prevents the model from hallucinating "owners" who weren't actually in the meeting.

### (2) Noise Reduction (`normalize_transcript`)

Before we look for actions, we ask the model to clean up the transcript. This step removes stuttering, filler words, and crosstalk. This makes the next step—extraction—much more accurate because the "Signal-to-Noise" ratio is higher.

### (3) The Schema Constraint (`action_item_schema`)

This is the heart of the recipe. We pass a formal JSON schema into the extraction step. The model is forced to return a list of objects, each with a `task`, `owner`, `priority`, and `due_date`. This transforms a rambling conversation into a strict data structure.

### (4) Date Fixing (`normalize_dates`)

Humans say things like "by Friday" or "next Tuesday." Computers need things like `2026-03-27`. We use a Python tool to convert these relative dates into absolute ISO-8601 strings. This is another example of the **80/20 Rule**: let the LLM understand the *meaning* of "next Friday," but let Python calculate the *value*.

<!-- --- -->

## Running It

Run the action item extractor on a sample sprint planning transcript:

```bash
spl run cookbook/29_meeting_actions/meeting_actions.spl \
    --adapter ollama --tools cookbook/29_meeting_actions/tools.py \
    filename="sprint_planning.txt" \
    output_format="markdown"
```

Expected output:
```markdown
### Meeting Summary
The team discussed the API migration and identified three blockers...

### Action Items
- [ ] **Task**: Fix login bug | **Owner**: Alice | **Due**: 2026-03-27
- [ ] **Task**: Update docs | **Owner**: Bob | **Due**: 2026-03-30
```

<!-- --- -->

## What Just Happened

**LLM calls: 3.** (Normalize, Extract, Format)
**Tool calls: 4.** (Load, Speakers, Dates, Validation)

The "Conductor" (SPL Runtime) managed an "Executive Secretary":
1.  **Identified** the participants.
2.  **Filtered** the conversation for clarity.
3.  **Structured** the commitments into a formal schema.
4.  **Enforced** business rules (dates and owners).
5.  **Presented** the result in a human-readable format.

<!-- --- -->

## Reproducibility Note

The stability of action extraction depends on the **Speaker Consistency**. If the transcript doesn't clearly label who is speaking, the model will have to guess. 

On a **GTX 1080 Ti**, a full 10-minute transcript can be processed in **30–50 seconds**. This is a massive time-saver for teams—the "Meeting Minutes" are ready before everyone has even left the room.

<!-- --- -->

## When to Use This Pattern

Use the **Meeting Actions** pattern when:
- **Agile Teams**: Automating sprint planning or standup summaries.
- **Project Managers**: Ensuring that every decision made in a design review is tracked.
- **Executive Support**: Creating "Briefing Notes" from long interviews or strategy sessions.

<!-- --- -->

## Exercises

1.  **Add a "Decisions" section.** Modify the schema and the extraction step to capture not just tasks, but also "Decisions Made" (e.g., "We decided to use PostgreSQL instead of MongoDB").
2.  **High-Priority Alert.** Modify the `validate_ownership` step to return a specific "URGENT" warning if a task is marked `priority: high` but has no `owner`.
3.  **Export to JSON.** Run the recipe with `output_format="json"` and see how easy it would be to `curl` this data directly into your company's TODO app.
