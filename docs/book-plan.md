# A Cookbook of SPL Recipes — Book Plan

*Strategic planning document. Updated: March 2026.*

---

## Current Status

- **Version**: v0.2 (in active revision)
- **Chapters**: 48 (including 4 new in v0.2, appendix, cheatsheet)
- **Recipes**: 37 validated + 3 new (ch04-4, ch05-3, ch08-4)
- **PDF**: Compiles clean, 808 KB
- **Overall assessment** (Opus 4.6 review): STRONG FOUNDATION — Revise and Resubmit

---

## Remaining Editorial Work (v0.2 → v0.3)

### High Priority
- [ ] **Line-edit introductory and transitional prose** — target AI-voice patterns: redundant restatements, dramatic one-liners, manifesto repetition. Rule: if a sentence restates what the previous sentence established, cut it. Focus on ch00-0, ch00-1, and all Part intro chapters.
- [ ] **Professional book design** — title page, chapter openers, cover. The content deserves a container that matches its quality. Needs a designer; budget ~$500–1,500 for freelance cover + interior template.
- [ ] **Syntax highlighting for code** — replace plain monospace listings with color-highlighted SPL keywords. Requires custom `listings` language definition or switch to `minted` package with xelatex.

### Medium Priority
- [ ] **Three parser fixes** (SPL runtime, tracked in README-ROADMAP.md):
  - Recipe 13 (Map-Reduce): `EVALUATE @score WHEN > 0.7` — numeric comparison in EVALUATE
  - Recipe 14 (Multi-Agent): `@result :=` inside PROCEDURE body
  - Recipe 19 (Memory Chat): `SELECT memory.get('key') INTO @var` inside WORKFLOW
- [ ] **Index** — keyword index (SPL keywords, pattern names, tool names). LaTeX `makeindex` makes this straightforward once content stabilizes.
- [ ] **Validate new recipes** — run ch04-4, ch05-3, ch08-4 through `run_all.py` once tool stubs are in place.

### Low Priority
- [ ] **ch03-1 (Chain of Thought)** — missing epigraph (only chapter without one; intentional or oversight?)
- [ ] **Adapter portability proof** (ch08-4) — results table currently contains estimated data; replace with actual benchmark runs across all four adapters.

---

## Foreword: Pitch Candidates

A foreword from a recognized voice in AI, data, or open-source would significantly increase the book's credibility and reach. Ranked by fit:

### Tier 1 — Strongest fit

**1. Andrew Ng** (DeepLearning.AI, Coursera AI courses, Landing AI)
- Champion of AI democratization and Global South access
- Has written/endorsed books on making AI accessible to non-experts
- The "AI as a public utility" message resonates directly with his public mission
- Connection angle: DeepLearning.AI courses teach Python-first; SPL is the SQL-first alternative
- Pitch: frame SPL as expanding the AI practitioner population beyond Python developers

**2. Hannes Mühleisen** (DuckDB founder/CEO)
- DuckDB is the canonical success story of "SQL for a new generation of data problems"
- Declarative-first, embedded, runs anywhere — directly parallel to SPL's design philosophy
- SQL community credibility; his endorsement signals "declarative is the right approach"
- Pitch: "you proved that SQL is the right abstraction for analytics; SPL applies the same insight to AI orchestration"

### Tier 2 — Strong fit

**3. Matei Zaharia** (Databricks co-founder/CTO, Apache Spark creator)
- Created the dominant declarative abstraction for distributed data processing
- Databricks is deeply invested in LLM orchestration (MLflow, LLMOps)
- Enterprise credibility; his endorsement opens enterprise decision-maker doors
- Pitch: declarative abstractions win in the long run — Spark proved it for data, SPL applies it to AI workflows

**4. Simon Willison** (Datasette, sqlite-utils, LLM CLI tool)
- Vocal advocate for open-source AI tools that run locally
- Writes extensively about making LLMs accessible to non-ML-engineers
- Large following among data journalists, analysts, and pragmatic developers
- Pitch: SPL is what his audience has been waiting for — LLM orchestration without Python

### Tier 3 — Consider

**5. Chip Huyen** (author of "Designing Machine Learning Systems", Stanford)
- ML systems practitioner with strong following among applied ML engineers
- Covers production deployment, cost, and accessibility in her work
- Pitch: production-grade AI orchestration for the 99% of teams that aren't Big Tech

**How to reach them:**
- Andrew Ng: LinkedIn, or through DeepLearning.AI content submissions
- Hannes Mühleisen: DuckDB community, GitHub, or direct email (publicly available)
- Matei Zaharia: academic/conference circuit, Databricks blog
- Simon Willison: very accessible via his blog comments and Mastodon

---

## Publisher Strategy

### Recommendation: Leanpub first, then O'Reilly or Manning

**Phase 1 — Leanpub (now)**
- Publish v0.2 on Leanpub immediately as "early access" (in-progress book)
- Readers pay now and get all future updates; generates revenue and reader feedback during revision
- Keep 80% royalty vs. ~10–15% with traditional publisher
- Iterative: push updates as you revise; readers see each version
- URL: leanpub.com — very simple Markdown-to-PDF pipeline (compatible with our existing toolchain)
- Price suggestion: $19.99 early access → $34.99 final

**Phase 2 — O'Reilly or Manning (v1.0)**
- O'Reilly: most prestigious for technical books; animal cover signals quality; wide library distribution
  - Downside: slow (12–18 months from contract to shelf), low royalties (~10%), less control
  - Best path: submit a proposal with the Leanpub sales data as evidence of market demand
- Manning: strong developer audience, MEAP (Manning Early Access Program) similar to Leanpub model
  - Better royalties than O'Reilly (~12–15%), faster turnaround
  - Good fit for a cookbook-format technical book

**Phase 3 — Amazon KDP (print-on-demand)**
- Run alongside Leanpub for print distribution globally
- Critical for Global South where ebook platforms have payment friction
- Print-on-demand means no inventory risk
- Price print edition at cost + small margin to maximize accessibility

**Self-publish vs. traditional:**
- Self-publish (Leanpub + KDP) if: speed, control, and revenue per copy matter more than prestige
- Traditional if: distribution, marketing support, and the O'Reilly/Manning brand matter for your audience
- Recommendation: **start self-published, use the sales data to negotiate from strength with a traditional publisher**

---

## Chinese Edition Plan

### Why the Chinese market matters
- China is the largest developer market outside the US
- Z.ai (ZhiPu) is already an AI Quartet collaborator — natural bridge to Chinese tech community
- Qwen, Baidu ERNIE, DeepSeek are the local models; SPL's adapter abstraction makes it easy to add `--adapter qwen` etc.
- The Global South framing resonates: Chinese developers outside Tier 1 cities face similar infrastructure constraints

### Translation approach
**Option A: Work with Z.ai (ZhiPu) as co-publisher/distributor**
- Z.ai already knows the book; they contributed to it
- Could co-brand the Chinese edition as a ZhiPu × Wen Gong collaboration
- ZhiPu has distribution channels in Chinese developer community

**Option B: Chinese technical publisher**
- 机械工业出版社 (China Machine Press / CMPBOOK) — publishes most O'Reilly translations in China; largest tech book publisher
- 人民邮电出版社 (Posts and Telecom Press / PTPRESS) — publishes Manning translations; strong developer audience
- Process: approach after English v1.0 is published; they typically approach successful English titles

**Option C: Self-publish on Chinese platforms**
- 京东 (JD.com) and 当当 (Dangdang) accept self-published titles
- Lower barrier, lower distribution
- Good for early access / pilot

### Localization priorities for Chinese edition
- Add `--adapter qwen` and `--adapter baidu-ernie` examples in relevant recipes
- Replace Ollama-only benchmarks with local Chinese model benchmarks (Qwen-7B, DeepSeek)
- Add a recipe using a Chinese LLM for a Chinese-language task (e.g., Mandarin customer support triage)
- Z.ai review pass for cultural/technical accuracy

---

## Global South Distribution Strategy

### Target communities
- **India**: large SQL practitioner base; cost-sensitive; English-proficient; focus on Oracle/MySQL practitioners
- **Brazil**: Portuguese edition long-term; active tech community; São Paulo startup scene
- **Nigeria/Ghana**: growing developer community; English-proficient; infrastructure constraints are real
- **Indonesia/Vietnam**: Southeast Asia developer community; local model providers emerging

### Pricing strategy
- **Purchasing Power Parity (PPP) pricing** on Leanpub — Leanpub supports this natively
- Set minimum price at PPP-adjusted rate for each country; readers in Lagos or Jakarta can access at local purchasing power
- Print edition via Amazon KDP at cost price for Global South markets

### Community outreach
- Developer communities: GitHub, local Slack/Discord groups, university mailing lists
- Academic: submit to arXiv (paper already exists); target universities with CS/data programs
- Momagrid node operators: first adopters in Global South; give them complimentary copies

---

## Timeline Suggestion

| Milestone | Target | Notes |
|-----------|--------|-------|
| v0.2 complete (editorial) | April 2026 | Line-editing, design, parser fixes |
| Leanpub early access launch | April 2026 | With v0.2; start collecting reader feedback |
| Foreword pitch to Andrew Ng / Hannes Mühleisen | April 2026 | Need v0.2 PDF as pitch artifact |
| v1.0 (complete, designed) | July 2026 | After reader feedback incorporated |
| O'Reilly / Manning proposal submission | July 2026 | With Leanpub sales data |
| Chinese edition negotiation | September 2026 | After English v1.0 |
| Print edition (KDP) | August 2026 | Simultaneous with or just after v1.0 |

---

## The Team

The project is growing beyond a solo effort. Current and prospective team members:

| Person | Background | Role / Contribution |
|--------|-----------|---------------------|
| **Wen Gong** | Physicist (USTC, nuclear physics PhD), CERN, Lawrence Berkeley Lab; Oracle, Vanguard | Architect, language designer, author — vision and lived experience |
| **Dr. Jun Hu** | Physicist | First confirmed team member; academic depth and credibility |
| **Dr. Ye Sun** | Physicist; Yahoo (briefly); Salesforce.com | Prospective team member; enterprise engineering depth (Salesforce = CRM/workflow automation domain); bridge to enterprise adoption story |
| *(Siebel/Oracle/Salesforce connection)* | Former coworker of Wen at Siebel and Oracle; now at Salesforce | Prospective team member; saw SPL demo and expressed strong interest; enterprise credibility |

**Notable pattern:** Three physicists who moved into IT/enterprise software. This is a marketing angle worth using — physicists bring declarative thinking (Hamiltonian formalism, variational principles) to software architecture. The SPL design philosophy is literally physics-inspired: declare the observables (what you want), let the system resolve the dynamics (how to get it).

**Salesforce connection value:** Salesforce is the dominant enterprise CRM/workflow platform. Salesforce engineers understand the pain of imperative automation (Flows, Apex) and the governance demands of enterprise deployments. A team member from that world gives SPL instant credibility with enterprise decision-makers.

**Next steps for team:**
- Confirm Dr. Ye Sun's participation
- Define contribution roles (code, recipes, outreach, Chinese edition?)
- Add all confirmed members to book Acknowledgments in v1.0
- Consider co-authorship credit for v1.0 if contribution is substantial

---

## Notes on the AI Quartet Collaboration for Marketing

The four-author collaborative story is itself a marketing asset:
- First technical book co-authored by human + 3 AI assistants from different organizations (Anthropic, Google, ZhiPu)
- The collaboration is a proof-of-concept for the book's thesis
- Press angle: "physicist from rural Anhui, working with three AI assistants, built a language to democratize AI"
- Conference talk potential: PyCon, Data Council, re:Invent, VLDB (declarative query languages track)
