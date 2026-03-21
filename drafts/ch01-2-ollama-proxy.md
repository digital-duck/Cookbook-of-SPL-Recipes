# Chapter 1.2 — Ollama Proxy

*"The simplest tool is often the most powerful when it becomes a building block."*

---

## The Pattern

In the previous chapter, we verified the "Hello World" of SPL: a hardcoded prompt that proves the connection between the runtime and the model. But real-world utility requires input. You don't just want the model to introduce itself; you want to ask it *your* questions.

The common way to interact with a local LLM is via a dedicated chat UI or a specific CLI tool like `ollama run`. These are great for interactive sessions, but they are hard to script or integrate into a larger pipeline. If you want to use the output of a model as a step in a bash script or a CI process, you often end up writing a wrapper script in Python or Node.js to handle the HTTP request, extract the text from the JSON response, and print it to stdout.

The SQL analogy is a parameterized query:

```sql
SELECT * FROM users WHERE user_id = ?;
```

You don't rewrite the query every time you want a different user; you pass the `user_id` as a parameter. The query structure remains constant, while the data varies.

The Ollama Proxy recipe is the SPL version of a parameterized query. It defines a reusable prompt structure that accepts a `prompt` argument from the command line, sends it to the model, and returns the result. It turns any LLM into a standard Unix-style utility.

---

## The Open-Source Engine Room: Ollama and Llama.cpp

Before we dive into the code, we must acknowledge the "engine room" that makes this recipe possible: **Ollama** and **Llama.cpp**.

In the proprietary AI world, models are locked behind APIs. You pay per token, you need a credit card, and you need a high-speed, uncensored connection to a data center in the Global North. For an engineer in Lagos, a student in rural Anhui, or a researcher in Recife, this is a barrier to entry that reproduces old inequalities.

**Llama.cpp** (and its user-friendly distribution, **Ollama**) changed the game. By optimizing LLM inference for consumer-grade hardware, they turned the "commodity hardware" in your closet—like a used **GTX 1080 Ti**—into a powerful AI workstation. These are not just technical achievements; they are tools of digital sovereignty.

In the Momagrid vision, these open-source foundations are the "orchestra" in our conductor metaphor. SPL 2.0 provides the "score" (the logic), but Ollama provides the "instruments" (the models). By advocating for open-source models (like Gemma, Llama, or Mistral) running on open-source runtimes, we ensure that AI remains a public utility accessible to everyone, everywhere, without a middleman.

When you run this recipe, you aren't just calling a model; you are exercising your right to run state-of-the-art intelligence on your own terms.

---

## The SPL Approach

The core idea is to use the `context` object to bridge the gap between the command line and the SPL runtime. By selecting `context.prompt`, we take a named argument passed at runtime and inject it into the LLM's context.

---

## The .spl File (Annotated)

```spl2
-- Recipe 02: Ollama Proxy
-- General-purpose LLM query — proxy any prompt to any adapter/model.
--
-- Usage:
--   spl2 run cookbook/02_ollama_proxy/proxy.spl prompt="Explain quantum computing"

PROMPT ollama_proxy                           -- (1) name the prompt block
SELECT
    system_role('You are a helpful, knowledgeable assistant.'),
                                             -- (2) establish the persona
    context.prompt AS prompt                 -- (3) bind the CLI parameter
GENERATE answer(prompt)                      -- (4) execute the query
```

### (1) `PROMPT ollama_proxy`

Like "Hello World," we use a `PROMPT` block because we only need a single LLM call. This is the "view" that we are executing.

### (2) `system_role(...)`

We define a general-purpose persona. Since this script is a proxy for any question, we want a model that is helpful and knowledgeable. This stays constant regardless of the input.

### (3) `context.prompt AS prompt`

This is the bridge. In SPL, the `context` object contains all parameters passed via the CLI (e.g., `key="value"`). By selecting `context.prompt`, we are telling SPL: "Look for a parameter named `prompt` in the environment and include its value in the context row."

The `AS prompt` alias is important. It gives the piece of context a label that we can refer to in the `GENERATE` step.

SQL Analogy:
```sql
SELECT :input_param AS user_query;
```
You are taking an external variable and bringing it into the scope of your query.

### (4) `GENERATE answer(prompt)`

We trigger the LLM call. Unlike Recipe 01, we now pass an argument to the step: `answer(prompt)`. This tells the runtime to specifically emphasize the `prompt` column from our `SELECT` statement as the primary instruction for the model.

---

## Running It

You can pass the `prompt` parameter as a key-value pair after the file path:

```bash
spl2 run cookbook/02_ollama_proxy/proxy.spl --adapter ollama -m gemma3 \
    prompt="Explain quantum computing in one sentence"
```

Expected output:
```output
Quantum computing uses the principles of subatomic physics to perform complex 
calculations that are currently impossible for traditional computers.
```

Because the adapter and model are specified at the CLI level, this single `.spl` file can be used to test any model in your Ollama library:

```bash
# Test with Llama 3.2
spl2 run cookbook/02_ollama_proxy/proxy.spl -m llama3.2 prompt="What is 2+2?"

# Test with Mistral
spl2 run cookbook/02_ollama_proxy/proxy.spl -m mistral prompt="Write a haiku about SPL"
```

---

## What Just Happened

**LLM calls: 1.**

The runtime performed the following steps:
1.  Parsed the command-line arguments and populated the `context` object with `prompt="Explain quantum computing..."`.
2.  Executed the `SELECT` clause, combining the `system_role` string and the `context.prompt` value into a single context row.
3.  Passed this row to the specified adapter/model.
4.  Captured the model's output and printed it to the console.

If you omit the `prompt=` argument, the runtime will throw an error because `context.prompt` is undefined. This is similar to a SQL error when a required bind variable is missing.

---

## Reproducibility Note

Since this is a proxy, its performance and stability depend entirely on the underlying model you choose. 

On a **GTX 1080 Ti**, running **gemma3**, you should expect:
- **Time to First Token (TTFT)**: ~200ms
- **Generation Speed**: ~40-60 tokens per second

The reproducibility of the *answer* depends on the prompt complexity. For factual questions ("What is 2+2?"), most models are 100% stable. For creative tasks, expect high variance unless you configure the adapter for `temperature=0`.

---

## When to Use This Pattern

Use the **Ollama Proxy** pattern when:
- **CLI Tooling**: You want to call an LLM from a shell script, e.g., `git commit -m "$(spl2 run proxy.spl prompt='Summarize these changes...')"`
- **Quick Model Testing**: You want to compare how different models handle the exact same prompt without writing any code.
- **Generic Utility**: You need a "swiss army knife" script that can handle any one-shot task.

Do not use this pattern when:
- **Structured Logic**: You need to validate the output or take different actions based on what the model says (use `EVALUATE` in a `WORKFLOW`).
- **Chain of Thought**: You need the model to "think" through steps before answering (use the patterns in Part 3).

---

## Exercises

1.  **Multiple Parameters**: Modify the `SELECT` clause to accept a second parameter `context.topic`. Update the `system_role` to say `'You are an expert in ' || context.topic`. Run it with `topic="Biology" prompt="What is a cell?"`.
2.  **Default Values**: (Advanced) Research how to use the `COALESCE` or `DEFAULT` equivalent in SPL to provide a fallback if `context.prompt` is missing.
3.  **Shell Integration**: Use the proxy in a bash pipe. For example:
```bash
echo "The weather is nice today" | xargs -I {} spl2 run proxy.spl prompt="Translate to French: {}"
```
