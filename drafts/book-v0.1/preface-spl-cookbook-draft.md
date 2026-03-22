# Preface

## Why This Book Exists

In early 2025, I watched a colleague—a skilled data engineer with a decade of SQL experience—struggle for three weeks to build a simple multi-step AI workflow. She had read the LangChain documentation, attended an AutoGen workshop, and even completed an online course on building AI agents. Yet there she was, drowning in callback functions, state machine definitions, and framework-specific abstractions that seemed to multiply with each tutorial she followed.

"I just want to chain three LLM calls together," she told me over coffee, frustration evident in her voice. "Why does this require a hundred lines of Python?"

That question haunted me. Because the answer—*because that's how the frameworks are designed*—wasn't good enough. Not when millions of people on this planet already know a declarative language powerful enough to express complex logic. Not when SQL has been solving orchestration problems for fifty years. Not when the syntax for joining tables, filtering results, and aggregating data could map so naturally to joining prompts, filtering outputs, and aggregating responses.

This book is my answer to her question. And to the thousands of data engineers, SQL analysts, and BI developers who have looked at the AI agent landscape and thought: *there has to be a simpler way.*

---

## There Is.

SPL (Structured Prompt Language) is a declarative workflow language that treats LLM orchestration the way SQL treats data: as something to be queried, filtered, transformed, and composed—without specifying the how. You write what you want. The runtime handles the rest.

If you can write this:

```sql
SELECT name, SUM(revenue)
FROM sales
WHERE region = 'APAC'
GROUP BY name
```

Then, with this book, you will learn to write this:

```spl
PROMPT answer: """
Summarize the key findings from this document.
Return exactly 3 bullet points.
"""
USING doc = $input
WITH MODEL "gemma3"
ADAPTER ollama;
```

And then this:

```spl
WORKFLOW research_agent(input: text) -> report: text
BEGIN
  GENERATE plan FROM input USING planner;
  WHILE NOT satisfied DO
    GENERATE step_result FROM plan USING executor;
    EVALUATE satisfied FROM step_result USING checker;
  END WHILE;
  GENERATE report FROM step_result USING synthesizer;
END;
```

The first example is a prompt. The second is a multi-step agentic workflow with a feedback loop—implemented in eleven lines of declarative syntax. No Python classes. No state machine definitions. No callback functions. Just logic, expressed clearly and executed reliably.

---

## For the Global South

This book is dedicated to the engineers, researchers, and students of the Global South—who have every bit as much right to participate in the AI revolution as their counterparts in San Francisco, London, or Shanghai, yet face barriers their peers never encounter.

When we benchmarked every recipe in this book, we did not use H100s or A100s. We used a GTX 1080 Ti—a graphics card you can buy on eBay for under $200, or find in a gaming PC that's already gathering dust in a closet. Every latency figure, every reproducibility claim, every "this works" guarantee comes from that hardware. Not because we couldn't access better equipment. Because we chose not to.

Because accessibility is not an afterthought. It is a design principle.

Because a student in Nairobi with a used GPU should have the same learning materials as a researcher in Mountain View with a cloud budget.

Because the future of AI belongs to everyone, or it belongs to no one.

If you are reading this book from a university in Jakarta, a startup in Lagos, a government office in São Paulo, or a home in any of the hundred countries where GPU clouds are expensive, slow, or unavailable: this book was written for you. The code in these pages will run on your hardware. The patterns will work within your constraints. And the knowledge will be yours to keep, share, and build upon.

---

## What This Book Is Not

This is not a book about machine learning theory. We will not discuss transformer architectures, attention mechanisms, or the mathematics of backpropagation. If you want that, there are excellent textbooks and courses available—and I encourage you to explore them.

This is not a book about prompt engineering as a creative art. We will not spend pages on "magic phrases" or prompt archaeology. The prompts in this book are functional: designed to be clear, reliable, and reproducible, not clever or surprising.

This is not a book that teaches Python. If you want to use SPL programmatically, the `spl-llm` package provides a Python API—but that's documentation, not this book. Here, we focus on the `.spl` file itself: the declarative artifact that expresses your workflow logic independently of any host language.

And crucially, this is not a book that claims SPL is the only way to build AI workflows. LangGraph, AutoGen, CrewAI, and other frameworks have their place, their communities, and their strengths. If you are a Python developer building production systems with complex state requirements, those frameworks may serve you well. This book is for everyone else—for the SQL millions who have been left out of the agentic AI conversation because they don't speak Python fluently enough to translate their ideas into imperative code.

---

## How This Book Works

Every chapter in this book follows the same structure. You can open to any recipe and start there, or read sequentially from beginning to end. Each recipe includes:

- **The Pattern**: What problem does this solve? Why would you need it?
- **The SPL Approach**: How does SPL make this natural to express?
- **The `.spl` File (Annotated)**: Full source code with line-by-line explanations
- **Running It**: Exact commands and expected output
- **What Just Happened**: An execution trace showing what the runtime did
- **Reproducibility Note**: Latency, variability, and hardware requirements
- **When to Use This Pattern**: Concrete use cases and alternatives
- **Exercises**: Modifications to try on your own

This structure is intentional. It respects your time. It supports both linear reading and random access. And it ensures that every recipe is complete—no "left as an exercise for the reader" gaps, no dependencies on external repositories that may disappear, no hand-waving over the hard parts.

---

## A Note on Reproducibility

Every recipe in this book was tested. Not once, but multiple times, across different runs, to verify that the output is consistent and the latency is predictable. We report the coefficient of variation (CV%) for latency-sensitive recipes, so you know which patterns are stable and which depend on LLM judgment calls.

The reference hardware for all benchmarks:
- **GPU**: NVIDIA GTX 1080 Ti (11 GB VRAM)
- **CPU**: AMD Ryzen 7 3700X
- **RAM**: 32 GB DDR4
- **OS**: Ubuntu 22.04 LTS
- **Primary Model**: Gemma 3 (via Ollama)

Why Gemma 3? Because it fits on a 1080 Ti with room for context. Because it's open-weights. Because it represents what's achievable on commodity hardware today—not what requires enterprise infrastructure.

If you have better hardware, these recipes will run faster. If you have worse hardware, you may need to use smaller models or shorter contexts. But the patterns themselves are hardware-agnostic. The logic is what matters.

---

## Acknowledgments

This book would not exist without the SPL community—the early adopters who tested recipes, reported bugs, and suggested improvements when `spl-llm` was barely functional. Your patience and feedback made both the language and this book better.

I am grateful to [Foreword Author TBD] for lending their voice to this project, and to the researchers whose work on declarative languages, workflow orchestration, and prompt programming laid the intellectual foundation for SPL.

Special thanks to my colleague—the data engineer who asked the question that started this journey. You know who you are. This book is my answer, three years in the making.

And finally, to the readers in the Global South and beyond who pick up this book hoping to build something meaningful: may these recipes serve you well. May your hardware be sufficient, your latencies low, and your workflows reliable. May you build systems that help your communities, advance your careers, and contribute to a more equitable AI future.

---

*"Every atom in a crystal is equally fundamental. Every recipe in this book is equally real—no toy examples, no omitted edge cases, no hardware you can't buy on eBay."*

— Wen
March 2026
