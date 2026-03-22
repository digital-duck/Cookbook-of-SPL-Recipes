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

The book is currently text-heavy. The following figures would break up the prose, aid comprehension, and give DALL-E meaningful work to do. Grouped by chapter location and purpose.

---

## Part 0 — Foundations

### Figure 0.1 — The SPL Stack (Chapter 1.1)
**Purpose:** Show the three-tier architecture visually so readers grasp the full system before writing a line of code.

**Concept:** A layered kitchen illustration — three shelves of a kitchen:
- **Bottom shelf (pantry):** SPL 1.0 — labelled jars of PROMPT, SELECT, GENERATE
- **Middle shelf (prep counter):** SPL 2.0 — tools labelled WORKFLOW, EVALUATE, WHILE, EXCEPTION
- **Top shelf (serving window):** Momagrid — a window looking out to a network of small kitchens (GPU nodes) around the world

**DALL-E prompt:**
```
Cross-section illustration of a three-shelf kitchen. Bottom shelf: glass
jars labelled PROMPT, SELECT, GENERATE. Middle shelf: cooking tools
labelled WORKFLOW, EVALUATE, WHILE. Top shelf/window: small kitchens
visible through a window representing a distributed network. Warm colors,
flat illustration style, no people.
```

---

### Figure 0.2 — Imperative vs Declarative (Chapter 1.1)
**Purpose:** The "before and after" moment — the core argument of the book made visual.

**Concept:** Split image. Left side: a tangled mess of wires, pipes, and valves (imperative Python — the plumber's nightmare). Right side: a clean, simple recipe card with three lines (SPL — the chef's clarity). Same kitchen, same ingredients, completely different experience.

**DALL-E prompt:**
```
Split illustration. Left half: chaotic tangle of pipes, valves, and wires
labeled with technical jargon, overwhelmed plumber. Right half: clean
simple recipe card with three clear lines, calm chef reading it. Same
warm kitchen background. Flat illustration style, warm colors.
```

---

### Figure 0.3 — The Adapter as Oven (Chapter 1.2)
**Purpose:** Make adapter portability concrete and memorable.

**Concept:** The same pizza (recipe / `.spl` file) being slid into three different ovens side by side — a home wood-fired oven (Ollama/local), a professional restaurant oven (OpenRouter/cloud), and a communal outdoor clay oven (Momagrid/decentralized). Same pizza, three ovens.

**DALL-E prompt:**
```
Three ovens side by side: a rustic wood-fired home oven, a stainless
steel professional restaurant oven, and an outdoor clay community oven.
The same pizza being placed into each. Top-down perspective. Warm
lighting, flat illustration style.
```

---

## Part 2 — Agentic Patterns

### Figure 2.1 — The Self-Refine Loop (Chapter 3.1)
**Purpose:** Show the draft → critique → revise cycle visually before the code. Readers should see the pattern before reading the SPL.

**Concept:** A potter at a wheel. First throw is rough clay (draft). The potter examines it critically (critique). Reshapes it (revise). Examines again. The final pot on a shelf. A small counter in the corner shows "iteration 2 / 5".

**DALL-E prompt:**
```
Sequence of four panels showing a potter at a wheel: (1) rough first
clay pot, (2) potter examining it critically, (3) hands reshaping the
clay, (4) finished refined pot on a shelf with a small "iteration 2/5"
label. Warm earthy tones, flat illustration style.
```

---

### Figure 2.2 — The ReAct Loop (Chapter 3.2)
**Purpose:** Illustrate the Think → Act → Observe cycle that drives a ReAct agent.

**Concept:** A chef in three poses in a kitchen — (1) thinking, looking at a recipe (Think), (2) reaching into a cabinet or using a tool (Act), (3) tasting from a spoon and nodding (Observe). Arrow cycle connecting the three poses.

**DALL-E prompt:**
```
Three-panel circular illustration of a chef: (1) chef thinking, looking
at a recipe card, (2) chef acting, reaching into a spice cabinet,
(3) chef observing, tasting from a wooden spoon. Circular arrows
connecting the panels. Flat illustration style, warm kitchen colors.
```

---

### Figure 2.3 — Plan and Execute (Chapter 3.3)
**Purpose:** Show the two-phase nature: plan first, then execute step by step.

**Concept:** A sous chef writing a mise en place list (the plan), then the same chef executing each item in sequence — chopping, sautéing, plating. The list has checkboxes getting ticked off.

**DALL-E prompt:**
```
Two-panel illustration. Left panel: chef writing a detailed mise en place
checklist. Right panel: same chef executing the list step by step, with
checkboxes being ticked off. Flat illustration style, warm colors.
```

---

## Part 3 — Reasoning

### Figure 3.1 — Chain of Thought (Chapter 4.1)
**Purpose:** Show sequential reasoning as a chain of stepping stones.

**Concept:** A person crossing a stream on stepping stones, each stone labeled with a reasoning step. The far bank is the answer. The stones are clearly sequential — you cannot skip.

**DALL-E prompt:**
```
Illustration of a person stepping across a stream on stepping stones,
each stone labeled with a step in a reasoning chain. The far bank shows
a lightbulb representing the answer. Sequential, cannot skip stones.
Flat illustration style, cool blue-green water, warm stone colors.
```

---

### Figure 3.2 — Tree of Thought (Chapter 4.2)
**Purpose:** Contrast with chain of thought — show branching exploration.

**Concept:** A fruit tree. The trunk is the initial question. Branches split at decision points. Some branches end in fruit (good reasoning paths). Others are pruned (dead ends). The best fruit is at the end of the best branch.

**DALL-E prompt:**
```
Illustration of a tree where the trunk is labeled "question", branches
split into reasoning paths, some branches end with ripe fruit (good
outcomes), others are pruned with small red X marks (dead ends). The
largest fruit hangs from the best branch. Flat illustration style,
warm autumn colors.
```

---

## Part 5 — Memory & Retrieval

### Figure 5.1 — RAG as a Library (Chapter 6.1)
**Purpose:** Make RAG (Retrieval Augmented Generation) concrete for readers who may not know the term.

**Concept:** A chef consulting a library of recipe books before cooking. The chef pulls the most relevant book from the shelf (retrieval), reads the relevant passage (context injection), then cooks (generation). The library shelves are labeled "vector store".

**DALL-E prompt:**
```
Illustration of a chef in a library of recipe books. Chef pulls one
relevant book from a tall shelf labeled "vector store", reads a page,
then turns to cook at a stove. Three-step sequence. Flat illustration
style, warm library colors, wooden shelves.
```

---

## Part 6 — Multi-Agent Systems

### Figure 6.1 — The Debate Arena (Chapter 7.1)
**Purpose:** Show multiple agents arguing and a judge deciding.

**Concept:** A formal debate stage with two podiums facing each other — two chefs presenting their dishes to a seated judge. The judge holds up a scorecard. The audience (empty seats) represents the reader watching the workflow unfold.

**DALL-E prompt:**
```
Illustration of a formal debate stage with two chef podiums facing each
other, each chef presenting a dish. A judge sits between them holding a
scorecard. Formal but warm, flat illustration style, theatre lighting.
```

---

### Figure 6.2 — Ensemble Voting (Chapter 7.3)
**Purpose:** Show N independent outputs converging to one voted result.

**Concept:** Five chefs each cooking the same dish independently. All five dishes brought to a table. A tasting panel votes by raising hands for the best one. The winner dish is circled.

**DALL-E prompt:**
```
Illustration of five chefs each presenting an identical dish on a long
table. A small panel of three tasters at the end of the table, hands
raised to vote. One dish is circled as the winner. Flat illustration
style, warm colors.
```

---

## Part 9 — The Road Ahead

### Figure 9.1 — The Momagrid Network (Chapter 10.2)
**Purpose:** Make the decentralized inference vision tangible — the "anyone with a GPU can contribute" idea.

**Concept:** A world map with small kitchen icons scattered across it — Lagos, São Paulo, Hefei, Jakarta, rural Anhui, a university dorm in Berlin. Lines connect them to a central hub. Each kitchen has a small GPU chip visible. The overall image feels like a global community sharing compute, not a corporate data center.

**DALL-E prompt:**
```
Illustrated world map with small kitchen/cooking icons scattered across
continents including Africa, South America, Asia, and Europe. Thin lines
connect each kitchen to a central glowing node. Each kitchen has a small
computer chip symbol. Warm, community feel, flat illustration style,
no corporate or cold aesthetic.
```

---

## Summary Table

| Figure | Location | DALL-E needed | Priority |
|--------|----------|---------------|----------|
| 0.1 The SPL Stack | Ch 1.1 | Yes | High |
| 0.2 Imperative vs Declarative | Ch 1.1 | Yes | High |
| 0.3 The Adapter as Oven | Ch 1.2 | Yes | High |
| 2.1 Self-Refine Loop | Ch 3.1 | Yes | High |
| 2.2 ReAct Loop | Ch 3.2 | Yes | Medium |
| 2.3 Plan and Execute | Ch 3.3 | Yes | Medium |
| 3.1 Chain of Thought | Ch 4.1 | Yes | Medium |
| 3.2 Tree of Thought | Ch 4.2 | Yes | Medium |
| 5.1 RAG as a Library | Ch 6.1 | Yes | Medium |
| 6.1 Debate Arena | Ch 7.1 | Yes | Low |
| 6.2 Ensemble Voting | Ch 7.3 | Yes | Low |
| 9.1 Momagrid Network | Ch 10.2 | Yes | High |

**High priority figures** (6 total) cover the foundations and the book's two most important ideas: the declarative mental model and the global access vision. Generate these first and the book will feel substantially richer even before the rest are done.
