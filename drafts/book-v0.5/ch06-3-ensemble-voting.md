# Ensemble Voting

<!-- *"The wisdom of the crowd is more reliable than the genius of the individual." — Wen Gong* -->

<!-- --- -->

## The Pattern

In the world of statistics and machine learning, an **Ensemble** is a collection of models that work together to solve a single problem. The core idea is simple: if you ask one person a question, they might be wrong. If you ask five people and take the average of their answers, you are much more likely to be right. This is known as "The Wisdom of the Crowd."

For LLMs, this pattern is incredibly powerful for reducing "hallucinations." A single model might confidently state a fact that is slightly off. But if you generate five independent answers, the correct facts will likely appear in the majority, while the hallucinations will be unique to each run and can be "voted out."

The SQL analogy is a **UNION ALL with a GROUP BY and HAVING COUNT(*) > 1**. You are collecting multiple result sets and then filtering for the "consensus" that appears across most of them.

The Ensemble Voting recipe (section 6.3) generates five independent candidate answers, scores each one for accuracy and clarity, identifies the "Consensus" themes across all five, and finally synthesizes a "Winning" response.

<!-- --- -->

## The SPL Approach

This recipe demonstrates **Multi-Sample Generation** and **Consensus-Driven Synthesis**.

<!-- --- -->

## The .spl File (Annotated)

```spl
-- Recipe 20: Ensemble Voting
-- Generates multiple independent answers, then uses majority voting to pick the best.

WORKFLOW ensemble_voting
    INPUT: @question TEXT
DO
    -- Phase 1: Multi-Sampling (The Crowd)
    GENERATE answer_candidate(@question) INTO @candidate_1 -- (1) Five independent runs
    GENERATE answer_candidate(@question) INTO @candidate_2
    GENERATE answer_candidate(@question) INTO @candidate_3
    GENERATE answer_candidate(@question) INTO @candidate_4
    GENERATE answer_candidate(@question) INTO @candidate_5

    -- Phase 2: Scoring (Individual Quality)
    GENERATE score_candidate(@candidate_1) INTO @score_1 -- (2) Measuring each
    GENERATE score_candidate(@candidate_2) INTO @score_2
    ...

    -- Phase 3: Consensus (Finding the Wisdom)
    GENERATE find_consensus(@candidate_1, @candidate_2, ...) INTO @consensus -- (3) Grouping

    -- Phase 4: Selection and Polishing
    GENERATE select_winner(@scores, @consensus) INTO @best_candidate
    GENERATE polish(@best_candidate, @consensus) INTO @final_answer -- (4) The Final Act

    COMMIT @final_answer WITH status = 'complete', candidates = 5
END
```

### (1) Phase 1: Multi-Sampling

We run the *exact same* prompt five times. In a stateless environment, we rely on the model's inherent "Temperature" (randomness) to produce slightly different phrasings and perspectives in each run.

### (2) Phase 2: Scoring

Before we look for consensus, we score each candidate individually. 
- "Is this answer coherent?" 
- "Does it address all parts of the question?" 
- "Are there obvious factual errors?"

### (3) Phase 3: Finding Consensus

This is the "Voting" step. We pass all five candidates to a "Synthesizer" model and ask it: "What are the common facts and arguments that appear in at least three of these versions?" This identifies the "Grounded Truth" that most of the runs agree on.

### (4) Phase 4: Polishing

Finally, we take the highest-scoring candidate and "polish" it using the consensus themes. If the winner missed a detail that the other four versions caught, we add it back in. The result is a "Super-Answer" that is more robust than any single model could produce.

<!-- --- -->

## Running It

Run the ensemble on a controversial or factual topic:

```bash
spl run cookbook/20_ensemble_voting/ensemble.spl --adapter ollama \
    question="What are the main causes of the Great Depression?"
```

Observe the output. You will notice that the final answer is exceptionally balanced and thorough, as it has been "filtered" through five independent reasoning passes.

<!-- --- -->

## What Just Happened

**LLM calls: 13.** (5 candidates + 5 scores + 1 consensus + 1 winner + 1 polish)

The "Conductor" (SPL Runtime) managed a "Delphi Method" process:
1.  **Surveyed** the crowd (the 5 candidates).
2.  **Audited** each response for quality.
3.  **Extracted** the consensus agreement.
4.  **Selected** the strongest voice.
5.  **Enhanced** that voice with the collective wisdom of the group.

<!-- --- -->

## Reproducibility Note

Ensemble Voting is the "Gold Standard" for stability. 
While a single run might vary by 20–30% in its details, the **Ensemble Result** is remarkably consistent. The "noise" of individual runs is cancelled out, leaving only the "signal" of the underlying model's knowledge.

On a **GTX 1080 Ti**, this recipe takes **2–4 minutes**. It is a heavy workload, but for high-accuracy requirements, it is the most reliable tool in the cookbook.

<!-- --- -->

## When to Use This Pattern

Use the **Ensemble Voting** pattern when:
- **Fact-Critical Queries**: Medical, legal, or historical questions where being "mostly right" is not enough.
- **Reducing Hallucination**: When you suspect the model might "make things up" and want to verify facts across multiple samples.
- **Consensus Building**: When you need a balanced view of a topic with multiple valid perspectives.

<!-- --- -->

## Exercises

1.  **Parallel Execution.** (Required for speed) Use the `WITH` clause (Chapter 9.1) to run all 5 candidates and all 5 scores in parallel blocks.
2.  **Diversity Prompting.** Instead of running the same prompt five times, give each candidate a slightly different "Persona" (e.g., "Answer as an economist," "Answer as a historian," "Answer as a sociologist").
3.  **Weighted Voting.** Modify the `select_winner` step to give more "weight" to candidates that have higher individual scores.
