# Socratic Tutor

*"The highest form of teaching is not giving answers, but asking the right questions."*

---

## The Pattern

Most AI tutors act like talking encyclopedias. You ask "Why is the sky blue?" and they give you a three-paragraph lecture on Rayleigh scattering. This is efficient for information retrieval, but it is terrible for *learning*. Learning happens when a student is forced to think, reason, and arrive at a conclusion themselves.

The **Socratic Tutor** pattern implements the oldest pedagogical technique in history. Instead of explaining, the AI acts as a guide. It asks a question, listens to the student's response, identifies a gap in their logic, and then asks a *better* question to help them close that gap.

The SQL analogy is an **Iterative Refinement Query**. You are querying a "Student Mind" (the user) and using the results to filter and focus your next "Query" (the question), repeating until the "Result Set" (the student's understanding) meets your quality threshold.

The Socratic Tutor recipe (Recipe 32) simulates this dialogue. It doesn't just ask questions; it **simulates** a student's responses to test its own effectiveness, scores the student's emerging understanding, and adapts its questioning strategy in real-time.

---

## The SPL Approach

This recipe demonstrates **Persona-Driven Branching**—using a strict system role to constrain the model's behavior while using an `EVALUATE` block to change the pedagogical strategy.

---

## The .spl File (Annotated)

```spl
-- Recipe 32: Socratic Tutor
-- Ask guiding questions rather than giving answers directly.

CREATE FUNCTION socratic_persona(student_level TEXT)
RETURNS TEXT AS $$
You are a Socratic tutor. 
Core rules:
1. Ask exactly ONE clear question at a time.
2. NEVER state facts or give direct answers.
3. Build on what the student just said.
Student level: {student_level}
$$;

WORKFLOW socratic_tutor
    INPUT: @topic TEXT, @student_level TEXT DEFAULT 'high school'
DO
    -- Phase 1: Initiation
    GENERATE opening_question(@topic, socratic_persona(@student_level)) INTO @q1

    -- Phase 2: Dialogue Simulation (Testing the logic)
    GENERATE simulate_student(@q1, @student_level) INTO @s1 -- (1) The "Dummy Student"
    GENERATE followup_question(@q1, @s1) INTO @q2
    GENERATE simulate_student(@q2, @student_level) INTO @s2

    -- Phase 3: Assessment
    GENERATE assess_understanding(@s1, @s2) INTO @score    -- (2) Measuring Learning

    -- Phase 4: Adaptive Branching
    EVALUATE @score
        WHEN > 7 THEN                                     -- (3) High Understanding
            GENERATE consolidation_question(@s2) INTO @q3
        OTHERWISE                                         -- (4) Low Understanding
            GENERATE hint_question(@q2, @s2) INTO @q3
    END

    -- Phase 5: Final Performance
    GENERATE simulate_student(@q3) INTO @s3
    COMMIT compile_dialogue(@q1, @s1, @q2, @s2, @q3, @s3) WITH status = 'complete'
END
```

### (1) The "Dummy Student" (`simulate_student`)

To build a truly effective tutor, we don't just write prompts; we test them. In this workflow, we use one model instance to act as the Tutor and another to act as a "Simulated Student" at a specific level (e.g., middle school). 
- **Why?** This allows us to "dry-run" the educational path. If the tutor is too confusing for the simulated student, it will likely be too confusing for a real human.

### (2) Measuring Learning (`assess_understanding`)

We use a "Judge" prompt to look at the student's two previous answers.
- "Are they getting closer to the truth?"
- "Are they identifying the right variables?"
This step turns the "Vibe" of a conversation into a hard numeric score.

### (3) & (4) Adaptive Branching

This is where the pedagogy lives. 
- If the student is succeeding (**Score > 7**), the tutor asks a "Consolidation" question to cement the knowledge.
- If the student is struggling (**Otherwise**), the tutor pivots to a "Hint" question to simplify the concept.

SQL Analogy: **Conditional Routing**. You are routing the "Transaction" (the lesson) through different logic paths based on the "Data" (the student's performance).

---

## Running It

Test the tutor on a scientific concept:

```bash
spl run cookbook/32_socratic_tutor/socratic_tutor.spl \
    --adapter ollama --tools cookbook/32_socratic_tutor/tools.py \
    topic="Why do objects fall at the same speed?" student_level="middle school"
```

Expected output: A three-turn dialogue where the AI guides the student from "gravity pulls everything" toward the more nuanced understanding of mass and acceleration.

---

## What Just Happened

**LLM calls: 7.** (3 questions + 3 simulated responses + 1 assessment)

The "Conductor" (SPL Runtime) managed a "Pedagogical Loop":
1.  **Established** a strict role-play boundary.
2.  **Facilitated** a multi-turn reasoning chain.
3.  **Monitored** the quality of the student's progress.
4.  **Modified** the difficulty level dynamically.
5.  **Verified** the final outcome.

---

## Reproducibility Note

The Socratic Tutor is highly dependent on the **Persona Guardrails**. If the model "breaks character" and gives the answer, the learning value is lost. Larger models like **gemma3** are much better at maintaining this discipline than smaller models.

On a **GTX 1080 Ti**, a 3-turn simulation takes **30–50 seconds**. This is a powerful way to generate "Synthetic Training Data" for educational apps or to test different teaching strategies.

---

## When to Use This Pattern

Use the **Socratic Tutor** pattern when:
- **Educational Apps**: Building tools that help students think rather than just cheat.
- **Corporate Training**: Helping employees discover new processes or compliance rules through reasoning.
- **Problem Discovery**: When you have a complex problem and want to "think through it" by having an AI ask you guiding questions.

---

## Exercises

1.  **Add a "Subject" Bias.** Modify the `socratic_persona` to accept a `@subject` parameter (e.g., "Physics," "History") and observe how it uses different analogies.
2.  **Extend the Loop.** Use a `WHILE` loop (Chapter 7.1) to allow the dialogue to continue for up to 10 turns, or until the `@understanding_score` reaches 9.
3.  **Strict Mode.** Add an `EXCEPTION` handler that triggers if the model ever says the phrase "The answer is" and forces a `RETRY` with a stricter safety prompt.
