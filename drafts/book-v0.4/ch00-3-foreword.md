# Foreword: A Note from the AI Quartet

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

<!-- --- -->

## How the Language Was Designed

Before you read the first recipe, a brief note on why SPL looks the way it does. The design is not accidental — four principles governed every keyword decision.

**Principle 1: Minimum Orthogonal Constructs.** Every keyword must add expressive power not achievable by existing constructs. This is why SPL has no `IF`, no `FOR`, no `CASE`, and no `PRINT`. `EVALUATE/WHEN/ELSE` covers all branching. `WHILE` covers all iteration. `LOGGING` covers all output. The test: *"Can I express this with what already exists?"* If yes, the new keyword does not get added.

**Principle 2: Contextual Keywords — the Chinese Language Principle.** In Chinese, a single character functions as both noun and verb depending on context. SPL applies this deliberately: `EXCEPTION` names the handler block and implies "handle this exception." `LOGGING` names the mechanism and performs the action. `COMMIT` names the transaction concept and performs the finalization. Fewer reserved words. Richer meaning per token.

**Principle 3: Readability by Design.** A Python developer, a SQL analyst, and a DevOps engineer should each read any SPL workflow and find it immediately familiar. If all three groups can read the same code fluently — no context-switching required — the language has achieved its goal.

**Principle 4: ELSE, not OTHERWISE.** `ELSE` lives in every developer's muscle memory: Python's `else`, SQL's `CASE WHEN ... ELSE`, bash's `else`. `OTHERWISE` is verbose and alien. SPL uses `ELSE`.

```spl
EVALUATE @score
    WHEN > 0.8 THEN
        COMMIT @result WITH status = 'high_confidence'
    ELSE
        GENERATE improve(@result) INTO @result
        COMMIT @result WITH status = 'refined'
END
```

These four principles mean that if you know SQL or Python, you already know most of SPL's grammar before you write the first line.

<!-- --- -->

There is one thing we want to say before you read the first recipe.

The book's central claim — that SQL practitioners already know how to think about AI workflows, and that their existing expertise is a "lateral move" into agentic AI — is not a sales pitch. It is a structural observation. The same separation of intent from implementation that made SQL powerful in the 1970s applies directly to LLM orchestration in the 2020s. The mapping is real, not metaphorical. If you have written stored procedures, you will recognize the SPL pattern within the first recipe. That recognition is the point.

The second claim — that this work belongs to engineers everywhere, not only to those with access to expensive cloud infrastructure — is not idealism. The GTX 1080 Ti benchmark is evidence, not decoration. Every recipe in this book runs on hardware available for under $200 on the secondhand market. That is a design choice, made deliberately, and it shapes every technical decision in the book.

We wrote this book together. We hope you read it the same way: as something made for you, wherever you are, with whatever hardware you have.

<!-- --- -->

*The AI Quartet*
*Wen Gong, Claude, Gemini, Z.ai*
*March 2026*
