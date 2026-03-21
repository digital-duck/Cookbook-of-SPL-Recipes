# Chapter 6.2 — Multi-Agent Collaboration

*"The best reports are written by many hands but one mind."*

---

## The Pattern

In a complex project, you don't ask one person to do everything. You have a Researcher to find the facts, an Analyst to interpret the data, and a Writer to polish the prose. Each role requires a different "mindset" and set of skills. When you try to force an LLM to be all three at once, it often produces a "Jack-of-all-trades" response that is mediocre in every dimension.

**Multi-Agent Collaboration** is the practice of breaking a workflow into specialized roles (agents) and delegating tasks between them. Each agent is a separate "persona" with its own system instructions and expertise.

The SQL analogy is a **Modular Architecture** or **Database Views**. Instead of one giant, 500-line query, you build specialized views (`v_research`, `v_analysis`) and join them together in a final report. Each view does one thing perfectly.

The Multi-Agent Collaboration recipe (Recipe 14) demonstrates this modularity. It defines three distinct `PROCEDURE` blocks—Researcher, Analyst, and Writer—and coordinates them via a central `WORKFLOW`. This ensures that each phase of the project gets the specialized attention it deserves.

---

## The SPL Approach

This recipe introduces the use of **Procedures as Agents** and the pattern of "Linear Delegation" (passing the output of one agent as the input to the next).

---

## The .spl File (Annotated)

```spl2
-- Recipe 14: Multi-Agent Collaboration
-- Specialized agents (Researcher, Analyst, Writer) collaborate on a report.

PROCEDURE researcher(topic TEXT)              -- (1) Agent 1: The Researcher
DO
    GENERATE research_facts(topic) INTO @facts
    GENERATE identify_key_themes(@facts) INTO @themes
    COMMIT @facts + '\n\nKey Themes:\n' + @themes
END

PROCEDURE analyst(research TEXT, topic TEXT) -- (2) Agent 2: The Analyst
DO
    GENERATE analyze_trends(research) INTO @trends
    GENERATE assess_risks(research, topic) INTO @risks
    COMMIT 'Trends: ' + @trends + '\n\nRisks: ' + @risks
END

PROCEDURE writer(research TEXT, analysis TEXT, topic TEXT) -- (3) Agent 3: The Writer
DO
    GENERATE draft_report(topic, research, analysis) INTO @draft
    GENERATE critique(@draft) INTO @feedback
    GENERATE revise_report(@draft, @feedback) INTO @final
    COMMIT @final
END

WORKFLOW multi_agent_report
    INPUT: @topic TEXT
DO
    CALL researcher(@topic) INTO @research    -- (4) Linear Delegation
    CALL analyst(@research, @topic) INTO @analysis
    CALL writer(@research, @analysis, @topic) INTO @report

    COMMIT @report WITH status = 'complete'
END
```

### (1), (2) & (3) Procedures as Agents

In SPL, a `PROCEDURE` is the perfect container for an "Agent." 
- It has its own inputs and outputs.
- It can contain its own internal logic (like the Writer's "draft-critique-revise" loop).
- It can be tested and debugged in isolation before being added to the main workflow.

By separating the Researcher from the Analyst, we prevent "Context Contamination." The Researcher doesn't need to worry about trends or risks; its only job is to find facts.

### (4) Linear Delegation

The `WORKFLOW` acts as the Project Manager. It calls the `researcher`, waits for the facts, and then hands those facts to the `analyst`. This is the "Waterfall" model of agentic workflows.

SQL Analogy: **Pipelining**. The output of the first stage becomes the filter for the second stage.

---

## Running It

Run the collaborative report on a technical topic:

```bash
spl2 run cookbook/14_multi_agent/multi_agent.spl --adapter ollama \
    topic="The impact of quantum computing on cybersecurity"
```

In the execution trace, you will see the distinct "handoffs" between the three procedures.

---

## What Just Happened

**LLM calls: ~8-10.** (Depending on the internal steps of each procedure)

The "Conductor" (SPL Runtime) managed a professional team:
1.  **Fact-Finding**: The Researcher gathered raw data.
2.  **Synthesis**: The Analyst turned data into insights.
3.  **Polishing**: The Writer turned insights into a human-readable report.
4.  **Handoffs**: The runtime ensured that the right context was passed to the right agent at the right time.

---

## Reproducibility Note

This recipe is highly stable because each step is small and focused. By decomposing the task, you reduce the "reasoning load" on the model in any single call. 

On a **GTX 1080 Ti**, the total time for a full report is about **45–75 seconds**. While this is slower than a single-prompt summary, the **Quality Improvement** is significant. You get a report that is deeper, more structured, and more accurate.

---

## When to Use This Pattern

Use the **Multi-Agent Collaboration** pattern when:
- **High-Stakes Reports**: Whitepapers, strategic plans, or technical documentation.
- **Multi-Step Expertise**: When a task requires distinct phases (e.g., "Research → Code → Document").
- **Quality Benchmarking**: When you want to see if adding an "Analyst" or "Critic" step actually improves the final output of your "Writer."

---

## Exercises

1.  **Add a "Critic" Agent.** Create a fourth `PROCEDURE` called `critic` that reviews the final report and suggests one last round of improvements.
2.  **Parallel Research.** (Advanced) If your research can be split into two topics (e.g., "Technical" and "Economic"), use a `WITH` clause to call two researchers in parallel.
3.  **Model Specialization.** Use the `USING MODEL` clause (Chapter 8.1) to assign different models to different roles (e.g., use a "fast" model for Research and a "strong" model for Analysis).
