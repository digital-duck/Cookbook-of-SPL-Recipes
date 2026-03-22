# The Road Ahead: Declarative AI, Momagrid, and Where SPL Fits

<!-- *"Every tool that survives its first decade does so by becoming infrastructure. The question is not whether SPL will be used — it is whether what it enables will be distributed equitably." — Wen Gong* -->

<!-- --- -->

## What 37 Recipes Taught Us

You have reached Part 9 of this book having built, or at least read, 37 working recipes. Before the final recipe — the recipe-maker — it is worth pausing to ask: what does the arc of those 37 patterns tell us about where agentic AI is going, and what role a declarative language like SPL plays in that future?

The recipes started simple. A Hello World. A multilingual greeting. A few-shot classifier. Then the patterns grew richer: self-refining loops, ReAct agents, plan-and-execute workflows, multi-agent debates. By the time you reached the map-reduce summarizer and the ensemble voter, you had covered the entire space of what the current agentic AI literature calls "compound AI systems" — systems where multiple LLM calls, deterministic tools, and routing logic combine to produce results no single call could achieve.

What the recipes collectively demonstrate is a thesis that was stated in the Preface and has now been tested 37 times: **the logic of these workflows is expressible declaratively**, and expressing it declaratively makes it readable, portable, and maintainable in a way that imperative Python implementations are not.

The thesis holds. Not because the book says so, but because the `.spl` files exist and run.

<!-- --- -->

## Three Problems That Remain Open

Building 37 working recipes also clarifies what SPL does not yet solve. Three problems remain genuinely open.

### 1. Dynamic workflows

Every recipe in this book has a structure determined at design time: a fixed number of steps, a fixed set of branches, a fixed loop bound. Real-world agentic systems sometimes need workflows whose structure is itself a product of reasoning — a planner that decides not just *what* to do but *how many* steps to take and *which* tools to use, at runtime, based on intermediate results.

SPL's `WHILE` and `EVALUATE` give you runtime branching within a fixed structure. They do not give you fully dynamic workflow generation — a workflow that writes its own next step. The recipe-maker (Chapter 9.2) is a partial answer: it generates a new `.spl` file from a concept description, which can then be executed. But the two-step process — generate, then run — is not the same as a workflow that reasons about and modifies its own execution while running.

This is an active research problem. SPL v3 will address it. The current architecture's constraint — that the workflow structure is parsed and validated before execution begins — is a deliberate trade-off: it makes workflows human-reviewable, because the reviewer sees the complete structure before it runs. Fully dynamic workflows sacrifice that property. The right answer depends on the use case.

### 2. Long-running and stateful workflows

Every recipe in this book runs to completion in a single invocation. The session ends; the state is gone. For short workflows this is fine. For workflows that run for hours, survive machine restarts, or maintain state across multiple user interactions over days — the pattern breaks down.

`SPL 2.0` provides no native persistence layer. The workflow's variables live in memory; when the process ends, they are lost. Practical production deployments work around this by checkpointing intermediate state to a database or file system using `CALL write_checkpoint(...)` tools, and resuming from the checkpoint on restart. This works but is manual and recipe-specific.

`SPL v3` will address this with a native `CHECKPOINT` primitive and a workflow execution engine that can suspend and resume across process boundaries. The design is informed by the 37 recipes in this book: most of the checkpoint patterns that emerged naturally in complex recipes will become first-class language features.

### 3. Multi-tenant and multi-user workflows

Every recipe in this book is single-user: one person, one workflow, one output. Multi-tenant systems — where many users run the same workflow with their own data, credentials, and isolation requirements — require infrastructure that the current SPL runtime does not provide. This is not a language problem; it is a deployment problem. But it is a real barrier to production use at scale.

Momagrid's architecture addresses this directly: each workflow execution is isolated to a node, credentials are never included in the `.spl` file, and the adapter layer handles authentication at the node level. The Momagrid deployment model is inherently multi-tenant by design. As the network grows, this becomes the recommended production deployment model for SPL workflows at scale.

<!-- --- -->

## The Momagrid Vision: Status and Timeline

Momagrid is not a future promise. It is operational today on modest hardware.

The current network consists of independently operated GPU nodes running the Momagrid adapter, connected through a lightweight coordination layer. A workflow submitted to the grid is matched to an available node with sufficient VRAM for the requested model, executed in isolation, and the result returned to the submitter. The submitter never knows which node ran their workflow, and the node operator never sees the submitter's data — the protocol is designed for mutual opacity.

What the network needs to fulfill the democratic AI vision is scale: more nodes, more geographic diversity, more operator-owned hardware in the regions where cloud AI is expensive or unavailable. A student in Hefei with a GTX 1080 Ti can contribute a node today. A researcher in Nairobi with a used gaming PC can do the same. The coordination layer handles discovery, matching, and result routing. The operator sets their availability and model catalog; the grid does the rest.

Three things are needed to reach the critical scale where Momagrid becomes a meaningful alternative to cloud APIs:

1. **More recipes** — more `.spl` workflows that demonstrate what can be run on commodity hardware. This book is the first layer of that catalog.
2. **More node operators** — people and institutions willing to contribute inference capacity to the grid. The GTX 1080 Ti benchmark is the floor; any GPU above it can participate.
3. **More adapter integrations** — connections between the Momagrid grid and the tools people already use: databases, document stores, web search, enterprise APIs.

The recipe-maker in Chapter 9.2 is the mechanism for the first need. The second and third are community problems. If you have built something with SPL that you want to contribute to the catalog, or if you want to operate a Momagrid node, the project is open.

<!-- --- -->

## What SPL Is Not Trying to Be

Clarity about what SPL does not aim to replace is as important as understanding what it does.

**SPL is not trying to replace Python.** Python is the right tool for imperative logic, dynamic workflows, and anything that requires a full programming language's expressiveness. SPL calls Python functions through `CALL`. The two languages are complementary, not competing.

**SPL is not trying to replace LangChain, AutoGen, or CrewAI.** Those frameworks serve use cases that require dynamic agent construction, complex memory systems, and tight integration with specific enterprise platforms. If your system needs those capabilities, those frameworks are the right choice.

**SPL is not trying to be a research language.** It is a production tool. The design choices — human-reviewable syntax, adapter portability, the CALL/GENERATE split, explicit exception handling — are all oriented toward systems that real engineers maintain over time, not experiments that run once.

What SPL is trying to be: the simplest possible language for expressing the canonical agentic workflow patterns in a form that a SQL practitioner can read, a business stakeholder can review, and a system administrator can deploy portably across environments. That is a well-defined, non-trivial problem. The 37 recipes in this book are evidence that it is solvable.

<!-- --- -->

## On Adoption: An Honest Assessment

A reader who has reached this chapter has invested time in learning a language that is not yet widely adopted. That investment deserves a direct answer to the question the book has been avoiding.

**SPL is not a mainstream tool.** It is an open-source project with a small but growing user base, a published runtime, and a production-tested recipe catalog. It is not backed by a foundation or a large enterprise. It does not have a Stack Overflow tag with ten thousand questions. If your team evaluates SPL and asks "who else is using this?" — the honest answer is: early adopters, researchers, and practitioners who prioritized declarativeness over ecosystem size.

This is a real risk. A language that does not reach critical adoption becomes a maintenance liability. The roadmap items above — Momagrid scale, SPL v3, the specialty SPL model — are not decoration. They are the work required to build the ecosystem that makes the adoption risk acceptable.

Here is where the project stands:

| Milestone | Status |
|-----------|--------|
| SPL 2.0 runtime published | Complete |
| 37-recipe cookbook | Complete |
| Momagrid adapter live | Complete |
| Parser fixes for recipes 13, 14, 19 | In progress |
| `PARALLEL DO` for concurrent execution | Planned |
| Native `CHECKPOINT` for long-running workflows | Planned (v3) |
| Code-RAG for Text2SPL | Deferred — awaiting spec stability |
| Specialty SPL model (Qwen-Coder fine-tuned) | Deferred — awaiting training corpus |

**If your team evaluates SPL and decides it is not the right choice**, here is what you take away regardless: the CALL/GENERATE discipline (separating deterministic operations from probabilistic ones), the habit of writing workflows as declarative artifacts reviewable by non-engineers, and the pattern library in this book. Every one of these transfers to LangGraph, AutoGen, or CrewAI. The mental model is portable even when the syntax is not.

<!-- --- -->

## What Comes Next for You

You have 37 recipes. You have the recipe-maker. You have the adapter abstraction that lets you develop locally and deploy to the grid without changing your workflow.

The next step is yours to choose:

**If you are a SQL practitioner** building your first agentic system: pick the recipe closest to your use case, run it, read the annotated `.spl`, and modify it for your data. The pattern is the scaffold. Your domain knowledge is the dish.

**If you are in the Global South** with commodity hardware: set up Ollama, install `spl-llm`, and run Recipe 1.1. The stack runs on a GTX 1080 Ti. If that is more than you have, try Recipe 1.1 with a smaller model. The barrier to entry is a `pip install`, not a credit card.

**If you are an engineering leader** evaluating orchestration tools: the SPL repository contains all 37 recipes, the full runtime, and the benchmark data. The LOC comparison to equivalent LangGraph and AutoGen implementations is in the arxiv paper. The governance argument — that non-technical stakeholders can review an SPL script and approve it — is testable on the first recipe you run.

**If you want to contribute**: the catalog grows one recipe at a time. The recipe-maker generates the scaffold; your domain knowledge writes the recipe. Open source, CC-BY licensed, globally accessible.

<!-- --- -->

*Next: Chapter 9.2 — The Recipe Maker: SPL Eating Its Own Cake*
