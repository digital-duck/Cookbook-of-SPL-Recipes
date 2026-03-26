# Tree of Thought

<!-- *"A single path is a tunnel; multiple paths are a map." — Wen Gong* -->

<!-- --- -->

## The Pattern

When humans solve a truly hard problem, we don't just pick one idea and run with it. We brainstorm. We explore three or four different approaches, follow each one a few steps down the road, see which one runs into a dead end, and then double down on the most promising path. This is the **Tree of Thought (ToT)** pattern.

The problem with standard LLM prompting is that it is "linear." The model commits to a direction with its very first token and is then forced to stay on that path, even if it realizes halfway through that it was a mistake.

The SQL analogy is a **Recursive CTE with Branching** or a **Multi-Path Union**. You are generating multiple potential "result sets" (thought paths) in parallel and then using a filter (an evaluation step) to pick the best one.

The Tree of Thought recipe (section 3.2) implements this "Branch and Prune" strategy. It explores three independent approaches to a problem, develops each one into a more detailed plan, scores them, and then selects the winner for final refinement.

<!-- --- -->

## The SPL Approach

This recipe demonstrates **Parallel Exploration**—generating multiple independent states and then synthesizing them into a single conclusion.

<!-- --- -->

## The .spl File (Annotated)

```spl
-- Recipe 17: Tree of Thought
-- Explores multiple reasoning paths in parallel, then selects the best.

WORKFLOW tree_of_thought
    INPUT: @problem TEXT
DO
    -- Phase 1: Branching (The Brainstorm)
    GENERATE approach_1(@problem) INTO @path_a -- (1) Three independent seeds
    GENERATE approach_2(@problem) INTO @path_b
    GENERATE approach_3(@problem) INTO @path_c

    -- Phase 2: Developing (Following the map)
    GENERATE develop(@path_a, @problem) INTO @path_a_dev -- (2) Elaborating each
    GENERATE develop(@path_b, @problem) INTO @path_b_dev
    GENERATE develop(@path_c, @problem) INTO @path_c_dev

    -- Phase 3: Scoring (The Pruning)
    GENERATE evaluate_path(@path_a_dev) INTO @score_a -- (3) Objective evaluation
    GENERATE evaluate_path(@path_b_dev) INTO @score_b
    GENERATE evaluate_path(@path_c_dev) INTO @score_c

    -- Phase 4: Selection and Refinement
    GENERATE select_best(@path_a_dev, @score_a, ...) INTO @best_path
    GENERATE refine_solution(@best_path) INTO @best_solution

    -- Phase 5: Final Verification
    GENERATE verify(@best_solution) INTO @verification
    EVALUATE @verification                     -- (4) The Final Check
        WHEN 'sound' THEN
            COMMIT @best_solution WITH status = 'complete'
        OTHERWISE
            GENERATE synthesize_all(...) INTO @best_solution
            COMMIT @best_solution WITH status = 'synthesized'
    END
END
```

### (1) Phase 1: Branching

We ask the model to generate three distinct approaches to the same problem. For example, if the problem is "How to scale a database," Path A might be "Horizontal Sharding," Path B might be "Read Replicas," and Path C might be "Caching Layer."

### (2) Phase 2: Developing

We take each seed and ask the model to "develop" it further—writing out the pros, cons, and implementation steps for each specific approach. This is where the "tree" grows its branches.

### (3) Phase 3: Scoring

We use a "Judge" prompt to score each developed path on a set of criteria (e.g., feasibility, cost, scalability). This is the "Pruning" step. We are identifying which branches are worth keeping and which are dead ends.

### (4) The Final Check

Even after we've picked a "winner" and refined it, we perform one last verification. If the final solution is still not "sound," we fall back to a **Synthesis** step—taking the best ideas from *all three* paths and merging them. This ensures we don't lose the "good parts" of the losing paths.

<!-- --- -->

## Running It

Run the Tree of Thought on a strategic decision:

```bash
spl run cookbook/17_tree_of_thought/tree_of_thought.spl --adapter ollama \
    problem="Should we rewrite our legacy monolith in Rust or Go?"
```

In the output, you will see the model exploring both languages (and perhaps a third option like "Refactor in place"), scoring them based on performance and developer velocity, and then providing a nuanced recommendation.

<!-- --- -->

## What Just Happened

**LLM calls: 12-14.**

The "Conductor" (SPL Runtime) managed a "Tournament of Ideas":
1.  **Fanned out** the initial brainstorming.
2.  **Expanded** each idea into a concrete plan.
3.  **Measured** each plan against a set of standards.
4.  **Selected** the strongest candidate.
5.  **Refined** the candidate into a production-ready solution.
6.  **Verified** the result, with a fallback for complex failures.

<!-- --- -->

## Reproducibility Note

Tree of Thought is the most computationally expensive reasoning pattern. 
On a **GTX 1080 Ti**, a full 12-call ToT can take **2–4 minutes**. 

However, the **Robustness** is unparalleled. By exploring multiple paths, you significantly reduce the risk of the model "hallucinating" a single bad solution and sticking to it. This pattern is designed for high-stakes decision-making where the cost of a wrong answer is much higher than the cost of the extra tokens.

<!-- --- -->

## When to Use This Pattern

Use the **Tree of Thought** pattern when:
- **Strategic Decisions**: Architectural choices, business strategies, or complex product trade-offs.
- **Creative Brainstorming**: When you need a wide variety of high-quality ideas rather than just one.
- **Problem Solving with High Uncertainty**: When the "right" answer is not obvious and needs to be discovered through exploration.

<!-- --- -->

## Exercises

1.  **Parallelize the Branches.** Use the `WITH` clause (Chapter 9.1) to run Phase 1, 2, and 3 in parallel blocks. This will reduce the latency by nearly 60% if your hardware can handle it.
2.  **Add a "Devil's Advocate."** In Phase 2, instead of just "developing" the path, ask the model to specifically "Find the three biggest reasons why this approach will fail."
3.  **Variable Branching.** Modify the input to accept `@branch_count` and use a `WHILE` loop (Chapter 7.1) to generate an arbitrary number of paths instead of exactly three.
