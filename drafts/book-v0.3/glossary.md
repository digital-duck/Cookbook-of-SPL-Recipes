# Glossary

*Key terms used throughout this book, in alphabetical order.*

<!-- --- -->

**Adapter**
The component of the SPL runtime that translates a workflow's declarative instructions into API calls for a specific LLM provider or infrastructure backend. Adapters handle authentication, prompt formatting, response parsing, and error mapping — so the `.spl` file does not have to. Built-in adapters include `ollama`, `openrouter`, `claude_cli`, `gemini`, and `momagrid`. Swapped with `--adapter` at the command line.

**Agent / Agentic Workflow**
A workflow in which one or more LLM calls make decisions that affect subsequent steps — routing logic, loop termination, planning — rather than simply producing output. An agentic workflow *acts* on intermediate results, not just generates them.

**CALL**
The SPL statement for invoking a deterministic Python function registered with the `@spl_tool` decorator. `CALL` is zero-token, machine-speed, and perfectly reproducible. It should be used for everything a Python function can do: parsing, arithmetic, file I/O, API lookups, string manipulation. See also: `GENERATE`.

**Commit / COMMIT**
The SPL statement that finalizes workflow output and writes it to the result. A `WORKFLOW` must end with a `COMMIT` on every execution path. The committed value becomes the workflow's observable output.

**Context Window**
The maximum number of tokens an LLM can process in a single call — inputs plus output combined. SPL workflows that accumulate large intermediate results in variables (especially inside `WHILE` loops) can exhaust the context window. The correct pattern is to pass lightweight summaries between steps, not raw accumulated output.

**CREATE FUNCTION**
The SPL statement for defining a named prompt template that can be injected as system context into a `GENERATE` call. Analogous to a SQL user-defined function (UDF). A `CREATE FUNCTION` body contains free-form prompt text with `{parameter}` substitution slots; it is injected as the system role instruction when the function is called in a `GENERATE` statement.

**Declarative Programming**
A style of programming in which you describe *what* you want rather than *how* to produce it. SQL is the canonical example: you specify the desired result set, and the query optimizer decides how to retrieve it. SPL applies this principle to LLM workflows: you specify the intent of each step, and the runtime (adapter) handles provider-specific execution details.

**EVALUATE**
The SPL statement for branching workflow execution based on the content of an LLM-generated value. Analogous to a semantic `WHERE` or `CASE` clause. Unlike a deterministic conditional (`IF value == 'x'`), `EVALUATE` matches against language model output, which means the branch taken is probabilistic — the same input may route differently across runs. This is expected behavior for semantic branching.

**EXCEPTION**
The SPL block that handles runtime errors and failure modes. Analogous to `BEGIN...EXCEPTION...END` in PL/SQL. Named exception types (e.g., `GenerationError`, `MaxIterationsReached`, `BudgetExceeded`) allow the workflow to handle different failures differently — graceful degradation, partial commit, early termination — without crashing the entire workflow.

**The AI Quartet**
The four-member research team that produced this book: Wen Gong (human author and architect), Claude (Anthropic), Gemini (Google), and Z.ai (ZhiPu). Each brought a distinct perspective: Wen's architectural vision and lived experience, Claude's technical precision, Gemini's editorial breadth, and Z.ai's adversarial critical review.

**GENERATE**
The SPL statement for invoking an LLM. `GENERATE` costs tokens, takes time, and is probabilistic — the same input will produce slightly different output across runs. It should be reserved for steps that genuinely require language understanding, reasoning, or generation. For everything code can do, use `CALL` instead.

**GTX 1080 Ti**
The reference hardware used for all benchmarks in this book — an NVIDIA graphics card from 2017 with 11 GB VRAM, available on the secondhand market for under $200. Its use is deliberate: it represents the floor of what is achievable on commodity hardware, and it is the GPU a student in the Global South might realistically own or afford.

**Hallucination**
An LLM's generation of plausible-sounding but factually incorrect content. SPL does not eliminate hallucination, but it provides tools to detect and handle it: `EVALUATE` for semantic checking, `EXCEPTION WHEN HallucinationDetected`, and the CALL/GENERATE split that keeps deterministic facts in Python functions rather than asking the LLM to produce them.

**Imperative Programming**
A style of programming in which you specify *how* to produce a result, step by step. Python, Java, and most general-purpose programming languages are imperative. LLM framework code (LangChain, AutoGen, CrewAI) is typically imperative: you write the loop, the state machine, the API calls, the error handling. Contrast with *declarative programming*.

**LLM (Large Language Model)**
A neural network trained on large text corpora that can generate, classify, summarize, translate, and reason about text. In SPL, LLMs are invoked exclusively through `GENERATE` statements. They are the "orchestra" — the models are the musicians, SPL is the score, and the human is the conductor.

**Model**
The specific LLM variant invoked by a `GENERATE` step. Specified with `--model` or `-m` at the CLI, or with `USING MODEL @var` inside a workflow. Different models have different capability, cost, and latency profiles. The workflow does not change when the model changes.

**Momagrid**
A decentralized inference network where GPU nodes contributed by independent operators (students, hobbyists, cooperatives, universities) form a shared compute grid. Anyone with a GPU can contribute inference capacity; anyone with an SPL workflow can run it against the grid. Accessed via `--adapter momagrid`. Part of the full SPL + Momagrid stack for democratic AI access.

**Ollama**
An open-source tool for running LLMs locally on your own hardware, without API keys or cloud accounts. The default development adapter in this book (`--adapter ollama`). Used with locally pulled models like Gemma 3, Phi-4, Llama 3.2, Mistral, and Qwen.

**OpenRouter**
A cloud API gateway that provides access to a wide range of LLMs (OpenAI, Anthropic, Meta, Mistral, and others) through a single API endpoint. Accessed via `--adapter openrouter`.

**Part**
A grouping of related chapters in this book, organized by theme: Foundations, Basics, Agentic Patterns, Reasoning, Safety & Reliability, Memory & Retrieval, Multi-Agent Systems, Applications, Benchmarking & Evaluation, and The Road Ahead. Each Part corresponds to a section divider in the printed book.

**PROCEDURE**
A named, reusable SPL sub-workflow that can be CALLed from within another workflow. Analogous to a SQL stored procedure. Enables modular composition of complex workflows from smaller, independently testable units.

**PROMPT**
The SPL statement for a single, stateless LLM interaction — no workflow state, no loop, no COMMIT. A `PROMPT` block defines a template and executes it in one shot. Used for simple, single-step generation tasks where a full `WORKFLOW` would be over-engineering.

**Recipe**
A self-contained unit in this book: a specific pattern, demonstrated with a complete `.spl` file, annotated line by line, with sample data, a `tools.py` for deterministic operations, and a `readme.md` with usage instructions. Designed so you can open any recipe and run it independently.

**SELECT**
The SPL statement for assembling the context that flows into a `GENERATE` call — the variables, computed values, and system roles that form the LLM prompt. Analogous to the `SELECT` clause in SQL: you specify what you want to surface, and the adapter handles how to package it for the specific model being called.

**SPL (Structured Prompt Language)**
The declarative language this book teaches. SPL 2.0 extends SPL 1.0's context management primitives (`PROMPT`, `SELECT`, `GENERATE`) with agentic orchestration features (`WORKFLOW`, `EVALUATE`, `WHILE`, `EXCEPTION`, `PROCEDURE`). The language is model-agnostic and adapter-portable: the same `.spl` file runs against any supported backend.

**spl-llm**
The Python package that provides the `spl` command-line tool. Installed with `pip install spl-llm`. Provides the runtime that parses `.spl` files, resolves adapters, manages workflow state, and executes `CALL` and `GENERATE` steps.

**@spl_tool**
The Python decorator that registers a Python function as a `CALL`-able tool in an SPL workflow. Functions decorated with `@spl_tool` must accept string parameters and return strings. They are loaded at workflow invocation time with `--tools path/to/tools.py`.

**WHILE**
The SPL looping construct for iterating a block of steps as long as a condition holds. Used for retry loops, multi-round patterns (debate, refinement), and step-by-step execution over a plan. The loop body should be lightweight: decide or route, not generate large artifacts. Heavy generation belongs outside loops.

**WORKFLOW**
The SPL construct for a named, parameterized, multi-step agentic process. Analogous to a SQL stored procedure. Defines `INPUT` parameters (with optional defaults), an `OUTPUT` variable, a `DO` body (the steps), and an `EXCEPTION` block (error handling). The primary unit of composition in SPL 2.0.

<!-- --- -->

*Terms in italics within definitions are themselves defined in this glossary.*
