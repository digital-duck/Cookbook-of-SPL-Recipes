# Memory Conversation

<!-- *"The difference between a tool and a partner is memory." — Wen Gong* -->

<!-- --- -->

## The Pattern

Most LLM interactions are "stateless." The model doesn't remember who you are, what you said five minutes ago, or what your preferences are. Every time you start a new session, you have to re-explain everything. This makes for a very frustrating "Groundhog Day" experience for the user.

**Memory-Augmented Conversation** solves this by providing the model with a "Long-Term Memory." Before each turn, the system looks up facts about the user from a persistent database and injects them into the prompt. It also extracts *new* facts from the current turn to update that memory for the future.

The SQL analogy is a **User Profile Table** or a **Session Store**. Every time a user visits your website, you fetch their `user_id` from a cookie and join it with a `profiles` table to personalize their experience.

The Memory Conversation recipe (Recipe 19) implements this "Persistent Persona" pattern. It uses the `memory.get` function to fetch a user profile, uses an LLM to merge new facts into that profile, and then generates a response that is aware of the user's history and preferences.

<!-- --- -->

## The SPL Approach

This recipe introduces the `memory` namespace and the pattern of "Fact Extraction and Merging."

<!-- --- -->

## The .spl File (Annotated)

```spl
-- Recipe 19: Memory-Augmented Conversation
-- Conversational agent that remembers facts from prior turns.

WORKFLOW memory_conversation
    INPUT: @user_input TEXT
DO
    -- Phase 1: Retrieval (Remembering)
    SELECT memory.get('chat_user_profile') AS profile INTO @profile -- (1) The Long-Term Memory
    SELECT memory.get('chat_history') AS history INTO @history

    -- Phase 2: Fact Extraction (Learning)
    GENERATE extract_facts(@user_input) INTO @new_facts -- (2) Identifying new info

    EVALUATE @new_facts
        WHEN 'no_new_facts' THEN -- do nothing
        ELSE
            GENERATE merge_profile(@profile, @new_facts) INTO @profile -- (3) Updating the state
    END

    -- Phase 3: Contextual Response
    GENERATE contextual_reply(@user_input, @profile, @history) INTO @response

    -- Update history (Short-term context)
    @history := @history + '\nUser: ' + @user_input + '\nAI: ' + @response
    GENERATE trim_history(@history, 10) INTO @history

    COMMIT @response WITH status = 'complete'
END
```

### (1) Phase 1: Retrieval (`memory.get`)

We start by querying the built-in SPL memory store (a local SQLite database). We fetch two things:
- **`chat_user_profile`**: A summary of what we know about the user (e.g., "Name: Alice, Role: Data Scientist").
- **`chat_history`**: The last few turns of the conversation to maintain flow.

SQL Analogy: **SELECT FROM session_state**. You are pulling the existing context for this specific user.

### (2) Phase 2: Fact Extraction

Instead of just replying, we ask the model to "listen" for new information. If the user says "I prefer Python over R," the model identifies this as a new fact and produces `@new_facts`.

### (3) Updating the State (`merge_profile`)

We take the *old* profile and the *new* facts and ask the model to merge them into a single, updated profile. This prevents the memory from becoming a disorganized list of sentences; it becomes a structured, evolving "biography" of the user.

<!-- --- -->

## Running It

Run the conversation over multiple turns. Notice how the model "learns" as you go:

```bash
# Turn 1: Introduce yourself
spl run cookbook/19_memory_conversation/memory_chat.spl \
    user_input="My name is Alice and I'm a data scientist"

# Turn 2: Test the memory
spl run cookbook/19_memory_conversation/memory_chat.spl \
    user_input="What is my name and what do I do?"
```

<!-- --- -->

## What Just Happened

**LLM calls: 3.** (Extract, Merge, Reply)
**Memory calls: 2.** (Get profile, Get history)

The "Conductor" (SPL Runtime) managed a "Persistent Identity":
1.  **Recalled** the user's past.
2.  **Observed** new details in the current input.
3.  **Synthesized** the new and old information into an updated world-view.
4.  **Responded** with a "personalized" voice.

<!-- --- -->

## Reproducibility Note

The reliability of memory depends on the **Extraction Quality**. If your model is too small, it might miss subtle facts or misinterpret them. We recommend using a model with high "Information Density" (like **gemma3**) for the `merge_profile` step to ensure the memory remains clean and accurate.

On a **GTX 1080 Ti**, the memory lookup adds **zero** noticeable latency (it's a local SQLite query), but the extra LLM calls for extraction and merging add about **10–15 seconds** per turn.

<!-- --- -->

## When to Use This Pattern

Use the **Memory Conversation** pattern when:
- **Personal Assistants**: Bots that help with scheduling, coding, or writing over long periods.
- **Educational Tutors**: A bot that remembers which concepts a student has already mastered and where they are struggling.
- **Customer Support**: A bot that knows a user's purchase history or past complaints without being told every time.

<!-- --- -->

## Exercises

1.  **Inspect the Memory.** Use the command line `spl memory get chat_user_profile` to see the raw text the model has stored about you.
2.  **Add a "Mood" Memory.** Modify the workflow to track the user's emotional state over time (e.g., "Frustrated," "Curious") and adjust the `@response` tone accordingly.
3.  **Reset Logic.** Add a special input command (e.g., `user_input="Forget everything"`) that triggers a `memory.delete` call to wipe the profile and start over.
