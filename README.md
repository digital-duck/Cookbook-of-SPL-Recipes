# Title: A Cookbook of SPL Recipes

**Book Project Plan — v0.1**
*Created: 2026-03-21*

---

## Vision

This is the practitioner's book for SPL — the first book that teaches SQL-fluent engineers how to write production agentic AI workflows without learning a Python framework. Every chapter is a recipe: a real, runnable `.spl` file, benchmarked on commodity hardware, with annotated output and reproducibility notes.

The book is the bridge between the arXiv paper (formal contribution) and the PyPI package (`spl-llm`). Readers arrive as data engineers or SQL analysts; they leave as agentic AI practitioners.

---

## One-Sentence Pitch

> *If you can write a SQL query, you can orchestrate a production AI workflow — in one declarative file, on any hardware, without touching Python framework code.*

---

## Target Audience

**Primary**: SQL practitioners, data engineers, analytics engineers, BI developers
**Secondary**: Python developers who want a higher-level abstraction for LLM orchestration
**Tertiary**: AI/ML researchers evaluating declarative workflow languages

**What they know**: SQL (SELECT/WHERE/GROUP BY), maybe some Python, probably some cloud data stack (dbt, Spark, Redshift). They understand prompts conceptually but haven't built multi-step agentic systems.
**What they don't know**: LangGraph state machines, AutoGen agents, LLM orchestration patterns.
**What they want**: ship something that works, understand what it does, reproduce it reliably.

---

## Why This Book, Why Now

- 35 validated recipes, 100% pass rate, benchmarked on a GTX 1080 Ti — the cookbook exists and works
- SPL 2.0 paper submitted to arXiv (arXiv:2602.21257 SPL 1.0; SPL 2.0 in prep) — academic credibility established
- `spl-llm` on PyPI — readers can install and run in 5 minutes
- No comparable book exists: LangChain/LangGraph books teach Python imperative frameworks; no book teaches declarative LLM workflow design
- SQL audience is 10× larger than the Python LLM framework audience; transfer learning from SQL makes SPL uniquely accessible

---

## Publication Options

| Publisher | Model | Timeline | Revenue | Best for |
|-----------|-------|----------|---------|---------|
| **Leanpub** | Self-publish, variable pricing, early access revenue | 3–6 months | ~80% royalty | First book, fast to market, community feedback loop |
| **Manning MEAP** | Early Access Program, professional production | 12–18 months | ~25% royalty | Credibility, O'Reilly-tier reach |
| **O'Reilly** | Premium, requires agent/proposal | 18–24 months | ~10–15% royalty | Maximum market reach, requires track record |

**Recommended path**: Start Leanpub (early access while finishing recipes) → use sales/reader signal to approach Manning for a second edition or a follow-on volume.

---

## Book Structure

### Part 0: Foundations (2 chapters)
The SQL-to-SPL mental model. Why declarative. How to install and run.

### Part 1: Basics (4 recipes / chapters)
First four recipes — get something running, understand the primitive.

### Part 2: Agentic Patterns (7 recipes)
The core value: self-refine, ReAct, plan-and-execute, reflection, multi-model, tool use.

### Part 3: Reasoning (3 recipes)
Chain of thought, tree of thought, hypothesis testing.

### Part 4: Safety & Reliability (2 recipes)
Safe generation, guardrails pipeline.

### Part 5: Memory & Retrieval (2 recipes)
RAG query, memory conversation — and honest treatment of current limitations.

### Part 6: Multi-Agent Systems (5 recipes)
Debate arena, collaboration, ensemble voting, Socratic tutor, interview sim.

### Part 7: Applications (10 recipes)
Real tasks: code review, sentiment pipeline, support triage, map-reduce, data extraction, and more.

### Part 8: Benchmarking & Evaluation (3 recipes)
Model showdown, A/B test, batch testing — how to measure and compare.

### Part 9: The Bigger Picture (1 chapter)
Where SPL 2.0 fits: declarative AI, open protocols, Momagrid distributed inference. The road ahead.

---

## Detailed Chapter Map

| Chapter | Recipe # | Recipe Name | Category | SPL Type | Estimated Pages |
|---------|----------|-------------|----------|----------|-----------------|
| **Part 0: Foundations** | | | | | |
| 0.1 | — | Why Declarative? SQL as the Mental Model | — | — | 12 |
| 0.2 | — | Installing spl-llm, Running Your First Workflow | — | — | 10 |
| **Part 1: Basics** | | | | | |
| 1.1 | 01 | Hello World | basics | PROMPT | 8 |
| 1.2 | 02 | Ollama Proxy | basics | PROMPT | 8 |
| 1.3 | 03 | Multilingual | basics | PROMPT | 8 |
| 1.4 | 24 | Few-Shot Learning | basics | PROMPT | 10 |
| **Part 2: Agentic Patterns** | | | | | |
| 2.1 | 05 | Self-Refine | agentic | WORKFLOW | 14 |
| 2.2 | 06 | ReAct Agent | agentic | WORKFLOW | 16 |
| 2.3 | 12 | Plan and Execute | agentic | WORKFLOW | 14 |
| 2.4 | 16 | Reflection Agent | agentic | WORKFLOW | 16 |
| 2.5 | 21 | Multi-Model Pipeline | agentic | WORKFLOW | 14 |
| 2.6 | 25 | Nested Procedures | agentic | WORKFLOW | 12 |
| 2.7 | 36 | Tool-Use | agentic | WORKFLOW | 14 |
| **Part 3: Reasoning** | | | | | |
| 3.1 | 09 | Chain of Thought | reasoning | WORKFLOW | 14 |
| 3.2 | 17 | Tree of Thought | reasoning | WORKFLOW | 16 |
| 3.3 | 35 | Hypothesis Tester | reasoning | WORKFLOW | 14 |
| **Part 4: Safety & Reliability** | | | | | |
| 4.1 | 07 | Safe Generation | safety | WORKFLOW | 12 |
| 4.2 | 18 | Guardrails Pipeline | safety | WORKFLOW | 12 |
| **Part 5: Memory & Retrieval** | | | | | |
| 5.1 | 08 | RAG Query | retrieval | PROMPT | 14 |
| 5.2 | 19 | Memory Conversation | retrieval | WORKFLOW | 14 |
| **Part 6: Multi-Agent** | | | | | |
| 6.1 | 11 | Debate Arena | multi-agent | WORKFLOW | 16 |
| 6.2 | 14 | Multi-Agent Collaboration | multi-agent | WORKFLOW | 16 |
| 6.3 | 20 | Ensemble Voting | multi-agent | WORKFLOW | 14 |
| 6.4 | 32 | Socratic Tutor | multi-agent | WORKFLOW | 14 |
| 6.5 | 33 | Interview Sim | multi-agent | WORKFLOW | 14 |
| **Part 7: Applications** | | | | | |
| 7.1 | 13 | Map-Reduce Summarizer | application | WORKFLOW | 14 |
| 7.2 | 15 | Code Review | application | WORKFLOW | 14 |
| 7.3 | 22 | Text2SPL Demo | application | WORKFLOW | 12 |
| 7.4 | 23 | Structured Output | application | PROMPT | 10 |
| 7.5 | 27 | Data Extraction | application | PROMPT | 10 |
| 7.6 | 28 | Support Triage | application | WORKFLOW | 12 |
| 7.7 | 29 | Meeting Notes | application | WORKFLOW | 12 |
| 7.8 | 30 | Code Gen + Tests | application | WORKFLOW | 14 |
| 7.9 | 31 | Sentiment Pipeline | application | WORKFLOW | 14 |
| 7.10 | 34 | Progressive Summary | application | WORKFLOW | 12 |
| **Part 8: Benchmarking** | | | | | |
| 8.1 | 04 | Model Showdown | benchmarking | PROMPT | 12 |
| 8.2 | 10 | Batch Test | benchmarking | WORKFLOW | 12 |
| 8.3 | 26 | A/B Test | benchmarking | WORKFLOW | 14 |
| **Part 9: The Road Ahead** | | | | | |
| 9.1 | — | Declarative AI: Where SPL Fits | — | — | 12 |
| 9.2 | 00 | The Recipe Maker: SPL Eating Its Own Cake | meta | WORKFLOW | 18 |

**Estimated total: ~438 pages**

---

## Standard Chapter Template

Every recipe chapter follows the same structure. This consistency is a feature — readers can open any chapter and orient immediately.

```
## Chapter N.M — [Recipe Name]

### The Pattern
One-paragraph problem motivation. What task does this solve?
What would the naive Python approach look like? Why is it painful?

### The SPL Approach
The core idea in one sentence. How does SPL's syntax make this
natural to express?

### The .spl File (Annotated)
Full source listing with inline comments explaining each clause.
Side-by-side: SPL concept → SQL analogy where applicable.

### Running It
Copy-paste invocation command.
Expected output (truncated, clean).

### What Just Happened
Walk through the execution trace:
- How many LLM calls were made, and why
- What each GENERATE/EVALUATE/WHILE step did
- Any EXCEPTION handling triggered

### Reproducibility Note
Latency on reference hardware (GTX 1080 Ti, gemma3).
CV% if applicable. Why this recipe is stable or variable.
For WHILE-loop recipes: note that latency depends on LLM quality judgment.

### When to Use This Pattern
Concrete use cases. What makes this recipe the right tool vs alternatives.

### Exercises
2–3 short modifications to try:
- Change a parameter and re-run
- Swap the adapter (ollama → openrouter)
- Combine with another recipe
```

---

## Differentiators from Existing Books

| This Book | LangChain/LangGraph Books | AutoGen Books |
|-----------|--------------------------|---------------|
| Declarative SQL syntax | Imperative Python | Imperative Python |
| Adapter-agnostic (ollama/openrouter/claude) | Framework-locked | Framework-locked |
| All 35 recipes benchmarked and reproducible | Code examples, no systematic benchmarks | Code examples, no systematic benchmarks |
| Target: SQL/data engineers | Target: Python developers | Target: Python developers |
| 1 file per workflow | Multiple files, classes, state graphs | Multiple files, agent definitions |
| Open source (Apache 2.0) | Open source | Open source |

---

## Timeline

| Milestone | Target Date | Notes |
|-----------|-------------|-------|
| Complete recipe walkthrough (all 36) | 2026-04-15 | Currently at recipe #13; ~1 recipe per session |
| Draft Part 0 (Foundations) | 2026-04-20 | Write after walkthrough complete |
| Draft Parts 1–3 (Basics, Agentic, Reasoning) | 2026-05-10 | Highest-value chapters, write first |
| Draft Parts 4–6 (Safety, Retrieval, Multi-Agent) | 2026-05-30 | |
| Draft Parts 7–9 (Applications, Benchmarking, Road Ahead) | 2026-06-20 | |
| Internal review + corrections | 2026-06-30 | |
| Leanpub early access launch | 2026-07-15 | Publish Part 0 + Parts 1–3 as initial release |
| Complete manuscript | 2026-09-01 | |
| Manning/O'Reilly proposal (if pursuing) | 2026-09-15 | Use Leanpub traction as evidence |

---

## Credibility Anchors

These assets already exist and should be referenced prominently:

| Asset | Role in Book |
|-------|-------------|
| arXiv SPL 1.0 (arXiv:2602.21257) | Cite as academic foundation in preface |
| SPL 2.0 paper (in prep) | Cite when submitted; link from book |
| `spl-llm` on PyPI | Primary install instruction; version pinning |
| 35/35 cookbook pass rate | Opening hook: "Every recipe in this book works. We know because we ran all 35." |
| GTX 1080 Ti benchmark | Establishes "runs on commodity hardware" claim concretely |
| Cross-run reproducibility analysis | Source for CV% notes in each chapter |

---

## Key Decisions Still Open

1. **Co-author?** Solo (Wen) or invite a co-author for the Python/framework comparisons?
2. **Language edition?** English only for v1. Chinese edition as v2 (USTC audience)?
3. **Leanpub vs direct PDF?** Leanpub gives community + pricing flexibility. Direct PDF on GitHub gives maximum reach but no payment infrastructure.
4. **Recipe 22 (Text2SPL Demo)?** Currently pending in catalog. Chapter 7.3 depends on it being complete.
5. **Foreword?** Ramin Hasani (Liquid AI) or a prominent SQL/data engineering practitioner?

---

## Connection to Larger Projects

```
arXiv paper (formal contribution)
    └── validates SPL 2.0 semantics and performance claims
         └── referenced by Book (practitioner audience bridge)

PyPI spl-llm
    └── what readers install
         └── all 35 chapters' code runs against this package

Momagrid / MoMa Hub
    └── Chapter 9.1 positions SPL as the workflow layer
        above the distributed inference layer
         └── book becomes the developer onramp for Momagrid contributors
```

---

## Working Files

| File | Purpose |
|------|---------|
| `README.md` (this file) | Project plan and chapter map |
| `brainstorming-ideas.md` | Raw vision fragments, metaphors, voice notes |
| `outline/` | Detailed chapter outlines (to be created per chapter) |
| `drafts/ch09-2-recipe-maker.md` | Chapter 9.2 — The Recipe Maker (complete draft) |
| `code/` | Any supplementary code not already in the cookbook |

---

*"Every atom in a crystal is equally fundamental. Every recipe in this book is equally real — no toy examples, no omitted edge cases, no hardware you can't buy on eBay."*
