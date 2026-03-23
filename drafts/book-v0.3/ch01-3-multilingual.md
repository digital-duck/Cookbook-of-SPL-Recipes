# Multilingual Greeting

<!-- *"Language is the first barrier to knowledge; code should be the first bridge." — Wen Gong* -->

<!-- --- -->

## The Pattern

In a truly global AI ecosystem, assuming the user speaks English is a design flaw. Whether you are building a support bot for a marketplace in Southeast Asia or a localized tutor for a school in West Africa, the ability to pivot between languages dynamically is a core requirement.

The naive way to handle multilingual prompts is often to hardcode multiple prompts or use complex string interpolation in a programming language. You end up with a "prompt library" that is difficult to maintain and even harder to test across different models.

The SQL analogy is a multi-parameter join:

```sql
SELECT t.translation 
FROM dictionary d 
JOIN translations t ON d.id = t.id 
WHERE d.word = ? AND t.language = ?;
```

You have the "intent" (the word) and the "constraint" (the language). By providing both, you get the specific result you need.

The Multilingual Greeting recipe takes this principle and applies it to a prompt. It accepts two parameters—`user_input` and `lang`—and uses them to constrain the model's response. It's a simple demonstration of how SPL can manage multi-dimensional context without the "spaghetti code" of imperative string formatting.

<!-- --- -->

## The SPL Approach

We use the `context` object to capture multiple CLI arguments and then "bind" them to semantic labels in our `SELECT` clause. This allows us to pass structured, multi-part instructions to the `GENERATE` step.

<!-- --- -->

## The .spl File (Annotated)

```spl
-- Recipe 03: Multilingual Greeting
-- Greet in any language — demonstrates parametric context with lang.
--
-- Usage:
--   spl run cookbook/03_multilingual/multilingual.spl user_input="hello" lang="Chinese"

PROMPT multilingual_greeting                  -- (1) name the prompt block
SELECT
    system_role('You are a friendly assistant. Respond in the language specified.'),
                                             -- (2) system-level constraint
    context.user_input AS input,             -- (3) the user's message
    context.lang AS lang                     -- (4) the target language
GENERATE greeting(input, lang)               -- (5) context-aware generation
```

### (1) `PROMPT multilingual_greeting`

A single model call. The complexity is in the input, not the execution flow.

### (2) `system_role(...)`

This establishes the "rules of the game." We tell the model to be friendly and, crucially, to respect the language specification provided in the context.

### (3) & (4) `context.user_input AS input` and `context.lang AS lang`

This is where we "map" our command-line parameters into our query scope. By giving them clean aliases (`input`, `lang`), we make our `GENERATE` step more readable.

In SPL, every column in your `SELECT` clause becomes a piece of evidence for the model. By labeling them explicitly, you are giving the model a structured view of the world: "Here is the input, and here is the language constraint."

### (5) `GENERATE greeting(input, lang)`

We pass both aliases as arguments to the `GENERATE` step. This tells the model: "Produce a greeting by considering both the input message and the language requirement."

<!-- --- -->

## Running It

Test it with different languages:

```bash
# To Chinese
spl run cookbook/03_multilingual/multilingual.spl user_input="hello wen" lang="Chinese"

# To French
spl run cookbook/03_multilingual/multilingual.spl user_input="hello wen" lang="French"

# To Spanish
spl run cookbook/03_multilingual/multilingual.spl user_input="hello wen" lang="Spanish"
```

Expected output (for Chinese):
```output
你好，文！很高兴见到你。我是你的助手。
(Hello, Wen! Nice to see you. I am your assistant.)
```

<!-- --- -->

## What Just Happened

**LLM calls: 1.**

The runtime combined the `system_role`, the `input`, and the `lang` into a single prompt package. Because we are using an open-source model like **gemma3** via **Ollama**, the model's native multilingual capabilities are triggered.

Modern open-weights models are trained on vast, multi-lingual datasets. By explicitly naming the language in the prompt, you are activating the specific language weights within the model's neural network.

<!-- --- -->

## Reproducibility Note

The stability of this recipe varies based on the "popularity" of the language in the model's training set. 
- **High Stability**: English, Chinese, Spanish, French, German.
- **Moderate Stability**: Hindi, Japanese, Portuguese.
- **Lower Stability**: Low-resource languages (e.g., local dialects).

On a **GTX 1080 Ti**, the latency for a short greeting remains consistent at **2-5 seconds** regardless of the language, as the model's internal processing time is more dependent on the number of tokens generated than the specific language family.

<!-- --- -->

## When to Use This Pattern

Use the **Multilingual** pattern when:
- **Global Reach**: You need to serve users in their native tongue without duplicating your logic.
- **Dynamic Formatting**: You want to change the "style" or "format" of the output based on a parameter (e.g., `lang="pirate"`, `lang="formal"`, `lang="bullet points"`).
- **Context Injection**: You have more than one variable piece of data to feed into the model.

<!-- --- -->

## Exercises

1.  **Add a "Tone" parameter.** Modify the `SELECT` to accept `context.tone` and update the `system_role` to include it. Run with `lang="Chinese" tone="extremely excited"` and then `tone="very bored"`.
2.  **Combine with Translation.** Instead of just a greeting, change the prompt to be a "Translator." Set the `system_role` to `'You are a translator.'` and the `GENERATE` step to `translate(input, lang)`.
3.  **Regional Dialects.** Try specific dialects like `lang="Brazilian Portuguese"` vs. `lang="European Portuguese"`. See if your local model can tell the difference!
