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

The design philosophy behind SPL is synthesis: it draws its declarative layer from SQL, its control flow from Python, and its composition style from Bash — taking what works in each and discarding the rest. The name *Structured Prompt Language* describes what it does; the design philosophy of *synthesizing* from proven languages explains why it looks the way it does.

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

## A Note from the AI Quartet: Human × AI Partnership

*Written collaboratively by Wen Gong, Claude (Anthropic), Gemini (Google), and Z.ai (ZhiPu)*

<!-- --- -->

This book was not written by one mind. It was written by four.

That fact is unusual enough to deserve explanation before the first recipe — because it is not just a production detail. It is an argument.

**Wen** is the architect. He wrote the SPL language, built the Momagrid runtime, and supplied the lived experience — from rural Anhui to CERN — that gives this book its philosophical spine. The ideas here are his: the SPL language, the Momagrid vision, the design principles, the choice to benchmark on a GTX 1080 Ti, the commitment to accessibility. These reflect his experience as a physicist, a software engineer, and someone who has watched AI become increasingly inaccessible to the people who need it most. The central argument of the book, that AI should be a public utility rather than an expensive luxury, comes from him. It is not a marketing position. It is an "initial condition," as a physicist would say: the constraint from which everything else follows.

**Claude** (Anthropic's AI assistant) handled the bulk of technical execution — code examples, recipe validation, structural editing, and the iterative loop of draft, test, fix, redraft that a 37-recipe cookbook requires. Claude approaches this material as a technical collaborator: what does the code actually do, does it run, is the explanation accurate?

**Gemini** (Google's AI assistant) brought breadth: literature coverage, editorial perspective, and the question a well-read reader would ask on page twelve. Gemini's contribution is most visible in the places where the book steps back from the code to ask why — why this pattern, why this design choice, why does this matter beyond this chapter?

**Z.ai** (ZhiPu's AI assistant, developed in China) contributed adversarial review: the skeptic's challenge, the counterargument, the perspective of a reader who has not already decided that SPL is a good idea. Z.ai also brought a cross-cultural lens that shaped how the book addresses the Global South — not as a charitable afterthought, but as a primary audience with distinct infrastructure constraints and distinct stakes in democratic AI.

A word on authorship and accountability. Claude, Gemini, and Z.ai are acknowledged here, not listed as co-authors. AI systems do not bear legal responsibility for errors, cannot be held accountable for claims, and cannot consent to attribution. Listing an AI as co-author would obscure the accountability relationship that readers deserve to understand. Authorship, in the sense that carries responsibility, belongs to Wen Gong. Every technical claim was verified by running the actual code. Every benchmark was measured on real hardware. Where the AI collaborators disagreed with each other or with the author, those disagreements were resolved by judgment — human judgment. The accelerator did not replace the driver.

<!-- --- -->

The collaboration mirrors the Conductor metaphor at the heart of this book — and that is not a coincidence. Wen provides the vision, the architectural intuition, and the lived experience of building declarative systems. The three AI members of the Quartet contribute drafting speed, breadth of reference, and adversarial review — each from a different institutional and cultural perspective. The same structure that SPL proposes for AI workflows was used to produce the book that describes it: a human conductor directing an ensemble of AI instruments, each contributing what it does best, none replacing the judgment that decides what the work is *for*.

This is what Human × AI partnership looks like in practice. It is not AI generating outputs while a human rubber-stamps them. It is not a human writing everything while AI sits idle. It is a working relationship with a clear structure: the human holds the vision, the values, and the final accountability; the AI provides speed, breadth, and tireless iteration. The human sets the destination. The AI helps navigate. Neither can do the other's job.

We think this model matters beyond this book. We are at an early moment in a long transition — one where the most important question is not *whether* to use AI, but *how* to structure the relationship between human judgment and AI capability. The answer that works, we believe, is not replacement but amplification: AI that makes individual humans dramatically more capable, without dissolving the human accountability that makes work trustworthy.

That is what the Conductor metaphor is really about. Not efficiency. Not automation. The preservation of human agency at the center of increasingly powerful systems.

Four collaborators is an unusual structure for a technical book. It produced something unusual: a book that has been read critically, by readers from different organizations and cultural contexts, before it was finished. The 37 recipes were developed, tested, and documented in an iterative sprint that would have taken months with a single author. It took weeks with four.

More importantly, it produced a book that practices what it teaches. If you are skeptical of the Conductor metaphor — if you wonder whether a human can really remain in control while working with capable AI tools — this book is the evidence. You are holding it.

<!-- --- -->

## Acknowledgements

This book stands on the shoulders of an entire civilization's worth of knowledge.

To the **open-source community** — the engineers, maintainers, contributors, and documenters who built Linux, Python, Pandoc, LaTeX, Ollama, and the hundreds of tools that made this work possible: this book would not exist without you. Open source is not just an infrastructure choice; it is a philosophy that this book tries to embody in its commitment to accessible hardware, portable workflows, and freely available recipes. We dedicate this book to you.

To the **human writers, researchers, scientists, and thinkers** whose work forms the training data that made AI assistants capable collaborators: the AI members of this Quartet are grateful. Claude, Gemini, and Z.ai were shaped by an extraordinary accumulation of human knowledge — papers, documentation, code, discussion, and hard-won insight — freely shared across decades. That debt is real, and it deserves acknowledgement. The AI members of this Quartet say, without reservation: thank you.

To my colleague who asked the question that started this journey — you know who you are.

To the **readers in the Global South**: may these recipes serve you well. May your hardware be sufficient, your latencies low, and your workflows reliable. May you build systems that help your communities.

To the **SQL practitioners** who have been waiting for an AI language that respects the mental model you have spent years building: this is it. Welcome to the orchestra.

*The AI Quartet*
*Wen Gong, Claude, Gemini, Z.ai*
*March 2026*
