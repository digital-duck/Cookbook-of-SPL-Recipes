# Hypothesis Tester

<!-- *"The first principle is that you must not fool yourself — and you are the easiest person to fool." — Richard Feynman* -->

<!-- --- -->

## The Pattern

In business and science, we often make quick observations: "Users hate the new UI," or "The server is slow because of the database." These are not facts; they are **Hypotheses**. If you act on a hypothesis without testing it, you waste time and resources. 

**Structured Scientific Reasoning** is the pattern of converting a "vibe" into a falsifiable claim.
1.  **Formulate**: Define the Null Hypothesis (H0: it's chance) and the Alternative Hypothesis (H1: the claim).
2.  **Plan**: Design a test that could prove you wrong (Falsifiability).
3.  **Audit**: Look for confounding variables (other things that could cause the effect).
4.  **Evaluate**: Score the available evidence and draw a conclusion based on a confidence threshold.

The SQL analogy is **Hypothetical Querying** or **Impact Analysis**. You are running a "What-If" scenario against your data, calculating the "Confidence Interval" of your findings, and only committing to a business decision if the results are statistically significant.

The Hypothesis Tester recipe (Recipe 35) implements this rigorous loop. It forces the model to think like a scientist—identifying variables and seeking evidence that *refutes* its own initial guess before reaching a final verdict.

<!-- --- -->

## The SPL Approach

This recipe introduces **Evidence Weighting**—using a structured JSON schema to collect pros and cons and then using a numeric confidence score to drive the workflow's conclusion.

<!-- --- -->

## The .spl File (Annotated)

```sql
-- Recipe 35: Hypothesis Tester
-- Generate hypothesis → design test → evaluate evidence → conclude.

CREATE FUNCTION hypothesis_framework()
RETURNS TEXT AS $$
Format:
- Null hypothesis (H0): The effect does not exist.
- Alternative hypothesis (H1): The proposed claim.
- Falsifiability: How would we prove H1 wrong?
$$;

WORKFLOW hypothesis_tester
    INPUT: @observation TEXT, @threshold FLOAT DEFAULT 0.7
DO
    -- Phase 1: Formulation
    GENERATE formulate_hypotheses(@observation, hypothesis_framework()) INTO @hypo

    -- Phase 2: Experimental Design
    GENERATE design_test(@hypo) INTO @test_plan

    -- Phase 3: Evidence Evaluation
    GENERATE evaluate_evidence(@observation, @hypo, evidence_schema()) INTO @evidence_json

    -- Phase 4: Decision Logic
    GENERATE extract_confidence(@evidence_json) INTO @confidence

    EVALUATE @confidence
        WHEN >= @threshold THEN                               -- (1) Significant Result
            GENERATE write_conclusion(@hypo, @evidence_json, 'confident') INTO @final
            COMMIT @final WITH verdict = 'supported'
        WHEN >= 0.4 THEN                                      -- (2) Inconclusive
            GENERATE write_conclusion(@hypo, @evidence_json, 'uncertain') INTO @final
            COMMIT @final WITH verdict = 'needs_more_data'
        OTHERWISE                                             -- (3) Refuted
            GENERATE write_conclusion(@hypo, @evidence_json, 'refuted') INTO @final
            COMMIT @final WITH verdict = 'rejected'
    END
END
```

### (1), (2) & (3) The Confidence Ladder

This is the most "Honest" pattern in the cookbook. Instead of always giving an answer, the workflow can admit ignorance. 
- If the evidence is strong (**@confidence >= 0.7**), it commits a confident conclusion.
- If the evidence is mixed (**@confidence >= 0.4**), it tells the user "We need more data."
- If the evidence is weak, it concludes that the observation was likely a fluke.

SQL Analogy: **Threshold Filtering**. You are filtering your "Insights" by a quality metric, ensuring that only high-confidence conclusions are promoted to the final report.

<!-- --- -->

## Running It

Test a common business observation:

```bash
spl run cookbook/35_hypothesis_tester/hypothesis.spl \
    --adapter ollama -m gemma3 \
    observation="Remote teams show lower productivity in the first month after joining"
```

Expected output: A structured breakdown of the variables (e.g., "Time-to-onboard" vs "Work location"), a list of evidence for and against the claim, and a final verdict based on the calculated confidence.

<!-- --- -->

## What Just Happened

**LLM calls: 5.** (Formulate, Design, Evaluate, Extract, Conclude)

The "Conductor" (SPL Runtime) managed a "Peer Review Board":
1.  **Drafted** a formal scientific claim.
2.  **Designed** an experiment to test that claim.
3.  **Audited** the claim against existing evidence.
4.  **Measured** the strength of the findings.
5.  **Rendered** a conservative, evidence-based judgment.

<!-- --- -->

## Reproducibility Note

Hypothesis Testing is a "Deep Reasoning" task. Small models often fall into "Confirmation Bias"—they only look for evidence that supports the observation. For this recipe, we strongly recommend using a "Senior" reasoning model like **gemma3 (27B)** or **Llama 3.1 (70B)** to ensure the adversarial thinking is genuine.

On a **GTX 1080 Ti**, this full reasoning chain takes **40–60 seconds**.

<!-- --- -->

## When to Use This Pattern

Use the **Hypothesis Tester** pattern when:
- **Strategic Planning**: Testing "Gut Feelings" before making a pivot.
- **Root Cause Analysis**: Investigating why a system failed or why a metric dropped.
- **Academic/Scientific Research**: Automating the first pass of literature review and hypothesis formulation.

<!-- --- -->

## Exercises

1.  **Add "Confounding Variables".** Add a specific step between Phase 1 and 2 that asks the model to "List three other things that could explain this observation besides H1."
2.  **Multi-Model Review.** Use a different model for the `evaluate_evidence` step to provide a "blind" second opinion.
3.  **Custom Threshold.** Run the recipe with `@threshold = 0.9` and observe how much harder it is for the model to reach a "Confident" conclusion.
