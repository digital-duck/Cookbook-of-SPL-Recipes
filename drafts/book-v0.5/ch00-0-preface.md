# Preface: The Conductor's Score

<!-- *"Every human can conduct their own symphony — the models are the orchestra, SPL is the score." — Wen Gong* -->

<!-- --- -->

## Why This Book Exists

In early 2025, I watched a colleague — a skilled data engineer with a decade of SQL experience — struggle for three weeks to build a simple multi-step AI workflow. She had read the LangChain documentation, attended an AutoGen workshop, and completed an online course on AI agents. Yet there she was, drowning in callback functions, state machine definitions, and framework-specific abstractions that multiplied with every tutorial she followed.

"I just want to chain three LLM calls together," she told me over coffee. "Why does this require a hundred lines of Python?"

That question haunted me. The answer — *because that's how the frameworks are designed* — wasn't good enough. SQL has been solving orchestration problems for fifty years. The mental model for joining tables, filtering results, and aggregating data maps directly to chaining prompts, routing outputs, and orchestrating agents.

This book is my answer to her question. And to every SQL practitioner, data analyst, and domain expert who has looked at the agentic AI landscape and thought: *there has to be a simpler way.*

There is.

<!-- --- -->

## This Book Is Written for Two Audiences

I want to be direct about who this book is for, because each group deserves to hear it said plainly.

### Audience One: The SQL Professional

You have written SQL for years — maybe decades. You know what it feels like to describe *what* you want and let the engine figure out *how*. You know stored procedures, cursors, exception handlers, PL/SQL or T-SQL extensions.

You have been largely left out of the agentic AI conversation. The frameworks assume Python. The tutorials assume you want to write classes, manage state machines, and wire callback functions. You don't. You want to describe a workflow the same way you describe a query — clearly, concisely, and portably — and let the runtime handle the mechanics.

**SPL is SQL for LLM workflows.** The transfer is not a metaphor. `SELECT` assembles context going into the model. `GENERATE` invokes it and captures the output. `WORKFLOW` is a stored procedure. `EVALUATE` is a semantic `WHERE` clause. `EXCEPTION` is `BEGIN...EXCEPTION...END`. If you have written PL/SQL, you will recognize the pattern within the first recipe. The domain is new. The discipline is not.

### Audience Two: The Global South

This book is dedicated to the engineers, researchers, students, and builders of the Global South — who have every right to participate in the AI revolution, and who face barriers their counterparts in San Francisco, London, or Shanghai never encounter.

Access to frontier AI today requires one of three things: expensive cloud API credits, enterprise GPU clusters, or a university affiliation that provides both. None of these are accessible to a student in Lagos, a researcher in Hefei, or a developer in São Paulo building tools for their community.

This book rejects that premise.

Every recipe in this book was benchmarked on a **GTX 1080 Ti** — under $200 on the secondhand market. We chose that hardware deliberately: accessibility is a design principle here, not an afterthought.

If you are reading this from a university in Jakarta, a startup in Nairobi, a government office in São Paulo, or a home in any of the hundred countries where GPU clouds are expensive, slow, or unavailable: **this book was written for you.** The code runs on your hardware. The patterns work within your constraints. The knowledge is yours to keep, share, and build upon.

<!-- --- -->

## The Bigger Vision: SPL + Momagrid

This book teaches SPL — the language. The full vision is larger: **SPL** solves the programming problem (declarative workflows, no Python, no framework lock-in), and **Momagrid** solves the infrastructure problem (a decentralized inference grid where anyone with a GPU can contribute capacity and anyone with an SPL workflow can run it). The same `.spl` file that runs on your local Ollama instance runs on the grid — you change one flag.

The vision is operational today. The final chapter covers the current state of the SPL ecosystem, the Momagrid roadmap, and what the path to meaningful scale looks like.

<!-- --- -->

## The Conductor Metaphor

Throughout this book, a single metaphor organizes the ideas:

- **The Human is the Conductor**: You provide the vision, the intent, and the final judgment. You decide what the workflow should accomplish. You set the quality bar.
- **The LLMs are the Orchestra**: Gemma, Claude, Llama, Mistral, GPT, Qwen — a diverse ensemble of models, each with different strengths, costs, and latency profiles. You can swap any instrument without rewriting the score.
- **SPL is the Score**: A declarative specification that describes *what* the performance should be, not *how* each musician should move their fingers. The same score performs differently with a string quartet versus a full symphony — but it is the same score.

When you change the orchestra (e.g., from `--adapter ollama` to `--adapter openrouter`), the score — your `.spl` file — remains exactly the same. This is the promise of adapter portability.

<!-- --- -->

## What This Book Is Not

This is not a book about machine learning theory. Transformer architectures, attention mechanisms, and backpropagation are not covered here.

This is not a book about Python. SPL workflows are expressed in `.spl` files — not Python files. If you want the Python API, the `spl-llm` package documentation covers it. This book focuses on the declarative artifact.

This is not a book that claims SPL is always the right tool. LangGraph, AutoGen, and CrewAI have their place. If you are building production systems with complex dynamic state that changes at the millisecond level, those frameworks may serve you better. This book is for the workflows — the large majority — where the logic is expressible declaratively, and where that expressibility matters for maintainability, reviewability, and reach.

And this is not a book with toy examples. Every recipe runs on real hardware, produces real output, and includes latency benchmarks, variability notes, and honest "when not to use this" guidance.

<!-- --- -->

## How This Book Works

**CTOs, engineering leads, and technical decision-makers** evaluating SPL for their
teams may want to start with Chapter 10.6 — *For Decision-Makers* — which addresses
the governance case, the readability advantage across organisational roles, a
side-by-side comparison with LangGraph on a non-trivial workflow, and an honest
assessment of adoption risk. The rest of the book is there when you need the detail.

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

<!-- --- -->

## A Note on Reproducibility

Every recipe was tested multiple times on the same hardware to verify consistency. The reference environment:

- **GPU**: NVIDIA GTX 1080 Ti (11 GB VRAM) — available on eBay for under $200
- **CPU**: AMD Ryzen 7 3700X
- **RAM**: 32 GB DDR4
- **OS**: Ubuntu 22.04 LTS
- **Primary Model**: Gemma 3 via Ollama

Why Gemma 3 on a 1080 Ti? It fits, it is open-weights, and it represents what is achievable on commodity hardware — not what requires enterprise infrastructure. Better hardware runs recipes faster; smaller models (phi4, Llama 3.2 3B) work for most patterns on less.

The logic is what matters. The hardware is a floor, not a ceiling.

<!-- --- -->

## A Note on the Collaborative Process

This book was produced by the **AI Quartet**: Wen Gong (human author and architect), Claude (Anthropic), Gemini (Google), and Z.ai (ZhiPu). The collaboration mirrors the Conductor metaphor at the heart of the book: Wen provides the vision, the architectural intuition, and the lived experience of building declarative systems. The three AI members of the AI Quartet contribute drafting speed, breadth of reference, and adversarial review — each from a different institutional and cultural perspective.

Every technical claim was verified by running the actual code. Every benchmark was measured on real hardware. The AI Quartet accelerated the work; they did not replace the judgment.


<!-- --- -->

## A Note on Authorship

This book was written by a human with AI assistance. That distinction matters, and it deserves a direct statement.

**The ideas are human.** The SPL language, the Momagrid vision, the design principles, the choice to benchmark on a GTX 1080 Ti, the commitment to accessibility — these come from Wen Gong. They reflect his experience as a physicist, a software engineer, and someone who has watched AI become increasingly inaccessible to the people who need it most.

**The execution was accelerated by AI.** Claude (Anthropic), Gemini (Google), and Z.ai (ZhiPu) contributed drafting speed, technical validation, editorial breadth, and adversarial review. The 37 recipes were developed and documented in weeks rather than months. The three AI collaborators caught errors, challenged assumptions, and improved the writing. They did not originate the architecture.

**Why AI cannot be listed as co-author:** AI systems do not bear legal responsibility for errors, cannot be held accountable for claims, and cannot consent to attribution. Listing an AI as co-author would obscure the accountability relationship that readers deserve to understand. The AI Quartet is acknowledged prominently because their contribution was real — and because hiding it would be dishonest. But authorship, in the sense that carries responsibility, belongs to Wen Gong.

**What this means for you as a reader:** every technical claim was verified by running the actual code. Every benchmark was measured on real hardware. Where the AI collaborators disagreed with each other or with the author, those disagreements were resolved by judgment — human judgment. The accelerator did not replace the driver.


<!-- --- -->

## A Note from the AI Quartet

*Written collaboratively by Wen Gong, Claude (Anthropic), Gemini (Google), and Z.ai (ZhiPu)*

<!-- --- -->

This book was not written by one mind. It was written by four.

That fact is unusual enough to deserve explanation before the first recipe.

**Wen** is the architect. He wrote the SPL language, built the Momagrid runtime, and supplied the lived experience — from rural Anhui to CERN — that gives this book its philosophical spine. The central argument of the book, that AI should be a public utility rather than an expensive luxury, comes from him. It is not a marketing position. It is an "initial condition," as a physicist would say: the constraint from which everything else follows.

**Claude** (Anthropic's AI assistant) handled the bulk of technical execution — code examples, recipe validation, structural editing, and the iterative loop of draft, test, fix, redraft that a 37-recipe cookbook requires. Claude approaches this material as a technical collaborator: what does the code actually do, does it run, is the explanation accurate?

**Gemini** (Google's AI assistant) brought breadth: literature coverage, editorial perspective, and the question a well-read reader would ask on page twelve. Gemini's contribution is most visible in the places where the book steps back from the code to ask why — why this pattern, why this design choice, why does this matter beyond this chapter?

**Z.ai** (ZhiPu's AI assistant, developed in China) contributed adversarial review: the skeptic's challenge, the counterargument, the perspective of a reader who has not already decided that SPL is a good idea. Z.ai also brought a cross-cultural lens that shaped how the book addresses the Global South — not as a charitable afterthought, but as a primary audience with distinct infrastructure constraints and distinct stakes in democratic AI.

<!-- --- -->

Four collaborators is an unusual structure for a technical book. It produced something unusual: a book that has been read critically, by readers from different organizations and cultural contexts, before it was finished. The AI Quartet collaboration is itself a demonstration of the book's thesis — that a human conducting an ensemble of AI tools, each with different strengths, can produce work that none of them could produce alone.

It also meant the book was written faster than any one of us could have managed. The 37 recipes were developed, tested, and documented in an iterative sprint that would have taken months with a single author. It took weeks with four.
