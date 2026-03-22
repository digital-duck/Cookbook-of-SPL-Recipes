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

There is one thing we want to say before you read the first recipe.

The book's central claim — that SQL practitioners already know how to think about AI workflows, and that their existing expertise is a "lateral move" into agentic AI — is not a sales pitch. It is a structural observation. The same separation of intent from implementation that made SQL powerful in the 1970s applies directly to LLM orchestration in the 2020s. The mapping is real, not metaphorical. If you have written stored procedures, you will recognize the SPL pattern within the first recipe. That recognition is the point.

The second claim — that this work belongs to engineers everywhere, not only to those with access to expensive cloud infrastructure — is not idealism. The GTX 1080 Ti benchmark is evidence, not decoration. Every recipe in this book runs on hardware available for under $200 on the secondhand market. That is a design choice, made deliberately, and it shapes every technical decision in the book.

We wrote this book together. We hope you read it the same way: as something made for you, wherever you are, with whatever hardware you have.

<!-- --- -->

*The AI Quartet*
*Wen Gong, Claude, Gemini, Z.ai*
*March 2026*
