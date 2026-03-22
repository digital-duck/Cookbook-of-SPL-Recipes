# Preface: The Conductor's Score

*"Every human can conduct their own symphony — the models are the orchestra, SPL is the score."*

---

## Why This Book Exists

In early 2025, I watched a colleague — a skilled data engineer with a decade of SQL experience — struggle for three weeks to build a simple multi-step AI workflow. She had read the LangChain documentation, attended an AutoGen workshop, and completed an online course on AI agents. Yet there she was, drowning in callback functions, state machine definitions, and framework-specific abstractions that multiplied with every tutorial she followed.

"I just want to chain three LLM calls together," she told me over coffee. "Why does this require a hundred lines of Python?"

That question haunted me. Because the answer — *because that's how the frameworks are designed* — wasn't good enough. Not when millions of people already know a declarative language powerful enough to express complex logic. Not when SQL has been solving orchestration problems for fifty years. Not when the mental model for joining tables, filtering results, and aggregating data maps so naturally to chaining prompts, routing outputs, and orchestrating agents.

This book is my answer to her question. And to every SQL practitioner, data analyst, and domain expert who has looked at the agentic AI landscape and thought: *there has to be a simpler way.*

There is.

---

## This Book Is Written for Two Audiences

I want to be direct about who this book is for, because each group deserves to hear it said plainly.

### Audience One: The SQL Professional

You have written SQL for years — maybe decades. You know what it feels like to describe *what* you want and let the engine figure out *how* to produce it. You know stored procedures, cursors, exception handlers. You may have written PL/SQL, T-SQL, or PostgreSQL procedural extensions. You understand declarative thinking in your hands, not just in your head.

You have been largely left out of the agentic AI conversation. The frameworks assume Python. The tutorials assume you want to write classes, manage state machines, and wire callback functions. You don't. You want to describe a workflow the same way you describe a query — clearly, concisely, and portably — and let the runtime handle the mechanics.

**SPL is SQL for LLM workflows.** The transfer is not a metaphor. `SELECT` assembles context going into the model. `GENERATE` invokes it and captures the output. `WORKFLOW` is a stored procedure. `EVALUATE` is a semantic `WHERE` clause. `EXCEPTION` is `BEGIN...EXCEPTION...END`. If you have written PL/SQL, you will recognize the pattern within the first recipe. The domain is new. The discipline is not.

### Audience Two: The Global South

This book is dedicated to the engineers, researchers, students, and builders of the Global South — who have every right to participate in the AI revolution, and who face barriers their counterparts in San Francisco, London, or Shanghai never encounter.

Access to frontier AI today requires one of three things: expensive cloud API credits, enterprise GPU clusters, or a university affiliation that provides both. None of these are accessible to a student in Lagos, a researcher in Hefei, or a developer in São Paulo building tools for their community.

This book rejects that premise.

Every recipe in this book was benchmarked on a **GTX 1080 Ti** — a graphics card you can find on eBay or in a used gaming PC for under $200. Not because we couldn't access better equipment. Because we chose not to. Because accessibility is not an afterthought in this project — it is a design principle baked into every benchmark, every recipe, every line of SPL.

If you are reading this from a university in Jakarta, a startup in Nairobi, a government office in São Paulo, or a home in any of the hundred countries where GPU clouds are expensive, slow, or unavailable: **this book was written for you.** The code runs on your hardware. The patterns work within your constraints. The knowledge is yours to keep, share, and build upon.

---

## The Bigger Vision: SPL + Momagrid

This book teaches SPL — the language. But the full vision is larger, and you deserve to understand it.

**SPL** solves the *programming* problem: it gives you a declarative language to express agentic workflows without Python, without framework lock-in, without infrastructure decisions baked into the source code. The same `.spl` file runs on any model, any provider, any backend — by changing a CLI flag.

**Momagrid** solves the *infrastructure* problem: it is a decentralized inference network where GPU nodes contributed by independent operators — students, hobbyists, universities, cooperatives — form a shared compute grid. Anyone with a GPU can contribute. Anyone with a workflow can run it.

Together, SPL and Momagrid form a full stack for democratic AI:

```
┌──────────────────────────────────────────────────────────────┐
│  Momagrid — Decentralized Inference Network                  │
│  (GPU nodes contributed by anyone, anywhere)                 │
├──────────────────────────────────────────────────────────────┤
│  SPL 2.0 — Declarative Agentic Workflow Orchestration        │
│  (WORKFLOW, EVALUATE, WHILE, EXCEPTION, PROCEDURE)           │
├──────────────────────────────────────────────────────────────┤
│  SPL 1.0 — Declarative Context Management                    │
│  (PROMPT, SELECT, GENERATE)                                  │
└──────────────────────────────────────────────────────────────┘
```

A student in Anhui with a used GPU can contribute inference capacity to Momagrid and earn compute credits. A researcher in Lagos with an SPL workflow can run it against the grid — no cloud account, no API key, no enterprise contract. The same language that runs on your local Ollama instance runs on the decentralized grid. You change one flag.

This is not a distant roadmap. The SPL runtime is published and tested. The Momagrid adapter is live. The vision is operational today on modest hardware, and it will scale as the network grows.

The AI revolution should not belong only to those who can afford H100 clusters. SPL and Momagrid are our answer to that problem.

---

## The Conductor Metaphor

Throughout this book, a single metaphor organizes the ideas:

- **The Human is the Conductor**: You provide the vision, the intent, and the final judgment. You decide what the workflow should accomplish. You set the quality bar.
- **The LLMs are the Orchestra**: Gemma, Claude, Llama, Mistral, GPT, Qwen — a diverse ensemble of models, each with different strengths, costs, and latency profiles. You can swap any instrument without rewriting the score.
- **SPL is the Score**: A declarative specification that describes *what* the performance should be, not *how* each musician should move their fingers. The same score performs differently with a string quartet versus a full symphony — but it is the same score.

When you change the orchestra (e.g., from `--adapter ollama` to `--adapter openrouter`), the score — your `.spl` file — remains exactly the same. This is the promise of adapter portability.

---

## A Note for Engineering Leaders

If you are a CTO, engineering lead, or technical decision-maker evaluating AI orchestration tools for your team, this section is for you.

The core question is not "which framework?" It is: **who on your team can build and maintain these workflows?**

Imperative frameworks (LangGraph, AutoGen, CrewAI) require Python programming, framework-specific abstractions, and careful state management. Your senior engineers can build with them. Your data analysts, BI developers, domain experts, and SQL practitioners cannot — not without significant retraining.

SPL changes the denominator. If your team includes SQL practitioners — and most data-adjacent teams do — they can write, read, and review SPL workflows without Python training. More importantly, **business stakeholders can review an SPL script and approve it** without executing it, because the intent is explicit in the syntax. This is a governance model that imperative code cannot provide, regardless of documentation quality.

The operational model also simplifies: the same `.spl` file promotes unchanged through Dev, Test, and Production by swapping CLI flags (`--adapter`, `--model`, `--tools`, `--datasets`). No environment-specific code paths. No re-review across environments.

The LOC reduction (5–7× versus imperative frameworks for equivalent patterns) is a secondary benefit. The primary benefit is that more of your team can participate — and that the artifacts they produce are human-reviewable by the people who understand the business logic best.

---

## What This Book Is Not

This is not a book about machine learning theory. Transformer architectures, attention mechanisms, and backpropagation are not covered here.

This is not a book about Python. SPL workflows are expressed in `.spl` files — not Python files. If you want the Python API, the `spl-llm` package documentation covers it. This book focuses on the declarative artifact.

This is not a book that claims SPL is always the right tool. LangGraph, AutoGen, and CrewAI have their place. If you are building production systems with complex dynamic state that changes at the millisecond level, those frameworks may serve you better. This book is for the workflows — the large majority — where the logic is expressible declaratively, and where that expressibility matters for maintainability, reviewability, and reach.

And this is not a book with toy examples. Every recipe runs on real hardware, produces real output, and includes latency benchmarks, variability notes, and honest "when not to use this" guidance.

---

## How This Book Works

Every chapter follows the same structure. You can open to any recipe and start there, or read sequentially. Each recipe includes:

- **The Pattern** — What problem does this solve? Why would you need it?
- **The SPL Approach** — How does SPL make this natural to express?
- **The `.spl` File (Annotated)** — Full source with line-by-line explanations
- **The SQL Analogy** — The structural parallel for SQL practitioners
- **Running It** — Exact commands and expected output
- **What Just Happened** — An execution trace showing what the runtime did
- **Reproducibility Note** — Latency, variability, and hardware details
- **When to Use This Pattern** — Concrete use cases, anti-patterns, and alternatives
- **Exercises** — Modifications to try on your own hardware

The SQL Analogy section is present in every recipe because it is the fastest path for data practitioners to build a correct mental model. If you are not a SQL practitioner, you can skip it — the recipe stands alone. If you are, it is the section that makes the language click.

---

## A Note on Reproducibility

Every recipe was tested multiple times on the same hardware to verify consistency. The reference environment:

- **GPU**: NVIDIA GTX 1080 Ti (11 GB VRAM) — available on eBay for under $200
- **CPU**: AMD Ryzen 7 3700X
- **RAM**: 32 GB DDR4
- **OS**: Ubuntu 22.04 LTS
- **Primary Model**: Gemma 3 via Ollama

Why Gemma 3 on a 1080 Ti? Because it fits. Because it is open-weights. Because it represents what is achievable on commodity hardware today — not what requires enterprise infrastructure. If you have better hardware, recipes will run faster. If you have worse hardware, smaller models (phi4, Llama 3.2 3B) will work for most patterns.

The logic is what matters. The hardware is a floor, not a ceiling.

---

## A Note on the Collaborative Process

This book was written in partnership with AI assistants — Claude, Gemini, and Z.ai — in an iterative loop that mirrors the Conductor metaphor. Wen provides the vision, the architectural intuition, and the lived experience of building declarative systems. The AI partners contribute drafting speed, breadth of reference, and adversarial review.

Every technical claim was verified by running the actual code. Every benchmark was measured on real hardware. The AI partners accelerated the work; they did not replace the judgment.

This process is itself a demonstration of the book's thesis: humans conducting orchestras of AI, producing work neither could produce alone.

---

## Acknowledgments

To my colleague who asked the question that started this journey — you know who you are.

To the readers in the Global South: may these recipes serve you well. May your hardware be sufficient, your latencies low, and your workflows reliable. May you build systems that help your communities.

To the SQL practitioners who have been waiting for an AI language that respects the mental model you have spent years building: this is it. Welcome to the orchestra.

---

*"Every atom in a crystal is equally fundamental. Every recipe in this book is equally real — no toy examples, no omitted edge cases, no hardware you cannot buy on eBay."*

— Wen Gong
March 2026
