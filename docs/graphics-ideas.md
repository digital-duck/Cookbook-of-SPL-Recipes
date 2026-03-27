# Graphics Ideas — A Cookbook of SPL Recipes

---

## Chosen Concept: The Pizza

### Core Metaphor

A pizza is the ideal cover image for this book. It is a cookbook, and pizza is universally understood across every culture, income level, and geography — speaking directly to both target audiences (SQL practitioners and the Global South).

The metaphor is structurally exact:

| Pizza element | SPL equivalent |
|---------------|---------------|
| **The crust** | SPL 1.0 foundation — PROMPT, SELECT, GENERATE — the base everything builds on |
| **The sauce** | The declarative layer — what binds the workflow together and gives it coherence |
| **The toppings** | The adapters and models — Ollama, Claude, Gemini, OpenRouter, Momagrid, DeepSeek, Qwen — each a distinct ingredient you can swap or combine |
| **The whole pizza** | A complete workflow — composed from parts, the result greater than the sum |

**Same recipe, any oven.** The `.spl` file is the recipe. The adapter is the oven. You change the oven; the recipe stays the same.

---

## Tagline

> *"Flour, topping, oven, you bake."*

Mapping:
- **Flour** = SPL language (the base ingredient)
- **Topping** = your workflow logic (what you want to make)
- **Oven** = the adapter/runtime (Ollama, Claude, Momagrid — your choice)
- **You bake** = declarative execution — you describe it, the runtime does it

The tagline is short, warm, and captures the declarative philosophy without technical jargon. A student in Lagos and a data architect at a Fortune 500 company both understand it immediately.

---

## Cover Layout

```
┌──────────────────────────────────────────┐
│                                          │
│      A Cookbook of SPL Recipes           │  ← title, bold serif, top
│  ────────────────────────────────────    │
│                                          │
│         [ pizza photograph ]             │  ← center, top-down view
│    toppings labeled: ollama, claude,     │
│    gemini, openrouter, momagrid, qwen,   │
│    deepseek, anthropic                   │
│                                          │
│  Declarative Approaches to Agentic       │  ← subtitle, smaller
│  Workflow Orchestration                  │
│                                          │
│  "Flour, topping, oven, you bake."       │  ← tagline, italic
│                                          │
│                          Wen Gong        │  ← author, bottom right
└──────────────────────────────────────────┘
```

---

## Photography Direction

**Shot style:** Top-down (overhead) view of a rustic artisan pizza on a wooden board or dark slate surface. Warm, natural lighting. Food photography style — real and appetizing, not cartoon or illustration.

**Key visual details:**
- Toppings clearly visible and distinct (variety matters — this is a *cookbook of recipes*)
- Slightly imperfect / handmade feel — not a factory pizza, an artisan one
- No text baked into the photo; overlay title/author separately

**Image generation prompt (DALL-E / Midjourney / Stable Diffusion):**
```
Top-down overhead photo of a rustic artisan pizza on a dark wooden board,
various colorful toppings clearly visible, warm soft lighting, food
photography style, shallow depth of field at edges, no text, high
resolution, appetizing
```

---

## Typography

| Element | Font suggestion | Style |
|---------|----------------|-------|
| Title | EB Garamond, Crimson Pro, or Palatino | Bold, large |
| Subtitle | Same font, lighter weight | Regular, medium |
| Tagline | Same font | Italic, small |
| Author | Same font | Regular, small, bottom right |

Use a single font family throughout for cohesion. Serif fonts evoke the warmth of a classic cookbook.

---

## Color Palette

| Role | Color | Hex |
|------|-------|-----|
| Background | Warm cream / kraft paper | `#FDF6E3` |
| Title text | Dark navy | `#1B2A4A` |
| Subtitle / author | Burnt orange | `#C4581D` |
| Tagline | Warm grey | `#6B6055` |

The burnt orange echoes pizza crust and is the accent color throughout. Navy on cream is warm and readable at thumbnail size (critical for Leanpub/Amazon listings).

---

## Why This Cover Stands Out

Most AI/ML technical books use:
- Abstract blue gradients
- Circuit board patterns
- Robot silhouettes
- Generic "neural network" node diagrams

A warm overhead pizza photo is immediately distinctive on any digital shelf or search results page. At thumbnail size (the primary discovery surface on Leanpub, Amazon, and Manning), it reads as a real cookbook — which is exactly what this is.

The O'Reilly animal and Manning portrait conventions work because they are memorable and consistent. For a self-published first edition on Leanpub, a strong thematic image tied directly to the book's metaphor is the right move.

---

## Tools for Final Production

| Tool | Use |
|------|-----|
| **Canva** | Easiest: cookbook cover template, drop in photo, set fonts/colors |
| **GIMP / Inkscape** | Free, full control, export at 300 DPI for print |
| **Adobe Express** | Good templates, free tier available |
| **Leanpub cover spec** | 1800 × 2700 px minimum, RGB, PDF or PNG |

---

## Alternative Concepts (Rejected)

| Concept | Why rejected |
|---------|-------------|
| Abstract SQL/code diagram | Too cold; doesn't convey "cookbook" warmth |
| Robot chef | Cliché in 2026 AI publishing landscape |
| Orchestra conductor | Fits the metaphor but not visual enough for a cover thumbnail |
| Circuit board | Overused in AI books; no warmth |

The pizza won because it is warm, universally understood, structurally accurate to the SPL metaphor, and visually distinctive in the current technical book market.

---

---

# Interior Figures

## Design Philosophy: B&W Schematic Style

**Print cost constraint:** Except for the cover (full-colour pizza photo), all interior figures use **black-and-white line art**. This reduces hardcopy printing costs substantially and keeps the book accessible for print-on-demand at low price points.

**Two figure types:**

| Type | When to use | Tool |
|------|-------------|------|
| **Structural diagram** | Flow loops, layer stacks, trees, pipelines — anything where structure *is* the message | TikZ (LaTeX), draw.io, or Excalidraw → export SVG/PDF |
| **Conceptual line-art** | Metaphor illustrations (conductor, ovens, kitchen) where a human image helps — pen-and-ink style, no fills | AI image generation with B&W line-art prompt, or commission line-art |

The DALL-E prompts below are updated for B&W line-art style. Structural diagrams marked **[DIAGRAM]** should be built as proper technical figures, not illustrations — they are clearer, more accurate, and free.

> **Note on colour images:** If a colourful reference image already exists (e.g., a diagram generated earlier), CV tools (Inkscape trace, GIMP desaturate + threshold, or `potrace`) can convert it to a clean B&W schematic. Prefer this over regenerating from scratch.

---

## Part 0 — Foundations (`ch00-*`, `ch01-1`)

### Figure 0.1 — The Conductor Metaphor (`ch00-0` Preface)
**Purpose:** Establish the book's central organising metaphor before the first recipe. Human = conductor, LLMs = orchestra, SPL = score.

**Type:** Conceptual line-art

**Concept:** A conductor (seen from behind) faces a small orchestra. Each musician is labelled with a model name (Gemma, Claude, Llama, Mistral). The score on the stand is labelled `.spl`. The conductor holds a baton. No fills — pure line art, pen-and-ink style.

**Line-art prompt:**
```
Black and white pen-and-ink illustration. A conductor seen from behind,
baton raised, facing a small orchestra. Each musician labelled with a
model name: Gemma, Claude, Llama, Mistral. The music score on the stand
reads ".spl". Clean lines, no fills, textbook illustration style.
```

---

### Figure 0.2 — Human × AI Partnership (`ch00-0` Preface)
**Purpose:** Illustrate the structured partnership: human holds vision and accountability, AI provides speed and breadth.

**Type:** [DIAGRAM] — two-column structure diagram

**Concept:** Two columns separated by a vertical line. Left column header: **Human (Conductor)**; items: Vision, Values, Judgment, Accountability. Right column header: **AI (Orchestra)**; items: Speed, Breadth, Iteration, Reference. Below both columns, a shared row: **Output: Work neither could produce alone**. Arrows from both columns point down to the shared output row.

---

### Figure 0.3 — Imperative vs Declarative (`ch00-1` Why Declarative)
**Purpose:** The core argument of the book made visual — the "before and after" moment.

**Type:** [DIAGRAM] — split comparison

**Concept:** Two boxes side by side. Left box labelled **Imperative (Python)**: a tangle of labelled lines (client, model, max_tokens, response.content[0].text, retry logic, SDK version). Right box labelled **Declarative (SPL)**: three clean lines (GENERATE draft(@topic), GENERATE critique(@draft), GENERATE refine(@draft, @critique)). A vertical dividing line between them. B&W, no fills.

---

### Figure 0.4 — CALL vs GENERATE (`ch00-1` Why Declarative)
**Purpose:** The single most important design decision in any SPL workflow — which operations deserve LLM tokens and which don't.

**Type:** [DIAGRAM] — decision flowchart

**Concept:** A diamond decision node at the top: *"Can code do this reliably?"* Two branches: **Yes → CALL** (box: deterministic, fast, zero tokens, examples: count_words, json.loads, regex) and **No → GENERATE** (box: probabilistic, LLM tokens, examples: assess_argument_quality, draft_proposal, critique_essay). Monochrome, clean box-and-arrow style.

---

### Figure 0.5 — The Adapter as Oven (`ch00-1` Why Declarative / `ch01-2` Ollama Proxy)
**Purpose:** Make adapter portability concrete and memorable.

**Type:** [DIAGRAM] — one-to-many schematic

**Concept:** A single box on the left labelled **workflow.spl** with an arrow branching to three boxes on the right: **ollama** (local GPU), **openrouter** (cloud API), **momagrid** (decentralised grid). Each right-hand box has a small label beneath it: *"--adapter ollama"*, *"--adapter openrouter"*, *"--adapter momagrid"*. The `.spl` box is unchanged across all three. B&W, monospace labels.

---

### Figure 0.6 — The SPL Language Stack (`ch00-2` Installing / `ch01-1` Hello World)
**Purpose:** Show how SPL 1.0, SPL 2.0, and Momagrid relate as layers before readers write a line of code.

**Type:** [DIAGRAM] — layered stack

**Concept:** Three horizontal bands stacked vertically, like a network layer diagram. Bottom band: **SPL 1.0** — labelled constructs: PROMPT, SELECT, GENERATE. Middle band: **SPL 2.0** — labelled constructs: WORKFLOW, EVALUATE, WHILE, EXCEPTION, PROCEDURE. Top band: **Momagrid** — label: distributed runtime, any GPU, any geography. Thin dividing lines between bands. B&W.

---

## Part 2 — Agentic Patterns (`ch02-*`)

### Figure 2.1 — The Self-Refine Loop (`ch02-1` Self-Refine)
**Purpose:** Show the draft → critique → revise cycle before the code. Readers should see the pattern before reading the SPL.

**Type:** [DIAGRAM] — circular flow

**Concept:** Three boxes in a triangle arrangement: **Draft**, **Critique**, **Revise**. Arrows connect them clockwise. A small exit arrow from **Revise** labelled *"quality threshold met?"* leads to a **Commit** terminal box. An iteration counter label on the loop: *"max N iterations"*. B&W box-and-arrow.

---

### Figure 2.2 — The ReAct Loop (`ch02-2` ReAct Agent)
**Purpose:** Illustrate the Think → Act → Observe cycle that drives a ReAct agent.

**Type:** [DIAGRAM] — circular flow

**Concept:** Three boxes in a cycle: **Think** (reason about the goal), **Act** (call a tool or GENERATE), **Observe** (read the result). Arrows cycle clockwise. An exit arrow from **Think** labelled *"goal achieved"* leads to a **Commit** terminal. Distinguish from Self-Refine by labelling the Act box with example tool calls. B&W.

---

### Figure 2.3 — Plan and Execute (`ch02-3` Plan and Execute)
**Purpose:** Show the two-phase nature: one planning LLM call, then sequential execution of the plan.

**Type:** [DIAGRAM] — two-phase pipeline

**Concept:** A vertical line divides two phases. Left phase: **Plan** — single GENERATE box producing a labelled list (Step 1, Step 2, Step 3 … Step N). Right phase: **Execute** — the same list items as sequential boxes with CALL/GENERATE labels, connected top-to-bottom with arrows, a checkbox ticking off each step. B&W.

---

## Part 3 — Reasoning (`ch03-*`)

### Figure 3.1 — Chain of Thought (`ch03-1` Chain of Thought)
**Purpose:** Show sequential reasoning as a linear chain — steps cannot be skipped.

**Type:** [DIAGRAM] — linear chain

**Concept:** A horizontal chain of labelled boxes connected by arrows: **Step 1** → **Step 2** → **Step 3** → **…** → **Answer**. Each box has a short label (e.g., "identify premises", "check consistency", "draw conclusion"). The linearity — no branches, no skips — is the message. B&W, monospace labels.

---

### Figure 3.2 — Tree of Thought (`ch03-2` Tree of Thought)
**Purpose:** Contrast with Chain of Thought — branching exploration, pruning dead ends.

**Type:** [DIAGRAM] — tree/graph

**Concept:** A rooted tree. Root node: **Question**. Branches split into reasoning paths. Some leaf nodes marked with ✓ (promising), others with ✗ (pruned dead ends). The best path from root to answer is highlighted with a thicker line. This is a standard computer-science tree diagram and works excellently in B&W — no illustration needed.

---

## Part 4 — Safety & Guardrails (`ch04-*`)

### Figure 4.1 — The Guardrails Pipeline (`ch04-2` Guardrails Pipeline)
**Purpose:** Show safety as a pipeline layer that wraps generation — input filtering before, output validation after.

**Type:** [DIAGRAM] — pipeline with wrapper layers

**Concept:** A horizontal pipeline: **Input** → [**Input Guard** box] → **GENERATE** → [**Output Guard** box] → **Output**. The guard boxes are drawn with double borders to indicate they are wrappers. Rejected paths branch downward from each guard to a **Reject / Flag** terminal. B&W.

---

## Part 5 — Memory & Retrieval (`ch05-*`)

### Figure 5.1 — RAG Pipeline (`ch05-1` RAG Query)
**Purpose:** Make Retrieval-Augmented Generation concrete for readers who may not know the term.

**Type:** [DIAGRAM] — three-step pipeline

**Concept:** Three sequential boxes: **1. Retrieve** (query → vector store → top-K chunks), **2. Inject** (chunks + original query → assembled context), **3. Generate** (context → LLM → answer). Arrows connect the boxes. A small side box labelled **Vector Store** connects to step 1 with a dashed retrieval arrow. B&W.

---

## Part 6 — Multi-Agent Systems (`ch06-*`)

### Figure 6.1 — The Debate Arena (`ch06-1` Debate Arena)
**Purpose:** Show multiple agents arguing to a judge — convergence through adversarial process.

**Type:** [DIAGRAM] — N-to-1 convergence

**Concept:** Two boxes on the left (**Agent A**, **Agent B**) with arrows pointing to a central box (**Judge / Evaluator**). The Judge box has an arrow to a **Decision** terminal on the right. Optionally add a feedback arrow from Judge back to agents for multi-round debate. B&W.

---

### Figure 6.2 — Ensemble Voting (`ch06-3` Ensemble Voting)
**Purpose:** Show N independent outputs converging to one voted result.

**Type:** [DIAGRAM] — fan-out / fan-in

**Concept:** One input box at the top fans out to N parallel boxes (Agent 1 … Agent N) via branching arrows. All N boxes fan back in to a **Voting / Aggregation** box at the bottom, which produces a single **Output**. N = 5 is typical — show 5 parallel boxes. B&W, clean parallel layout.

---

## Part 7 — Production Patterns (`ch07-*`)

### Figure 7.1 — Map-Reduce Summarizer (`ch07-1` Map-Reduce Summarizer)
**Purpose:** Show parallel chunk processing (Map) followed by aggregation (Reduce) — the signature pattern for long-document workflows.

**Type:** [DIAGRAM] — fan-out / fan-in with two stages

**Concept:** A **Document** box at top splits into N **Chunk** boxes (fan-out). Each chunk feeds into a **Summarize** GENERATE box (the Map stage). All summaries feed into a single **Reduce** GENERATE box (the Reduce stage), which produces the **Final Summary**. Label the fan-out "CALL split()" and the fan-in "GENERATE reduce()". B&W.

---

## Part 9 — The Road Ahead (`ch09-1`, `ch00-4`)

### Figure 9.1 — The Momagrid Network (`ch09-1` Road Ahead / `ch00-4` LAN Momagrid)
**Purpose:** Make the decentralised inference vision tangible — anyone with a GPU can contribute.

**Type:** Conceptual line-art (schematic map)

**Concept:** A simplified world map outline (B&W, no fills). Small square node icons scattered across it — Lagos, São Paulo, Hefei, Jakarta, Berlin, Nairobi. Thin lines connect nodes to each other (mesh topology, not hub-and-spoke). Each node labelled with a city name and a small GPU symbol. No corporate aesthetic — emphasise the distributed, community nature.

**Line-art prompt:**
```
Black and white schematic world map outline, no fills. Small square
node icons at Lagos, São Paulo, Hefei, Jakarta, Berlin, Nairobi — each
labelled with city name and a small GPU chip symbol. Thin connecting
lines between nodes in a mesh pattern. Clean technical illustration
style, no shading.
```

---

## Summary Table

| Figure | Chapter file | Type | Priority |
|--------|-------------|------|----------|
| 0.1 Conductor Metaphor | `ch00-0` Preface | Line-art | High |
| 0.2 Human × AI Partnership | `ch00-0` Preface | Diagram | High |
| 0.3 Imperative vs Declarative | `ch00-1` Why Declarative | Diagram | High |
| 0.4 CALL vs GENERATE | `ch00-1` Why Declarative | Diagram | **Critical** |
| 0.5 The Adapter as Oven | `ch00-1` / `ch01-2` | Diagram | High |
| 0.6 The SPL Language Stack | `ch00-2` / `ch01-1` | Diagram | Medium |
| 2.1 Self-Refine Loop | `ch02-1` | Diagram | High |
| 2.2 ReAct Loop | `ch02-2` | Diagram | Medium |
| 2.3 Plan and Execute | `ch02-3` | Diagram | Medium |
| 3.1 Chain of Thought | `ch03-1` | Diagram | Medium |
| 3.2 Tree of Thought | `ch03-2` | Diagram | Medium |
| 4.1 Guardrails Pipeline | `ch04-2` | Diagram | Medium |
| 5.1 RAG Pipeline | `ch05-1` | Diagram | Medium |
| 6.1 Debate Arena | `ch06-1` | Diagram | Low |
| 6.2 Ensemble Voting | `ch06-3` | Diagram | Low |
| 7.1 Map-Reduce | `ch07-1` | Diagram | Medium |
| 9.1 Momagrid Network | `ch09-1` / `ch00-4` | Line-art | High |

**Build order:** Start with the four Critical/High diagrams in Part 0 — they support the most-read chapters and require no image generation (pure diagrams). The two line-art figures (0.1 Conductor, 9.1 Momagrid) can be generated or commissioned independently.
