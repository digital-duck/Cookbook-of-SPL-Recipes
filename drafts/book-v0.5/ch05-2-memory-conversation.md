# Memory Conversation

<!-- *"The difference between a tool and a partner is memory." — Wen Gong* -->

<!-- --- -->

## The Pattern

Most LLM interactions are "stateless." The model doesn't remember who you are, what you said five minutes ago, or what your preferences are. Every time you start a new session, you have to re-explain everything — a frustrating Groundhog Day experience.

**Memory-Augmented Conversation** solves this by giving the model a long-term memory. Before each turn, the system loads facts about the user from a persistent store and injects them into the prompt. It also extracts *new* facts from the current turn and writes them back for next time.

The SQL analogy: a **User Profile Table**. Every request fetches the user's profile, personalizes the response, and writes any updates back. The difference here is that the profile is written in natural language — a concise bullet list — not a relational schema.

<!-- --- -->

## The SPL Approach

section 5.2 introduces two ideas that work together:

1. **`STORAGE`-typed INPUT** — memory is declared as a first-class workflow parameter, not a hidden global. The caller can override the path; the default is `~/.spl/memory.db`.
2. **Fact Extraction and Merging** — a two-step LLM pattern: first *identify* new facts in the user's message, then *merge* them into the existing profile. This keeps the profile clean and non-redundant.

<!-- --- -->

## The .spl File (Annotated)

```spl
-- Recipe 19: Memory-Augmented Conversation

-- Extract any personal facts the user shared. Return the exact string 'no_new_facts'
-- if nothing new was shared, otherwise return a bullet list of facts.
CREATE FUNCTION extract_facts(user_input TEXT) RETURNS TEXT
AS $$

You are a fact extractor. Read the user message and extract any personal facts they shared
about themselves (name, job, preferences, location, etc.).

If no personal facts are present, reply with exactly: no_new_facts
Otherwise reply with a concise bullet list, one fact per line, e.g.:
- Name: Alice
- Role: data scientist
- Preference: Python over R

User message: "{user_input}"
$$;

-- Merge new facts into an existing profile. Return the updated profile as a bullet list.
CREATE FUNCTION merge_profile(existing_profile TEXT, new_facts TEXT) RETURNS TEXT
AS $$

You are maintaining a user profile as a concise bullet list.
If the existing profile is empty or blank, start a new profile from the new facts only.
Otherwise merge the new facts in, keeping all prior facts unless directly contradicted.
Do NOT invent or assume any facts not explicitly stated.
Return ONLY the bullet list, no preamble.

Existing profile:
{existing_profile}

New facts to merge:
{new_facts}
$$;

-- Reply using full context: known profile + conversation history + current message.
CREATE FUNCTION contextual_reply(user_input TEXT, profile TEXT, history TEXT) RETURNS TEXT
AS $$

Known facts about the user: {profile}

Recent conversation:
{history}

Based solely on the known facts above, answer in one sentence: "{user_input}"
If the fact is not listed above, respond: "I don't have that in memory."
$$;

WORKFLOW memory_conversation
    INPUT:
        @user_input TEXT,
        @memory     STORAGE(sqlite, '~/.spl/memory.db')   -- (1) Memory as a parameter
    OUTPUT: @response TEXT
DO
    LOGGING f'Memory conversation | input: {@user_input}' LEVEL INFO

    -- Load existing user profile and chat history from the injected storage backend
    @profile      := @memory['chat_user_profile']          -- (2) Read from storage
    @chat_history := @memory['chat_history']

    -- Extract any new personal facts the user shared
    GENERATE extract_facts(@user_input) INTO @new_facts    -- (3) Fact extraction

    -- Update profile only when new facts were actually found (exact string check)
    EVALUATE @new_facts
        WHEN = 'no_new_facts' THEN
            LOGGING 'No new facts — profile unchanged' LEVEL DEBUG
        ELSE
            LOGGING 'New facts detected — merging profile' LEVEL DEBUG
            GENERATE merge_profile(@profile, @new_facts) INTO @profile  -- (4) Merge
            @memory['chat_user_profile'] := @profile       -- (5) Write back
    END

    -- Generate response with full context: profile + history + current input
    GENERATE contextual_reply(@user_input, @profile, @chat_history) INTO @response

    -- Persist updated chat history (keep last 10 turns, deterministic — no LLM cost)
    @chat_history := @chat_history || '\nUser: ' || @user_input || '\nAssistant: ' || @response
    CALL trim_turns(@chat_history, '10') INTO @chat_history  -- (6) Deterministic trim
    @memory['chat_history'] := @chat_history

    LOGGING 'Response ready' LEVEL INFO
    COMMIT @response WITH status = 'complete'

EXCEPTION
    WHEN BudgetExceeded THEN
        COMMIT 'I remember you! But I ran out of budget for this response.' WITH status = 'budget_limit'
END
```

### (1) Memory as a First-Class Parameter

```spl
@memory STORAGE(sqlite, '~/.spl/memory.db')
```

Memory is not a hidden global or a hardcoded path — it is a typed INPUT parameter. `STORAGE(sqlite, '~/.spl/memory.db')` is the default, aligned with the `~/.spl/` workspace that `spl init` creates. The caller can override it at run time:

```bash
# Use a different memory file for a specific project
spl run ... memory=~/projects/myapp/memory.db
```

This makes memory **portable and testable**. Point it at a fresh `.db` in CI, a shared file for a team, or a per-user path in a multi-tenant deployment — without changing a line of SPL.

### (2) Reading from Storage

```spl
@profile      := @memory['chat_user_profile']
@chat_history := @memory['chat_history']
```

`@memory['key']` dispatches to the storage backend's `get(key)` method. Returns an empty string if the key doesn't exist yet — no error, no null checks needed. On the first-ever run, both variables start empty and the workflow handles that gracefully.

### (3) Fact Extraction

The `extract_facts` function is the "listener." It reads the user's message and returns either `no_new_facts` (exact string) or a bullet list of newly shared information. The exact-string contract is the bridge between probabilistic LLM output and deterministic SPL branching — `EVALUATE ... WHEN = 'no_new_facts'` is a zero-token string comparison.

### (4) Profile Merging

`merge_profile` receives the *old* profile and the *new* facts and produces a single updated bullet list. The merge step prevents the profile from becoming a growing pile of sentences. It also handles contradictions — if the user says "I moved to Berlin" after previously saying "I live in Paris," the merged profile keeps only Berlin.

### (5) Writing Back to Storage

```spl
@memory['chat_user_profile'] := @profile
```

`@memory['key'] := value` dispatches to `set(key, value)`. The write happens only inside the `ELSE` branch — only when new facts were actually found. No unnecessary writes.

### (6) Deterministic History Trimming

```spl
CALL trim_turns(@chat_history, '10') INTO @chat_history
```

`trim_turns` is a **deterministic built-in** — it keeps the last 10 `User:/Assistant:` turn pairs by string manipulation. `CALL` costs zero tokens. Compare this to `GENERATE trim_history(...)` which would cost tokens on every single turn just to do string truncation. The SPL principle: *if you can write it as code, write it as code.*

<!-- --- -->

## Running It

```bash
# Turn 1: Introduce yourself
spl run cookbook/19_memory_conversation/memory_chat.spl --adapter ollama \
    user_input="My name is Alice and I am a data scientist"

# Turn 2: Test the memory
spl run cookbook/19_memory_conversation/memory_chat.spl --adapter ollama \
    user_input="Who is Alice"

# Turn 3: Unknown person — should say "I don't have that in memory"
spl run cookbook/19_memory_conversation/memory_chat.spl --adapter ollama \
    user_input="Who is Bob"
```

**Inspect and manage memory** with the `spl memory` commands:

```bash
spl memory list                          # Show all stored keys
spl memory get chat_user_profile         # Inspect the profile
spl memory delete chat_history           # Clear conversation history
spl memory delete chat_user_profile      # Reset the profile
```

<!-- --- -->

## What Just Happened

**LLM calls: 2 (no new facts) or 3 (new facts found).**

- Turn 1 ("My name is Alice"): 3 calls — extract (finds facts), merge, reply
- Turn 2 ("Who is Alice"): 2 calls — extract (no new facts, skips merge), reply

The `EVALUATE` branch eliminates the merge call when nothing new was shared. On a long-running assistant where most turns are questions rather than introductions, this saves a meaningful fraction of token spend.

**Zero-token operations:**
- `@memory['key']` reads (SQLite lookup)
- `@memory['key'] := value` writes (SQLite upsert)
- `CALL trim_turns(...)` (string manipulation)

The SPL runtime makes the efficient choice the natural choice.

<!-- --- -->

## The Prompt Design Lesson

The `contextual_reply` function took several iterations to get right. Early versions suffered from two failure modes:

1. **History poisoning** — if the model hallucinated an answer and it got saved to `@chat_history`, every subsequent turn reinforced the same hallucination (the model treated its own prior output as a factual source).

2. **Profile ignored** — rules like "if the answer is not in the profile, say I don't know" were applied by small models *even when the answer was in the profile*.

The final prompt resolves both by:
- Putting the known facts on the **very first line** — small models weight early context heavily
- Giving a single, concrete instruction: "answer from the known facts; if not listed, say so"
- Avoiding long rule lists that small models misapply

```spl
Known facts about the user: {profile}

Recent conversation:
{history}

Based solely on the known facts above, answer in one sentence: "{user_input}"
If the fact is not listed above, respond: "I don't have that in memory."
```

Minimal rules. Concrete instruction. Profile first.

<!-- --- -->

## Model Notes

Local models vary significantly in how reliably they follow the "answer only from provided facts" constraint:

| Model | Behavior |
|-------|----------|
| `phi4` | Follows the constraint reliably; tested and recommended |
| `gemma3` | Prone to using pre-trained knowledge even when instructed not to |
| `llama3.2`, `mistral` | Generally reliable; good alternatives to phi4 |

If you observe hallucinated answers, check whether the history has been poisoned by a prior wrong response. Reset with `spl memory delete chat_history` and retry.

<!-- --- -->

## When to Use This Pattern

Use the **Memory Conversation** pattern when:
- **Personal Assistants** — bots that help with scheduling, coding, or writing over long periods
- **Educational Tutors** — a bot that remembers which concepts a student has mastered and where they are struggling
- **Customer Support** — a bot that knows a user's purchase history without being told every time

<!-- --- -->

## Exercises

1. **Inspect the Memory.** After a few turns, run `spl memory get chat_user_profile` to see the raw profile the model has built. Notice how facts accumulate and merge across turns.

2. **Override the Storage Path.** Run the workflow with a project-specific memory file: `memory=~/myproject/memory.db`. Confirm that `spl memory list` is now empty (pointing at `~/.spl/memory.db` by default) while the project file has data.

3. **Add a "Mood" Memory.** Extend the workflow with a third memory key `chat_user_mood`. Add a `detect_mood` function that classifies the user's emotional tone and an `update_mood` branch (similar to profile merging) that persists it. Have `contextual_reply` adjust its tone based on the stored mood.

4. **Reset Logic.** Add a special-case branch: if `@user_input` equals `"forget everything"`, delete both memory keys and commit a "Memory cleared." response — without making any LLM calls.
