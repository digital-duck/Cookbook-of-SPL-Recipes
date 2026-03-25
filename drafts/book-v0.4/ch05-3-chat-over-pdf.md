# Chat Over Your PDF

<!-- *"A document that cannot be questioned is not a resource — it is a monument." — Wen Gong* -->

<!-- --- -->

### The Pattern

You have a PDF — a research paper, a contract, a technical specification, a financial report. You want to ask questions about it in natural language and get answers grounded in the document's actual content, not the model's training data.

This is the most commonly requested recipe in the SPL repertoire. "Chat over your documents" is the killer use case for RAG (Retrieval-Augmented Generation) in enterprise settings — it is what most teams mean when they say they want to "do something with AI and our documents."

The naive approach — paste the PDF text into a prompt — fails at scale. PDFs are long. Context windows are finite. A 50-page contract does not fit in a single prompt. Even when it technically fits, the model's attention disperses across the full document and precision drops. The right architecture is *retrieve-then-generate*: find the relevant passages first, then generate an answer from those passages only.

What makes this recipe different from Recipe 5.1 (RAG Query) is the *conversation loop*. Recipe 5.1 answers a single question. This recipe maintains a conversation — tracking what has been asked and answered, so follow-up questions like "What does that mean in practice?" resolve correctly.

<!-- --- -->

### The SPL Approach

Two components work together: a PDF ingestion step (CALL to a tool connector) and a conversational RAG loop (WORKFLOW with memory). The PDF is ingested once at the start of the session; the conversation loop runs until the user ends the session.

The `tool.pdf_to_md()` connector handles the ingestion — no new SPL keywords, just the existing CALL construct routing to a configured tool backend (pymupdf by default). The memory layer stores conversation history so each new question has context from prior exchanges.

<!-- --- -->

### The `.spl` File (Annotated)

```sql
-- chat_over_pdf.spl
-- Pattern: document-grounded conversational Q&A with memory

CREATE FUNCTION answer_question(question TEXT, context TEXT, history TEXT) RETURNS TEXT AS $
You are a precise research assistant. Answer the user's question using ONLY the information in the provided document context. Do not use knowledge from outside the document.

Document context:
{context}

Conversation history (for follow-up resolution):
{history}

User question: {question}

Instructions:
- If the answer is in the document, quote the relevant passage and explain it
- If the answer is NOT in the document, say explicitly: "This information is not in the document"
- Do not speculate beyond what the document states
- Keep your answer concise (under 200 words unless the question requires more)
$;

CREATE FUNCTION extract_search_terms(question TEXT, history TEXT) RETURNS TEXT AS $
Given this conversation history and new question, extract the key search terms needed to find relevant passages in a document.

Conversation history: {history}
New question: {question}

Return only a list of 3-5 search terms or phrases, one per line. Focus on nouns and technical terms. Resolve pronouns using the conversation history (e.g., "it" → the specific thing referenced).
$;

WORKFLOW chat_over_pdf
  INPUT:
    @pdf_path     TEXT DEFAULT './document.pdf',
    @max_turns    INT  DEFAULT 20,
    @top_k_chunks INT  DEFAULT 5
  OUTPUT:
    @turns_completed INT
DO
  -- Step 1: Ingest the PDF once
  CALL tool.pdf_to_md(@pdf_path) INTO @document_text

  -- Step 2: Chunk and index the document for retrieval
  CALL memory.index_document(@document_text, chunk_size=500, overlap=50) INTO @doc_index

  -- Step 3: Initialize conversation state
  @history      := ''
  @turns_completed := 0

  -- Step 4: Conversation loop
  WHILE @turns_completed < @max_turns DO

    -- Get user question (blocks until input received)
    CALL tool.get_user_input(prompt='Ask a question (or type "quit" to exit): ') INTO @question

    -- Exit condition
    EVALUATE @question
      WHEN 'quit' THEN
        COMMIT @turns_completed WITH status = 'session_ended'
        BREAK
    END

    -- Step 4a: Extract search terms, resolving any pronouns via history
    GENERATE extract_search_terms(@question, @history) INTO @search_terms

    -- Step 4b: Retrieve relevant chunks from the indexed document
    CALL memory.retrieve(@doc_index, @search_terms, top_k=@top_k_chunks) INTO @context

    -- Step 4c: Generate a grounded answer
    GENERATE answer_question(@question, @context, @history) INTO @answer

    -- Step 4d: Display and update history
    CALL tool.display(@answer) INTO @_
    @history := @history || 'Q: ' || @question || '\nA: ' || @answer || '\n\n'
    @turns_completed := @turns_completed + 1

  END

  COMMIT @turns_completed WITH status = 'completed'

EXCEPTION
  WHEN ContextLengthExceeded THEN
    -- History grew too long; summarize it and continue
    GENERATE summarize_history(@history) INTO @history_summary
    @history := '[Earlier conversation summarized] ' || @history_summary
    RETRY

  WHEN FileNotFoundError THEN
    COMMIT 0 WITH status = 'pdf_not_found', error = 'PDF file not found: ' || @pdf_path
END
```

**Line-by-line highlights:**

- `CALL tool.pdf_to_md(@pdf_path)` — PDF ingestion via tool connector; no new syntax, just CALL routing to pymupdf (configurable: `--connector pdf=pdfplumber`)
- `CALL memory.index_document(...)` — chunks the document and builds an in-memory retrieval index; chunk size and overlap are tunable INPUT params
- `GENERATE extract_search_terms(...)` — resolves pronouns and extracts search terms *before* retrieval; this step is what makes follow-up questions ("What does *that* mean?") work correctly
- `CALL memory.retrieve(...)` — deterministic retrieval (CALL, not GENERATE); top-k chunks returned as structured context
- `@history` accumulation — running conversation history passed to each `answer_question` call; the model uses it to resolve follow-up references
- `EXCEPTION WHEN ContextLengthExceeded` — when history grows beyond the model's context window, summarize it in-place and retry; the workflow does not crash

<!-- --- -->

### The SQL Analogy

This recipe is a stored procedure with a cursor loop. The `WHILE @turns_completed < @max_turns DO` loop is a `WHILE` loop over a cursor. Each iteration:
1. Fetches a new input row (the user's question)
2. Runs a subquery to retrieve relevant document chunks (`memory.retrieve` = a filtered SELECT)
3. Calls a function to generate the answer
4. Appends to an accumulator variable (conversation history)

The `EXCEPTION WHEN ContextLengthExceeded` block is the cursor loop's error handler — equivalent to catching `ORA-01555 (snapshot too old)` and refreshing the cursor.

The `memory.index_document` call is equivalent to building an index before querying a large table — you pay the indexing cost once, then retrieve cheaply per query.

<!-- --- -->

### Running It

```bash
# Chat over a PDF document
spl run chat_over_pdf.spl \
  --adapter ollama -m gemma3 \
  --tools pdf_tools.py memory_tools.py \
  --input pdf_path="./research_paper.pdf" \
  --input top_k_chunks=5
```

Expected session:

```
[pdf_to_md] Ingested 42 pages (18,400 words)
[index_document] Built retrieval index: 148 chunks

Ask a question (or type "quit" to exit): What is the main finding?
[extract_search_terms] Terms: main finding, conclusion, result, key result
[retrieve] 5 chunks retrieved (avg relevance: 0.84)
[answer_question] The paper's main finding is that...

Ask a question (or type "quit" to exit): How did they measure that?
[extract_search_terms] Terms: measurement method, metric, evaluation (resolved "that" → main finding)
[retrieve] 5 chunks retrieved (avg relevance: 0.79)
[answer_question] The measurement methodology described in Section 3...

Ask a question (or type "quit" to exit): quit
Session ended. 2 turns completed.
```

<!-- --- -->

### What Just Happened

1. The PDF was ingested with `tool.pdf_to_md` and chunked into 148 overlapping segments
2. On each turn, `extract_search_terms` resolved the question (including pronoun references) into retrieval terms
3. `memory.retrieve` fetched the 5 most relevant chunks — a tiny fraction of the full document
4. `answer_question` generated a grounded response from those chunks and the conversation history
5. The "How did they measure that?" follow-up resolved correctly because `extract_search_terms` used the history to resolve "that" before retrieval

The architecture ensures the model never sees more than `top_k_chunks × chunk_size` tokens of document context per question — typically 2,000–3,000 tokens, well within any model's comfortable working range.

<!-- --- -->

### Reproducibility Note

- **Hardware**: GTX 1080 Ti, 11 GB VRAM
- **Model**: Gemma 3 via Ollama
- **PDF**: 42-page research paper (18,400 words)
- **Ingestion latency**: 3–5 seconds (pymupdf; CPU-bound)
- **Indexing latency**: 8–12 seconds (embedding 148 chunks)
- **Per-question latency**: 12–18 seconds (search terms + retrieval + answer generation)
- **Context window consumption**: ~2,500 tokens per turn (context + history); grows slowly as history accumulates

<!-- --- -->

### When to Use This Pattern

**Use it when:**
- The document is too long for a single prompt (most real-world PDFs qualify)
- You need multi-turn conversation with follow-up resolution
- Precision is critical — you want answers grounded in document text, not model priors

**Use Recipe 5.1 (RAG Query) instead when:**
- You have a single question, not a conversation
- You are querying across many documents (Recipe 5.1's corpus indexing model scales better)

**Anti-patterns to avoid:**
- Ingesting the full PDF text into the prompt instead of using retrieval — works for short documents, fails for anything over ~10 pages
- Skipping the `extract_search_terms` step — direct embedding of the user question against the document works for simple questions but fails for pronoun references and multi-part follow-ups
- Forgetting the `ContextLengthExceeded` handler — long conversations will eventually hit the model's context limit; without the handler, the workflow crashes on turn N with no recovery

<!-- --- -->

### Exercises

1. Add a citation mode: modify `answer_question` to always include the document page number or section heading from which it sourced the answer. Modify `memory.retrieve` to return chunk metadata (page number, section).
2. Add multi-document support: accept a list of PDF paths as input and index all documents before the conversation begins. The retrieval step should label which document each chunk came from.
3. Implement conversation summarization proactively: instead of waiting for `ContextLengthExceeded`, summarize the history every 5 turns to keep the context window usage flat regardless of conversation length.
