# Text2SPL Demo

<!-- *"The final barrier to programming is syntax; we are removing it." — Wen Gong* -->

<!-- --- -->

## The Pattern

For many, the biggest obstacle to using SPL 2.0 is the same obstacle they face with SQL: learning the keywords, the structure, and the punctuation. While SPL is designed to be readable, it still requires you to follow a "grammar." But what if you didn't have to? What if you could describe what you wanted in plain English and the system wrote the code for you?

This is the vision of **Text2SPL**. It is a "Compiler for Intent." Instead of writing a `.spl` file manually, you provide a natural language description—like "Summarize this document and then translate it into Chinese"—and the `spl` runtime generates the equivalent code.

The SQL analogy is **Natural Language to SQL (NL2SQL)**. Modern data platforms allow analysts to ask "What was the revenue in Q3?" and the system automatically generates the `SELECT ... FROM ... WHERE ...` query. Text2SPL brings this same "Zero-Barrier" experience to AI orchestration.

The Text2SPL Demo recipe (section 8.1) showcases this capability. It demonstrates how to compile simple prompts, multi-step workflows, and even "Auto-Mode" agents from plain text.

<!-- --- -->

## The SPL Approach

This chapter doesn't focus on a `.spl` file, but rather on the `text2spl` command built into the `spl` binary.

<!-- --- -->

## The Compilation Process (Annotated)

```bash
# Example 1: Compiling a simple PROMPT
spl text2spl "summarize a document with a 2000 token budget" \
    --mode prompt -o summarize.spl
```

When you run this command, the runtime:
1.  **Analyzes** your intent (summarization + budget constraint).
2.  **Identifies** the required SPL constructs (`PROMPT`, `SELECT`, `GENERATE`).
3.  **Synthesizes** a valid `.spl` file.
4.  **Validates** the syntax using the internal parser.

```bash
# Example 2: Compiling a multi-step WORKFLOW
spl text2spl "build a review agent that drafts, critiques, and refines text" \
    --mode workflow -o review_agent.spl
```

In "Workflow Mode," the compiler goes deeper. It creates a `WORKFLOW` block, defines multiple `GENERATE` steps, and sets up the variables to pass context between them. It may even define `CREATE FUNCTION` blocks for the different personas (the writer and the critic).

<!-- --- -->

## Running It

You can try the compiler demo yourself using the provided shell script:

```bash
bash cookbook/22_text2spl_demo/text2spl_demo.sh
```

This script will generate three different `.spl` files in the `generated/` directory based on increasingly complex descriptions. You can then run those files just like any other recipe:

```bash
# Execute the code generated from natural language
spl run generated/summarize.spl --adapter ollama text="Your document here..."
```

<!-- --- -->

## What Just Happened

**LLM calls: 1 (to compile).**

The "Conductor" (SPL Runtime) acted as a Software Engineer:
1.  **Interpreted** human requirements.
2.  **Transpiled** those requirements into a formal orchestration language.
3.  **Verified** the structural integrity of the generated code.
4.  **Delivered** a runnable asset.

This is the "North Star" of the Momagrid project: making the barrier to AI engineering effectively **Zero**.

<!-- --- -->

## Reproducibility Note

The reliability of Text2SPL depends on the **Compiler Model**. 
For simple prompts, small models like **gemma3** are 95%+ accurate. For complex workflows involving `WHILE` loops and `EXCEPTION` handling, we recommend using a "Senior" model like **Claude 3.5 Sonnet** as the compiler.

Once the code is compiled and validated, the **Execution** is perfectly deterministic. The "magic" only happens once at compile time; after that, you have a solid, version-controlled `.spl` file.

<!-- --- -->

## When to Use This Pattern

Use the **Text2SPL** pattern when:
- **Rapid Prototyping**: You have an idea for a workflow and want a "First Draft" of the code in seconds.
- **Onboarding**: You are new to SPL and want to see how the system would structure a specific task.
- **Dynamic Agents**: When your application needs to generate *new* workflows on the fly based on user requests.

<!-- --- -->

## A Live Session: The Intent Router

The following is not a constructed example. It is a real compilation run from a live development session on the SPL 2.0 Knowledge Studio.

The input was a single line:

```
classify user intent and route to the right handler
```

The compiler was Claude Sonnet 4.6 in `auto` mode. The generated script:

```spl
WORKFLOW intent_router
    INPUT @user_input TEXT, @context TEXT DEFAULT ''
    OUTPUT @handler_response TEXT
DO
    -- Step 1: Classify the user intent
    GENERATE classify(@user_input, intent_categories()) INTO @intent

    -- Step 2: Extract any entities or parameters needed by handlers
    GENERATE extract_entities(@user_input) INTO @entities

    -- Step 3: Route to the appropriate handler
    EVALUATE @intent
        WHEN 'question' THEN
            GENERATE answer(@user_input, @context, @entities) INTO @handler_response
            COMMIT @handler_response WITH handler = 'qa', intent = @intent

        WHEN 'command' THEN
            GENERATE execute_command(@user_input, @entities) INTO @handler_response
            COMMIT @handler_response WITH handler = 'command', intent = @intent

        WHEN 'complaint' THEN
            GENERATE handle_complaint(@user_input, @entities) INTO @handler_response
            COMMIT @handler_response WITH handler = 'complaint', intent = @intent

        WHEN 'chitchat' THEN
            GENERATE casual_reply(@user_input) INTO @handler_response
            COMMIT @handler_response WITH handler = 'chitchat', intent = @intent

        WHEN 'feedback' THEN
            GENERATE acknowledge_feedback(@user_input, @entities) INTO @handler_response
            COMMIT @handler_response WITH handler = 'feedback', intent = @intent

        OTHERWISE
            GENERATE fallback_response(@user_input, @intent) INTO @handler_response
            COMMIT @handler_response WITH handler = 'fallback', intent = @intent
    END

EXCEPTION
    WHEN HallucinationDetected THEN
        RETRY WITH temperature = 0.1
    WHEN RefusalToAnswer THEN
        GENERATE safe_fallback(@user_input) INTO @handler_response
        COMMIT @handler_response WITH handler = 'safe_fallback'
END;

CREATE FUNCTION intent_categories()
RETURNS TEXT AS $$
Supported intent categories:
- question:   user is asking for information or clarification
- command:    user is requesting an action to be performed
- complaint:  user is expressing dissatisfaction or reporting a problem
- chitchat:   casual or social conversation with no specific goal
- feedback:   user is providing a review, rating, or suggestion
- unknown:    intent cannot be determined with confidence
$$;
```

This was compiled from eleven words. The compiler inferred:

- A three-step pipeline: classify, extract entities, then route
- Six intent categories — including an `unknown` fallback
- Per-handler `COMMIT` statements that tag the output with handler metadata
- `EXCEPTION` handling for `HallucinationDetected` and `RefusalToAnswer` — AI-specific failure modes the compiler invented on its own
- A `CREATE FUNCTION intent_categories()` that injects domain knowledge as structured system context

The script was then run against Gemma3 (local, via Ollama) with the input:

```
The app keeps crashing every time I try to upload a file, this is really frustrating
```

Gemma3 correctly routed it to the `complaint` handler, called `handle_complaint`, and produced a structured troubleshooting response. The full round-trip — compile on Claude, execute on Gemma3 — worked without modification.

<!-- --- -->

## The Bootstrap Insight

The intent router is not production-ready. The intent categories are generic. The handler logic is shallow. A real deployment would need domain-specific categories, tighter prompts, and validation of the routing decisions.

But that is exactly the point.

*"It may not be useful out-of-the-box, but it bootstraps the further iteration and refinement process. One can try various LLM models, add new logic — this is why declarative programming is so powerful."* — Wen Gong

This is the correct frame for Text2SPL. The compiled script is not the destination. It is a **scaffold** — a structured starting point that encodes the compiler's best interpretation of your intent. From there, the developer's job shifts from writing code to refining a spec.

The iteration loop looks like this:

```
describe → compile → inspect → refine → iterate
```

Compare it to the imperative alternative:

```
design → code → debug → refactor → re-debug → iterate
```

In the imperative loop, every iteration requires touching implementation details: which API, which prompt format, which response accessor, which retry logic. In the SPL loop, every iteration is a conversation about intent. You change what the workflow does, not how it talks to a model.

The bootstrapped script also encodes structural knowledge that survives iteration. The compiler inferred that a complaint handler needs different logic than a chitchat handler. It inferred that entity extraction should precede routing so that handlers have structured input to work with. It inferred that AI workflows need typed exception handling. These are good decisions. They do not get thrown away when you refine the domain vocabulary. They become the scaffold on which the domain-specific version is built.

**The script is the spec.** `EVALUATE @intent WHEN 'complaint'` reads like a requirements document. When a product manager says "add a `billing` intent," you know exactly where to add one line — no hunting through callback chains, prompt templates, or routing middleware.

**The model is configurable.** The same script ran on Claude during compilation and Gemma3 during execution. Tomorrow you can point the runtime at GPT-4o or Mistral for a quality comparison, with zero code changes. The adapter is runtime config, not source code.

**The version history is free.** The Knowledge Studio saved this as `intent_router v1`. When you refine the `intent_categories()` function or add a `billing` handler, that becomes `v2` — a natural experiment log with no extra tooling required.

This is the same reason SQL outlasted every "better" imperative data access approach. The abstraction is at the right level. SPL 2.0 is that abstraction for agentic workflows. The models are the orchestra. SPL is the score. The score says what to play. Text2SPL gives you a first draft of the score from a description of the music you want to hear.

<!-- --- -->

## Exercises

1.  **Describe a "Self-Healer".** Try compiling the description: *"Generate a blog post, check it for facts, and if facts are missing, search the web and rewrite."* Use `--mode auto` and see if it generates a `WHILE` loop.
2.  **Fix and Re-run.** Take a generated `.spl` file that has a minor syntax error. Fix the error manually and run it. This is the "Human-in-the-loop" coding pattern.
3.  **Model Showdown.** Use two different compiler models (e.g., `phi4` vs `gemma3`) to compile the same description. Compare the "coding style" of each model.

<!-- --- -->

## Want a Visual Interface?

The CLI compiler is powerful, but if you prefer working in a browser, the **Recipe Kitchen** (Chapter 11.2) provides a full web UI for Text2SPL. You can describe a workflow in plain English, compile it, inspect the generated SPL, and run it — all from a browser tab, no terminal required. The Recipe Kitchen is SPL's answer to "low-code": the same declarative language, with a graphical front door.
