# Text2SPL Demo

<!-- *"The final barrier to programming is syntax; we are removing it." — Wen Gong* -->

<!-- --- -->

## The Pattern

For many, the biggest obstacle to using SPL 2.0 is the same obstacle they face with SQL: learning the keywords, the structure, and the punctuation. While SPL is designed to be readable, it still requires you to follow a "grammar." But what if you didn't have to? What if you could describe what you wanted in plain English and the system wrote the code for you?

This is the vision of **Text2SPL**. It is a "Compiler for Intent." Instead of writing a `.spl` file manually, you provide a natural language description—like "Summarize this document and then translate it into Chinese"—and the `spl` runtime generates the equivalent code.

The SQL analogy is **Natural Language to SQL (NL2SQL)**. Modern data platforms allow analysts to ask "What was the revenue in Q3?" and the system automatically generates the `SELECT ... FROM ... WHERE ...` query. Text2SPL brings this same "Zero-Barrier" experience to AI orchestration.

The Text2SPL Demo recipe (Recipe 22) showcases this capability. It demonstrates how to compile simple prompts, multi-step workflows, and even "Auto-Mode" agents from plain text.

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

## Exercises

1.  **Describe a "Self-Healer".** Try compiling the description: *"Generate a blog post, check it for facts, and if facts are missing, search the web and rewrite."* Use `--mode auto` and see if it generates a `WHILE` loop.
2.  **Fix and Re-run.** Take a generated `.spl` file that has a minor syntax error. Fix the error manually and run it. This is the "Human-in-the-loop" coding pattern.
3.  **Model Showdown.** Use two different compiler models (e.g., `phi4` vs `gemma3`) to compile the same description. Compare the "coding style" of each model.
